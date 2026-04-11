"""
OMG 付款通知 Discord Bot（非官方模板）
============================================

功能：
    /bind <token>       把當前 channel 綁定到商家（需要 admin token）
    /unbind             解除綁定
    /today              今日訂單數與營業額
    /orders             最近 20 筆訂單（含按鈕選單）
    /order <no>         查某筆訂單明細
    /refund             進入退款流程（二次確認）
    /health             呼叫後端 health-summary 查看系統狀態
    /help               顯示所有指令

推播：
    後端 webhook 收到付款成功 / 失敗 / 退款時，呼叫 POST http://localhost:9877/notify
    bot 會把該訊息以 Discord Embed 推到所有 bind 過的 channel

硬規則（務必遵守）：
    1. API 與 menu 一致性：新增 admin endpoint 時，必須同步新增對應 slash command
    2. 退款採警示不阻擋原則：超過 REFUND_* 上限時僅警示，不拒絕執行
    3. Bot token 一律走環境變數，不得寫入 repo

執行方式：
    pip install discord.py httpx python-dotenv fastapi uvicorn
    cp .env.example .env  # 填入 DISCORD_BOT_TOKEN、BACKEND_URL、ADMIN_TOKEN
    python bot.py

非官方聲明：
    本模板為社群維護，與歐買尬（OMG）無任何合作關係。官方資源請參考
    https://github.com/omgtwhub/ 與歐買尬商家後台。
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import discord
import httpx
from discord import app_commands, ui
from fastapi import FastAPI, HTTPException, Request
import uvicorn

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("omg-discord-bot")

# ---------- Config ----------

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_APP_ID = os.getenv("DISCORD_APP_ID", "")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID", "")  # 填入後 slash command 會即時同步
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8787").rstrip("/")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "CHANGEME")
NOTIFY_PORT = int(os.getenv("NOTIFY_PORT", "9877"))

# 退款警示閾值（不阻擋執行）
REFUND_MAX_PER_ORDER = int(os.getenv("REFUND_MAX_PER_ORDER", "50000"))
REFUND_DAILY_QUOTA = int(os.getenv("REFUND_DAILY_QUOTA", "100000"))
REFUND_DAILY_COUNT_CAP = int(os.getenv("REFUND_DAILY_COUNT_CAP", "20"))

# Embed 顏色（與 guides/09-discord-bot.md 一致）
COLOR_PAID = 0x22C55E        # 綠：付款成功
COLOR_REFUND = 0x3B82F6      # 藍：退款
COLOR_WEBHOOK_FAIL = 0xF97316  # 橘：webhook 失敗
COLOR_HEALTH_ALERT = 0xEF4444  # 紅：健康警示
COLOR_NEUTRAL = 0x64748B     # 灰：一般資訊

# 綁定狀態（正式環境建議改用資料庫或 Redis）
BIND_FILE = Path("./.bind_state_discord.json")
NOTIFY_SUBSCRIBERS: set[int] = set()

def _load_binds() -> None:
    global NOTIFY_SUBSCRIBERS
    if BIND_FILE.exists():
        data = json.loads(BIND_FILE.read_text(encoding="utf-8"))
        NOTIFY_SUBSCRIBERS = set(data.get("channel_ids", []))

def _save_binds() -> None:
    BIND_FILE.write_text(
        json.dumps({"channel_ids": list(NOTIFY_SUBSCRIBERS)}),
        encoding="utf-8",
    )

# 每日退款統計（記憶體內，重啟後重置；正式環境應改用 DB）
REFUND_LEDGER: dict[str, dict[str, int]] = {}

def _today_key() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _refund_warnings(amount: int) -> list[str]:
    """檢查退款是否超過建議閾值，回傳警示訊息清單。

    不阻擋退款執行。退款屬於正常業務行為，閾值的作用是讓操作者在超過
    常態金額時暫停思考，而非阻止合法退款。
    """
    warnings: list[str] = []
    ledger = REFUND_LEDGER.setdefault(_today_key(), {"amount": 0, "count": 0})

    if amount > REFUND_MAX_PER_ORDER:
        warnings.append(
            f"本次退款 NTD {amount:,} 超過建議單筆上限 NTD {REFUND_MAX_PER_ORDER:,}。"
        )
    if ledger["amount"] + amount > REFUND_DAILY_QUOTA:
        warnings.append(
            f"執行後今日退款總額將達 NTD {ledger['amount'] + amount:,}，"
            f"超過建議每日上限 NTD {REFUND_DAILY_QUOTA:,}。"
        )
    if ledger["count"] + 1 > REFUND_DAILY_COUNT_CAP:
        warnings.append(
            f"執行後今日退款次數將達 {ledger['count'] + 1} 次，"
            f"超過建議每日上限 {REFUND_DAILY_COUNT_CAP} 次。"
        )
    return warnings

def _consume_refund_quota(amount: int) -> None:
    ledger = REFUND_LEDGER.setdefault(_today_key(), {"amount": 0, "count": 0})
    ledger["amount"] += amount
    ledger["count"] += 1

# ---------- Backend API client ----------

async def backend_get(path: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.get(f"{BACKEND_URL}{path}", headers={"X-Admin-Token": ADMIN_TOKEN})
        r.raise_for_status()
        return r.json()

async def backend_post(path: str, body: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=15.0) as c:
        r = await c.post(
            f"{BACKEND_URL}{path}",
            json=body,
            headers={"X-Admin-Token": ADMIN_TOKEN, "Content-Type": "application/json"},
        )
        r.raise_for_status()
        return r.json()

# ---------- Discord client ----------

intents = discord.Intents.default()
intents.message_content = False  # slash command 不需要讀取訊息內容

class OmgBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        if DISCORD_GUILD_ID:
            guild = discord.Object(id=int(DISCORD_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info("slash commands synced to guild %s", DISCORD_GUILD_ID)
        else:
            await self.tree.sync()
            log.info("slash commands synced globally (may take up to 1 hour)")

bot = OmgBot()

# ---------- Slash commands ----------

@bot.tree.command(name="help", description="顯示所有指令")
async def cmd_help(interaction: discord.Interaction) -> None:
    embed = discord.Embed(
        title="OMG 付款通知 Bot 指令一覽",
        color=COLOR_NEUTRAL,
        description=(
            "`/bind <token>` — 綁定 channel\n"
            "`/unbind` — 解除綁定\n"
            "`/today` — 今日訂單數與營業額\n"
            "`/orders` — 最近 20 筆訂單\n"
            "`/order <no>` — 查某筆訂單明細\n"
            "`/refund` — 進入退款流程\n"
            "`/health` — 系統健康狀態"
        ),
    )
    embed.set_footer(text="社群維護 · 非官方 · github.com/omgtwhub")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="bind", description="綁定此 channel 為付款事件接收對象")
@app_commands.describe(token="管理員 token（由後端 .env 產生）")
async def cmd_bind(interaction: discord.Interaction, token: str) -> None:
    if token != ADMIN_TOKEN:
        await interaction.response.send_message(
            "admin token 錯誤。", ephemeral=True,
        )
        return
    channel_id = interaction.channel_id
    if channel_id is None:
        await interaction.response.send_message("無法取得 channel id。", ephemeral=True)
        return
    NOTIFY_SUBSCRIBERS.add(channel_id)
    _save_binds()
    await interaction.response.send_message(
        f"已綁定此 channel（id={channel_id}），之後付款事件將推播至此。",
        ephemeral=True,
    )
    log.info("bind channel_id=%s", channel_id)

@bot.tree.command(name="unbind", description="解除當前 channel 的綁定")
async def cmd_unbind(interaction: discord.Interaction) -> None:
    channel_id = interaction.channel_id
    if channel_id in NOTIFY_SUBSCRIBERS:
        NOTIFY_SUBSCRIBERS.remove(channel_id)
        _save_binds()
        await interaction.response.send_message("已解除綁定。", ephemeral=True)
    else:
        await interaction.response.send_message(
            "此 channel 尚未綁定。", ephemeral=True,
        )

@bot.tree.command(name="today", description="顯示今日訂單數與營業額")
async def cmd_today(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend_get("/api/admin/orders/today")
        count = data.get("count", 0)
        amount = data.get("amount", 0)
        embed = discord.Embed(
            title="今日營業狀況",
            color=COLOR_NEUTRAL,
        )
        embed.add_field(name="訂單數", value=f"{count}", inline=True)
        embed.add_field(name="總金額", value=f"NTD {amount:,}", inline=True)
        if count > 0:
            embed.add_field(
                name="平均單價",
                value=f"NTD {amount // count:,}",
                inline=True,
            )
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"查詢失敗：{e}", ephemeral=True)

@bot.tree.command(name="orders", description="列出最近 20 筆訂單")
async def cmd_orders(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend_get("/api/admin/orders?limit=20")
        orders = data.get("orders", [])
        if not orders:
            await interaction.followup.send("目前沒有訂單。", ephemeral=True)
            return
        lines = [
            f"`{o['order_no']}` · NTD {o['amount']:,} · {o['status']}"
            for o in orders
        ]
        embed = discord.Embed(
            title=f"最近 {len(orders)} 筆訂單",
            description="\n".join(lines),
            color=COLOR_NEUTRAL,
        )
        embed.set_footer(text="使用 /order <訂單號> 查看明細")
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"查詢失敗：{e}", ephemeral=True)

@bot.tree.command(name="order", description="查詢某筆訂單明細")
@app_commands.describe(order_no="訂單號")
async def cmd_order(interaction: discord.Interaction, order_no: str) -> None:
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend_get(f"/api/admin/orders/{order_no}")
        o = data.get("order", {})
        embed = _order_detail_embed(o)
        view = None
        if o.get("status") == "paid":
            view = RefundConfirmView(order_no=o.get("order_no", ""), amount=int(o.get("amount", 0)))
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"查詢失敗：{e}", ephemeral=True)

@bot.tree.command(name="refund", description="進入退款流程（列出可退款訂單）")
async def cmd_refund(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend_get("/api/admin/orders?status=paid&limit=20")
        orders = data.get("orders", [])
        if not orders:
            await interaction.followup.send("目前沒有可退款的訂單。", ephemeral=True)
            return
        lines = [
            f"`{o['order_no']}` · NTD {o['amount']:,}"
            for o in orders
        ]
        embed = discord.Embed(
            title="可退款訂單",
            description="\n".join(lines) + "\n\n使用 `/order <訂單號>` 進入該筆訂單並點擊退款按鈕。",
            color=COLOR_REFUND,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"查詢失敗：{e}", ephemeral=True)

@bot.tree.command(name="health", description="顯示系統健康狀態")
async def cmd_health(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend_get("/api/admin/payment/health-summary")
        uptime = data.get("overall_uptime_24h", 0)
        total = data.get("total_probes_24h", 0)
        if uptime >= 99:
            color, status = COLOR_PAID, "健康"
        elif uptime >= 95:
            color, status = COLOR_WEBHOOK_FAIL, "注意"
        else:
            color, status = COLOR_HEALTH_ALERT, "異常"
        embed = discord.Embed(
            title=f"系統健康狀態：{status}",
            color=color,
        )
        embed.add_field(name="24h uptime", value=f"{uptime}%", inline=True)
        embed.add_field(name="24h probe 次數", value=f"{total}", inline=True)
        embed.set_footer(text=f"更新時間：{data.get('generated_at', '-')}")
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"查詢失敗：{e}", ephemeral=True)

# ---------- Helpers ----------

def _order_detail_embed(order: dict) -> discord.Embed:
    status = order.get("status", "")
    color = COLOR_PAID if status == "paid" else COLOR_NEUTRAL
    embed = discord.Embed(title="訂單明細", color=color)
    embed.add_field(name="訂單號", value=f"`{order.get('order_no', '')}`", inline=False)
    embed.add_field(name="金額", value=f"NTD {order.get('amount', 0):,}", inline=True)
    embed.add_field(name="狀態", value=status, inline=True)
    embed.add_field(name="付款方式", value=order.get("payment_method", "-"), inline=True)
    embed.add_field(name="建立時間", value=order.get("created_at", "-"), inline=False)
    embed.add_field(name="付款時間", value=order.get("paid_at", "-"), inline=False)
    return embed

# ---------- Refund confirmation view ----------

class RefundConfirmView(ui.View):
    """退款二次確認 UI。

    採警示不阻擋原則：即使超過建議上限，按鈕仍可點擊執行退款，
    僅於確認訊息中顯示警示供操作者判斷。
    """

    def __init__(self, order_no: str, amount: int) -> None:
        super().__init__(timeout=300)
        self.order_no = order_no
        self.amount = amount
        self.warnings = _refund_warnings(amount)

        label_suffix = "（超過建議上限）" if self.warnings else ""
        confirm_button = ui.Button(
            label=f"確認退款 NTD {amount:,}{label_suffix}",
            style=discord.ButtonStyle.danger,
            custom_id=f"refund_confirm:{order_no}:{amount}",
        )
        confirm_button.callback = self._confirm
        self.add_item(confirm_button)

        cancel_button = ui.Button(
            label="取消",
            style=discord.ButtonStyle.secondary,
            custom_id="refund_cancel",
        )
        cancel_button.callback = self._cancel
        self.add_item(cancel_button)

    def warning_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="退款確認",
            color=COLOR_REFUND,
        )
        embed.add_field(name="訂單號", value=f"`{self.order_no}`", inline=False)
        embed.add_field(name="金額", value=f"NTD {self.amount:,}", inline=True)
        if self.warnings:
            embed.add_field(
                name="警示",
                value="\n".join(f"• {w}" for w in self.warnings),
                inline=False,
            )
        embed.set_footer(text="此動作無法復原，請再次確認。")
        return embed

    async def _confirm(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            resp = await backend_post(
                "/api/admin/refund",
                {"order_no": self.order_no, "amount": self.amount},
            )
            _consume_refund_quota(self.amount)
            note = ""
            if self.warnings:
                note = "\n（本次退款超過建議上限，已記錄於每日統計）"
            embed = discord.Embed(
                title="退款已送出",
                color=COLOR_REFUND,
                description=(
                    f"訂單：`{self.order_no}`\n"
                    f"金額：NTD {self.amount:,}\n"
                    f"後端回應：{resp.get('status', 'ok')}{note}"
                ),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            log.info(
                "refund executed order_no=%s amount=%s warnings=%s",
                self.order_no, self.amount, self.warnings,
            )
        except Exception as e:
            await interaction.followup.send(f"退款失敗：{e}", ephemeral=True)
            log.error("refund failed order_no=%s error=%s", self.order_no, e)
        finally:
            self.stop()

    async def _cancel(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("已取消退款。", ephemeral=True)
        self.stop()

# ---------- FastAPI notify receiver ----------

notify_app = FastAPI()

@notify_app.post("/notify")
async def notify(req: Request) -> dict:
    body = await req.json()
    if body.get("admin_token") != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")

    kind = body.get("kind", "payment")
    text = body.get("text", "")
    order_no = body.get("order_no", "")
    amount = body.get("amount", 0)

    color = {
        "paid": COLOR_PAID,
        "refund": COLOR_REFUND,
        "failed": COLOR_WEBHOOK_FAIL,
        "health_alert": COLOR_HEALTH_ALERT,
    }.get(kind, COLOR_NEUTRAL)

    title = {
        "paid": "付款成功",
        "refund": "退款完成",
        "failed": "付款失敗",
        "health_alert": "系統警示",
    }.get(kind, "付款事件")

    embed = discord.Embed(title=title, description=text, color=color)
    if order_no:
        embed.add_field(name="訂單號", value=f"`{order_no}`", inline=True)
    if amount:
        embed.add_field(name="金額", value=f"NTD {int(amount):,}", inline=True)

    if not NOTIFY_SUBSCRIBERS:
        return {"ok": True, "note": "no-subscribers"}

    sent = 0
    for channel_id in list(NOTIFY_SUBSCRIBERS):
        channel = bot.get_channel(channel_id)
        if channel is None:
            continue
        try:
            await channel.send(embed=embed)
            sent += 1
        except Exception as e:
            log.warning("推播失敗 channel_id=%s: %s", channel_id, e)
    return {"ok": True, "sent_to": sent}

# ---------- Main ----------

async def main() -> None:
    _load_binds()
    if not DISCORD_BOT_TOKEN:
        raise SystemExit("請於 .env 設定 DISCORD_BOT_TOKEN")

    config = uvicorn.Config(
        notify_app,
        host="127.0.0.1",
        port=NOTIFY_PORT,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    log.info("Discord bot starting... notify HTTP on :%d", NOTIFY_PORT)
    await asyncio.gather(
        bot.start(DISCORD_BOT_TOKEN),
        server.serve(),
    )

if __name__ == "__main__":
    asyncio.run(main())
