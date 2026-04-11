# Guide 09 — Discord Bot

本指南說明 Discord 通知機器人的設計與實作。結構與 Telegram bot（`guides/08-telegram-bot.md`）對應，分為綁定（Bind）、通知（Notify）、選單（Menu）三段。所有 Telegram bot 提供之功能，Discord bot 必須完全對應。

## 零步驟 — 申請 Discord Bot 與取得 token

如果你沒做過 Discord Bot，照下面八個步驟，大約 5 分鐘：

1. 使用你的 Discord 帳號登入 <https://discord.com/developers/applications>
2. 點右上角 `New Application`，輸入應用程式名稱（例：`Acme 金流小助手`），勾選開發者條款後送出
3. 進入應用程式頁，左側選單點 `Bot`，再點 `Reset Token`，確認後複製跳出的 token，這就是你的 `DISCORD_BOT_TOKEN`
4. 於同頁面的 `Privileged Gateway Intents` 啟用下列選項：`Server Members Intent`、`Message Content Intent`；若無此權限 slash command 仍可運作，但讀取訊息與成員清單會受限
5. 左側選單點 `OAuth2` → `URL Generator`，在 `Scopes` 勾選 `bot` 與 `applications.commands`，在 `Bot Permissions` 勾選最小集合：`Send Messages`、`Embed Links`、`Use Slash Commands`、`Read Message History`
6. 複製頁面下方產生的邀請 URL，貼到瀏覽器，選擇要加入的伺服器（建議建立一個僅有相關人員的私人伺服器），按下授權
7. 把 token 填到 `templates/discord-bot/.env` 的 `DISCORD_BOT_TOKEN=` 後面；這個檔案不可 commit
8. 啟動 bot 後，於 Discord 伺服器任一頻道輸入 `/bind <admin_token>` 完成綁定

如果 slash command 送出後沒有自動補全，表示 bot 尚未把指令同步到該伺服器。`templates/discord-bot/bot.py` 在啟動時會自動執行 `tree.sync()`，首次同步可能需要最多 1 小時才會於所有客戶端出現；可改用 `tree.sync(guild=discord.Object(id=GUILD_ID))` 以 guild 為單位同步，立即生效。

> ⚠️ **安全提醒**：Discord token 不可寫入版本控制、不可分享於公開頻道。若不慎外流，立即於開發者後台 `Bot` 頁點 `Reset Token`，舊 token 立即失效，取得新 token 後更新 `.env` 並重啟 bot。

---

## 三段結構

**Bind**：使用者於 Discord 執行 `/bind` slash command，輸入 `{{ADMIN_TOKEN}}` 建立與後端 admin 的連結。綁定關係儲存於 `discord_subscribers` 表，包含 Discord user ID 與 channel ID。

**Notify**：後端於付款成功、退款完成、webhook 失敗、健康探測異常等事件發生時，向綁定的 Discord channel 推送 embed 訊息。

**Menu**：使用者透過 slash commands 或 embed 上的 button 操作查詢訂單、執行退款、檢視健康狀態。所有後端 admin endpoint 均必須對應到至少一個 slash command 或 button。

## 已提供之模板

```
templates/discord-bot/
├── bot.py         discord.py 應用程式
├── .env.example   環境變數範本
└── requirements.txt
```

### 啟動方式

```bash
cd templates/discord-bot
pip install -r requirements.txt
cp .env.example .env
# 編輯 .env，填入 DISCORD_BOT_TOKEN、BACKEND_URL、ADMIN_TOKEN 等
python bot.py
```

啟動前需於 Discord Developer Portal 建立 bot application、取得 token、啟用 `applications.commands` scope，並將 bot 邀請至目標 server。

## 指令對照表

| Slash command | 功能 | 對應後端 endpoint |
|---|---|---|
| `/bind <token>` | 綁定 admin token | `POST /api/admin/bind-discord` |
| `/unbind` | 解除綁定 | `POST /api/admin/unbind-discord` |
| `/today` | 查詢今日訂單摘要 | `GET /api/admin/summary/today` |
| `/orders [status]` | 查詢訂單列表 | `GET /api/admin/orders` |
| `/order <order_no>` | 查詢單筆訂單明細 | `GET /api/admin/orders/{order_no}` |
| `/refund <order_no> <amount>` | 發起退款流程 | `POST /api/admin/refund` |
| `/health` | 顯示金流健康狀態 | `GET /api/admin/health` |
| `/help` | 顯示指令說明 | — |

指令必須透過 `app_commands.CommandTree` 註冊並同步至 Discord。Slash command 的描述、參數 autocomplete 均應以繁體中文撰寫。

## 通知訊息格式

Discord bot 發送之通知建議使用 embed 物件，以便視覺化區分事件類型：

| 事件 | 顏色 | 標題 |
|---|---|---|
| 付款成功 | 0x22C55E（綠） | 付款成功通知 |
| 退款完成 | 0x3B82F6（藍） | 退款執行通知 |
| Webhook 失敗 | 0xF97316（橘） | Webhook 處理失敗 |
| 健康探測異常 | 0xEF4444（紅） | 金流健康告警 |

