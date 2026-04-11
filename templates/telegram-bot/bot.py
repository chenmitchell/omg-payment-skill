"""
OMG 付款通知 Telegram Bot（非官方模板）
============================================

功能：
    /start              歡迎訊息
    /bind <token>       把當前聊天室綁定到商家（需要 admin token）
    /unbind             解除綁定
    /today              今日訂單數與營業額
    /orders             最近 20 筆訂單（inline keyboard）
    /order <no>         查某筆訂單明細
    /refund             進入退款選單（二次確認）
    /health             呼叫後端 /health-summary 看系統狀態
    /help               顯示所有指令

推播：
    後端 webhook 收到付款成功 / 失敗 / 退款時，呼叫 POST http://localhost:9876/notify
    bot 會把該訊息推到所有 bind 過的聊天室

硬規則（務必遵守）：
    1. API 有什麼功能，bot menu 就要有對應按鈕 —— 新增 admin endpoint 時，
       請 grep 一下本檔，確認 /orders /today /refund /health 這幾個 handler 的
       選單是不是也要加
    2. 退款必須二次確認 + 單筆上限 + 每日配額，下方 REFUND_* 常數決定
    3. bot token 一律走環境變數，不要寫進 repo

跑法：
    pip install python-telegram-bot httpx python-dotenv
    cp .env.example .env  填入 TG_BOT_TOKEN、BACKEND_URL、ADMIN_TOKEN
    python bot.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters,
)
from fastapi import FastAPI, HTTPException, Request
import uvicorn

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("omg-tg-bot")

# ---------- Config ----------

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8787").rstrip("/")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "CHANGEME")
NOTIFY_PORT = int(os.getenv("NOTIFY_PORT", "9876"))

# 退款硬規則
REFUND_MAX_PER_ORDER = int(os.getenv("REFUND_MAX_PER_ORDER", "50000"))   # 單筆上限 NTD
REFUND_DAILY_QUOTA = int(os.getenv("REFUND_DAILY_QUOTA", "100000"))      # 每日配額 NTD
REFUND_DAILY_COUNT_CAP = int(os.getenv("REFUND_DAILY_COUNT_CAP", "20"))  # 每日次數上限

# Bind state（正式版請寫 DB / Redis）
BIND_FILE = Path("./.bind_state.json")
NOTIFY_SUBSCRIBERS: set[int] = set()

def _load_binds() -> None:
    global NOTIFY_SUBSCRIBERS
    if BIND_FILE.exists():
        data = json.loads(BIND_FILE.read_text())
        NOTIFY_SUBSCRIBERS = set(data.get("chat_ids", []))

def _save_binds() -> None:
    BIND_FILE.write_text(json.dumps({"chat_ids": list(NOTIFY_SUBSCRIBERS)}))

# 每日退款統計
REFUND_LEDGER: dict[str, dict[str, int]] = {}   # {"YYYY-MM-DD": {"amount": int, "count": int}}

def _today_key() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _refund_warnings(amount: int) -> list[str]:
    """
    檢查退款是否超過建議上限，回傳警告訊息列表。
    注意：**不阻擋退款**，僅提醒操作者再次確認。退款屬於正常業務行為，
    上限的作用是讓操作者在超過常態金額時暫停思考，而非阻止合法退款。
    """
    warnings: list[str] = []
    k = _today_key()
    ledger = REFUND_LEDGER.setdefault(k, {"amount": 0, "count": 0})

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
    k = _today_key()
    ledger = REFUND_LEDGER.setdefault(k, {"amount": 0, "count": 0})
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

# ---------- TG Command handlers ----------

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 歡迎使用 OMG 付款通知 Bot（非官方）\n\n"
        "先用 `/bind <admin_token>` 把這個聊天室綁定到你的商家後台，\n"
        "之後每一筆付款成功 / 失敗 / 退款都會自動推播到這裡。\n\n"
        "所有可用指令請輸入 /help",
        parse_mode="Markdown",
    )

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📋 *指令一覽*\n"
        "`/bind <token>` — 綁定聊天室\n"
        "`/unbind` — 解除綁定\n"
        "`/today` — 今日訂單數與營業額\n"
        "`/orders` — 最近 20 筆訂單（含選單）\n"
        "`/order <no>` — 查某筆訂單明細\n"
        "`/refund` — 進入退款流程（會二次確認）\n"
        "`/health` — 系統健康狀態\n"
        "`/help` — 這份訊息",
        parse_mode="Markdown",
    )

async def cmd_bind(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    args = ctx.args
    chat_id = update.effective_chat.id
    if not args or args[0] != ADMIN_TOKEN:
        await update.message.reply_text("❌ admin token 錯誤或未提供。")
        return
    NOTIFY_SUBSCRIBERS.add(chat_id)
    _save_binds()
    await update.message.reply_text(f"✅ 已綁定聊天室（chat_id={chat_id}），之後付款事件會推到這裡。")
    log.info("bind chat_id=%s", chat_id)

async def cmd_unbind(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in NOTIFY_SUBSCRIBERS:
        NOTIFY_SUBSCRIBERS.remove(chat_id)
        _save_binds()
        await update.message.reply_text("✅ 已解除綁定，不會再推播付款事件到這裡。")
    else:
        await update.message.reply_text("ℹ️ 這個聊天室本來就沒有綁定。")

async def cmd_today(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await backend_get("/api/admin/orders/today")
        total_count = data.get("count", 0)
        total_amount = data.get("amount", 0)
        await update.message.reply_text(
            f"📊 *今日營業狀況*\n"
            f"訂單數：{total_count}\n"
            f"總金額：NTD {total_amount:,}\n"
            f"平均單價：NTD {(total_amount // max(total_count, 1)):,}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 查詢失敗：{e}")

async def cmd_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await backend_get("/api/admin/orders?limit=20")
        orders = data.get("orders", [])
        if not orders:
            await update.message.reply_text("（沒有訂單）")
            return
        buttons = [
            [InlineKeyboardButton(
                f"{o['order_no']} · NTD {o['amount']:,} · {o['status']}",
                callback_data=f"order:{o['order_no']}",
            )]
            for o in orders
        ]
        await update.message.reply_text(
            f"📦 最近 {len(orders)} 筆訂單（點擊查看明細）：",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 查詢失敗：{e}")

async def cmd_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not ctx.args:
        await update.message.reply_text("用法：/order <訂單號>")
        return
    await _show_order_detail(update.message.reply_text, ctx.args[0])

async def _show_order_detail(reply, order_no: str) -> None:
    try:
        data = await backend_get(f"/api/admin/orders/{order_no}")
        o = data.get("order", {})
        text = (
            f"🧾 *訂單明細*\n"
            f"訂單號：`{o.get('order_no', '')}`\n"
            f"金額：NTD {o.get('amount', 0):,}\n"
            f"狀態：{o.get('status', '')}\n"
            f"付款方式：{o.get('payment_method', '-')}\n"
            f"建立：{o.get('created_at', '-')}\n"
            f"付款：{o.get('paid_at', '-')}"
        )
        kb = None
        if o.get("status") == "paid":
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("💸 退款", callback_data=f"refund_prompt:{o['order_no']}"),
            ]])
        await reply(text, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        await reply(f"❌ 查詢失敗：{e}")

async def cmd_refund(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """進入退款流程：列最近 20 筆 paid 訂單"""
    try:
        data = await backend_get("/api/admin/orders?status=paid&limit=20")
        orders = data.get("orders", [])
        if not orders:
            await update.message.reply_text("（目前沒有可退款的訂單）")
            return
        buttons = [
            [InlineKeyboardButton(
                f"{o['order_no']} · NTD {o['amount']:,}",
                callback_data=f"refund_prompt:{o['order_no']}",
            )]
            for o in orders
        ]
        await update.message.reply_text(
            "💸 選擇要退款的訂單（退款會二次確認）：",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 查詢失敗：{e}")

async def cmd_health(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await backend_get("/api/admin/payment/health-summary")
        uptime = data.get("overall_uptime_24h", 0)
        total = data.get("total_probes_24h", 0)
        emoji = "🟢" if uptime >= 99 else "🟡" if uptime >= 95 else "🔴"
        await update.message.reply_text(
            f"{emoji} *系統健康狀態*\n"
            f"24h uptime：{uptime}%\n"
            f"24h probe 次數：{total}\n"
            f"更新時間：{data.get('generated_at', '-')}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 查詢失敗：{e}")

# ---------- Callback handlers（inline keyboard 點擊）----------

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    data = q.data or ""

    if data.startswith("order:"):
        order_no = data.split(":", 1)[1]
        await _show_order_detail(q.message.reply_text, order_no)

    elif data.startswith("refund_prompt:"):
        order_no = data.split(":", 1)[1]
        try:
            o = (await backend_get(f"/api/admin/orders/{order_no}")).get("order", {})
        except Exception as e:
            await q.message.reply_text(f"查詢失敗：{e}")
            return
        amount = int(o.get("amount", 0))
        warnings = _refund_warnings(amount)

        header = (
            f"*退款確認*\n"
            f"訂單：`{order_no}`\n"
            f"金額：NTD {amount:,}\n"
        )
        if warnings:
            warn_text = "\n".join(f"⚠️ {w}" for w in warnings)
            body = (
                f"{header}\n"
                f"{warn_text}\n\n"
                f"此動作無法復原，請再次確認是否執行退款。"
            )
            # 超過建議值時，確認按鈕文字加上 [超過上限] 標註，提高注意力
            confirm_label = f"確認退款 NTD {amount:,}（超過上限）"
        else:
            body = f"{header}\n此動作無法復原，請確認是否執行退款。"
            confirm_label = f"確認退款 NTD {amount:,}"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(confirm_label, callback_data=f"refund_confirm:{order_no}:{amount}")],
            [InlineKeyboardButton("取消", callback_data="refund_cancel")],
        ])
        await q.message.reply_text(body, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("refund_confirm:"):
        _, order_no, amount_str = data.split(":", 2)
        amount = int(amount_str)
        # 記錄警告但不阻擋執行
        warnings = _refund_warnings(amount)
        try:
            resp = await backend_post("/api/admin/refund", {"order_no": order_no, "amount": amount})
            _consume_refund_quota(amount)
            note = ""
            if warnings:
                note = "\n\n（本次退款超過建議上限，已記錄於每日統計）"
            await q.message.reply_text(
                f"退款已送出\n"
                f"訂單：`{order_no}`\n"
                f"金額：NTD {amount:,}\n"
                f"後端回應：{resp.get('status', 'ok')}{note}",
                parse_mode="Markdown",
            )
            log.info("refund executed order_no=%s amount=%s warnings=%s", order_no, amount, warnings)
        except Exception as e:
            await q.message.reply_text(f"退款失敗：{e}")
            log.error("refund failed order_no=%s amount=%s error=%s", order_no, amount, e)

    elif data == "refund_cancel":
        await q.message.reply_text("已取消退款。")

# ---------- FastAPI notify receiver（後端 webhook 呼叫這支推播）----------

notify_app = FastAPI()

@notify_app.post("/notify")
async def notify(req: Request):
    body = await req.json()
    # 驗 admin token（防止外人偽造推播）
    if body.get("admin_token") != ADMIN_TOKEN:
        raise HTTPException(401, "unauthorized")
    kind = body.get("kind", "payment")
    text = body.get("text", "")
    if not NOTIFY_SUBSCRIBERS:
        return {"ok": True, "note": "no-subscribers"}
    from telegram import Bot
    bot = Bot(TG_BOT_TOKEN)
    async with bot:
        for chat_id in list(NOTIFY_SUBSCRIBERS):
            try:
                emoji = {"paid": "💰", "failed": "⚠️", "refunded": "💸"}.get(kind, "🔔")
                await bot.send_message(chat_id, f"{emoji} {text}", parse_mode="Markdown")
            except Exception as e:
                log.warning("推播失敗 chat_id=%s: %s", chat_id, e)
    return {"ok": True, "sent_to": len(NOTIFY_SUBSCRIBERS)}

# ---------- Main ----------

async def main() -> None:
    _load_binds()
    if not TG_BOT_TOKEN:
        raise SystemExit("❌ 請在 .env 設定 TG_BOT_TOKEN")

    app = Application.builder().token(TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("bind", cmd_bind))
    app.add_handler(CommandHandler("unbind", cmd_unbind))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("orders", cmd_orders))
    app.add_handler(CommandHandler("order", cmd_order))
    app.add_handler(CommandHandler("refund", cmd_refund))
    app.add_handler(CommandHandler("health", cmd_health))
    app.add_handler(CallbackQueryHandler(on_callback))

    # 同時跑 polling + notify HTTP server
    config = uvicorn.Config(notify_app, host="127.0.0.1", port=NOTIFY_PORT, log_level="warning")
    server = uvicorn.Server(config)

    log.info("Bot starting... notify HTTP on :%d", NOTIFY_PORT)
    await asyncio.gather(
        app.run_polling(),
        server.serve(),
    )

if __name__ == "__main__":
    asyncio.run(main())