Embed 欄位應包含訂單號、金額、付款方式、時間等關鍵資訊，並於 footer 標註事件來源（例：`OMG Webhook / stage`）。

## 退款流程（警示但允許通過）

Discord bot 之退款流程與 Telegram bot 一致，採「二次確認 + 建議上限警示，不阻擋」之設計。

1. 使用者執行 `/refund <order_no> <amount>`
2. Bot 查詢後端取得該筆訂單狀態，確認為 `paid`
3. Bot 執行 `_refund_warnings(amount)` 檢查是否超過任一建議上限：
   - 單筆上限（`REFUND_MAX_PER_ORDER`，預設 50,000）
   - 每日總額上限（`REFUND_DAILY_QUOTA`，預設 100,000）
   - 每日次數上限（`REFUND_DAILY_COUNT_CAP`，預設 20）
4. Bot 發送確認 embed，包含 Confirm 與 Cancel 兩個 button
   - 若有任一項超過上限，embed 中顯示警示區塊說明超過哪一項
   - Confirm button 的 label 改為「確認退款 NTD X（超過上限）」
5. 使用者按下 Confirm 後，bot 呼叫 `POST /api/admin/refund`
6. 後端執行退款並寫入 `refund_audit_log`，warnings 內容一併記錄

退款不因超過任何上限而被阻擋，上限的作用僅為提醒使用者再次確認。完整設計原則請見 `guides/10-refund-safety.md`。

範例實作（節錄）：

```python
from discord import Embed, ui, ButtonStyle, Interaction
from discord.ext import commands
from discord import app_commands

class RefundConfirmView(ui.View):
    def __init__(self, order_no: str, amount: int, warnings: list[str]):
        super().__init__(timeout=120)
        self.order_no = order_no
        self.amount = amount
        self.warnings = warnings
        label = (
            f"確認退款 NTD {amount:,}（超過上限）"
            if warnings
            else f"確認退款 NTD {amount:,}"
        )
        self.confirm.label = label

    @ui.button(label="確認退款", style=ButtonStyle.danger)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        result = await backend_refund(self.order_no, self.amount, self.warnings)
        await interaction.response.edit_message(
            content=f"退款已執行：{result}", view=None
        )

    @ui.button(label="取消", style=ButtonStyle.secondary)
    async def cancel(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(content="已取消退款。", view=None)

@tree.command(name="refund", description="對指定訂單發起退款")
@app_commands.describe(order_no="訂單號", amount="退款金額（TWD）")
async def refund_cmd(interaction: Interaction, order_no: str, amount: int):
    order = await backend_get_order(order_no)
    if order["status"] != "paid":
        await interaction.response.send_message(
            f"訂單 {order_no} 目前狀態為 {order['status']}，無法退款。",
            ephemeral=True,
        )
        return

    warnings = _refund_warnings(amount)
    embed = Embed(title="退款確認", color=0xF97316 if warnings else 0x3B82F6)
    embed.add_field(name="訂單號", value=order_no, inline=False)
    embed.add_field(name="退款金額", value=f"NTD {amount:,}", inline=False)
    if warnings:
        embed.add_field(
            name="警示",
            value="\n".join(f"• {w}" for w in warnings),
            inline=False,
        )
    view = RefundConfirmView(order_no, amount, warnings)
    await interaction.response.send_message(
        embed=embed, view=view, ephemeral=True
    )
```

`_refund_warnings()` 與 `REFUND_LEDGER` 的實作與 Telegram bot 共用同一份邏輯，可抽離至 `templates/shared/refund_quota.py` 由兩個 bot 共同 import。

## 後端推送機制

後端於事件發生時，以 HTTP POST 通知 bot 行程的 notify server（預設 port 9877），bot 再經由 Discord API 送出訊息。Notify server 的驗證 header 應使用 `X-Admin-Token`，避免任意來源觸發推播。

```python
import os
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

@app.post("/notify/paid")
async def notify_paid(
    payload: dict,
    x_admin_token: str = Header(...),
):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(403)
    await broadcast_paid(payload)
    return {"ok": True}
```

## Discord 特有注意事項

1. Slash command 註冊後需呼叫 `tree.sync()`，第一次同步可能需數分鐘才會於客戶端顯示
2. Ephemeral 訊息（`ephemeral=True`）僅執行指令的使用者可見，適合用於退款確認等敏感操作
3. Bot 權限建議最小化：僅需 `Send Messages`、`Embed Links`、`Use Application Commands` 三項
4. 若 bot 需於多個 server 運作，綁定關係應以 `(guild_id, channel_id)` 為 key

## 安全提醒

1. `DISCORD_BOT_TOKEN` 僅可寫入 `.env`，不得寫入 repo
2. Notify server 應 bind 至 `127.0.0.1`，僅本機後端可呼叫
3. 退款確認 embed 必須採用 ephemeral 模式，避免訂單金額外洩至頻道
4. 綁定成功後，建議 bot 主動推送一則測試訊息確認推播路徑正常
