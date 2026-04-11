# Guide 08 — Telegram Bot（Bind / Notify / Menu）

> **硬規則（讀完這句再往下）**：
> **API 有什麼功能，bot menu 就要有對應按鈕**。每次新增一支 admin endpoint，必須同步更新 bot 的 CommandHandler。否則老闆的手機上會摸不到那個功能，等於白做。

---

## 零步驟 — 申請 Telegram Bot 與取得 token

如果你從來沒做過 Telegram Bot，照著下面七個步驟做，大約 3 分鐘：

1. 用你自己的手機或電腦 Telegram，搜尋並加入 `@BotFather`（官方帳號有藍色勾勾）
2. 在 BotFather 對話框中輸入 `/newbot`
3. 依指示輸入「顯示名稱」（例如：`Acme 金流小助手`），可含空格與中文
4. 再輸入「username」，必須以 `_bot` 結尾（例如：`acme_payment_bot`），只能用英數與底線
5. BotFather 回覆一段訊息，裡面有一行類似 `123456789:ABCdefGhIJKlmNoPQRsTUvwxyz-1234567890` 的 token，這就是你的 `TG_BOT_TOKEN`
6. 把 token 填到 `templates/telegram-bot/.env` 的 `TG_BOT_TOKEN=` 後面；這個檔案不可 commit
7. 於 BotFather 輸入 `/setdescription`、`/setabouttext`、`/setuserpic` 分別設定機器人描述與頭像，增加識別度

如果你的老闆或同事要收到通知，請他們先到 Telegram 搜尋你剛建立的 bot、按「START」一次，否則 bot 沒有權限主動傳訊給他們。之後他們在對話框輸入 `/bind <admin_token>` 完成綁定，即可開始收到通知。

如果要讓 bot 進群組，先把它拉進群組後，於 BotFather 執行 `/setprivacy`，選 `Disable`，讓 bot 能讀取群組訊息；接著在群組中輸入 `/bind@acme_payment_bot <admin_token>` 完成群組綁定。正式環境建議使用一個僅有相關人員的私人群組，避免 admin token 曝光。

> ⚠️ **安全提醒**：Telegram token 一旦外流，任何人都能以你的 bot 名義發送訊息。若不慎貼到公開處，請立即於 BotFather 執行 `/revoke`，取得新 token 後更新 `.env` 並重啟 bot。

---

## 為什麼一定要 bot

後台儀表板很漂亮，但老闆不會整天盯著電腦。週末、假日、半夜 —— 付款事件還是會發生。手機上沒有通知，等於沒監控。這就是為什麼本 Skill 把 TG bot 列為預設全自動產出之一。

- 有付款成功 → bot 推一張卡片到你的 TG
- 有付款失敗 → bot 推 ⚠️ 警告
- 有退款事件 → bot 推一張卡片含金額和操作人
- 要查訂單 → 手機上打 `/orders`，點某一筆看明細
- 要退款 → 手機上打 `/refund`，**選訂單 → 二次確認 → 執行**

---

## 三段式架構

### 1. Bind（綁定聊天室）

使用者在聊天室輸入：

```
/bind <admin_token>
```

bot 驗 token 成功後，把 `chat_id` 寫入 bind 清單。正式版建議用 DB + 多租戶欄位，template 用 `.bind_state.json` 暫存供原型測試。

### 2. Notify（推播付款事件）

bot 跑 polling 的同時啟一個小型 FastAPI notify endpoint（預設 `:9876`）。你的後端在 webhook 處理完成後，呼叫這支 endpoint：

```python
# 在後端的 webhook handler 最後呼叫
async with httpx.AsyncClient(timeout=3.0) as c:
    await c.post(
        "http://localhost:9876/notify",
        json={
            "admin_token": ADMIN_TOKEN,
            "kind": "paid",   # paid | failed | refunded
            "text": f"訂單 `{order_no}` 收款 NTD {amount:,} 成功",
        },
    )
```

bot 收到後會把訊息廣播給所有 bind 過的 chat_id。

### 3. Menu（選單式查詢與操作）

所有 command handler 最終都是**呼叫後端 admin API**，bot 自己不做 DB 操作。這樣可以保證：
- 退款一定經過後端的 idempotency 保護
- 權限 / 限流 / audit log 統一在後端
- bot 掛掉也不會影響業務

內建指令：

| 指令 | 對應後端 endpoint | 說明 |
|---|---|---|
| `/start` | — | 歡迎訊息 |
| `/bind <token>` | — | 綁定聊天室（用 admin token 驗） |
| `/unbind` | — | 解綁 |
| `/today` | `GET /api/admin/orders/today` | 今日訂單數 + 營業額 |
| `/orders` | `GET /api/admin/orders?limit=20` | 最近 20 筆訂單，點擊看明細 |
| `/order <no>` | `GET /api/admin/orders/{no}` | 某筆訂單明細 |
| `/refund` | `GET /api/admin/orders?status=paid&limit=20` | 選單式退款入口 |
| `/health` | `GET /api/admin/payment/health-summary` | 系統健康狀態 |
| `/help` | — | 所有指令列表 |

---

## 退款安全機制（警示而非阻擋）

退款是合法的業務行為，即便金額較大或頻率較高，仍應允許操作者執行。本 bot 的安全機制**不阻擋**退款，而是**提醒**操作者再次確認。設計理念是：上限的作用在於讓操作者停下來思考，而非阻止合法退款。

三項建議上限設定在 `templates/telegram-bot/bot.py`：

```python
REFUND_MAX_PER_ORDER   = 50000   # 單筆退款建議上限（TWD）
REFUND_DAILY_QUOTA     = 100000  # 每日退款總額建議上限（TWD）
REFUND_DAILY_COUNT_CAP = 20      # 每日退款次數建議上限
```

這三個值可於 `.env` 覆蓋，依商家實際營業規模調整。

### 退款執行流程

```
操作者於聊天室輸入 /refund
  ↓
bot 呼叫後端 GET /api/admin/orders?status=paid&limit=20
  ↓
顯示最近 20 筆可退款訂單（inline keyboard）
  ↓
操作者點擊某筆訂單
  ↓
bot 呼叫後端 GET /api/admin/orders/{order_no} 取得訂單明細
  ↓
呼叫 _refund_warnings(amount) 檢查是否超過建議上限
  ↓
顯示確認訊息：
  - 未超過上限：顯示訂單號 + 金額 + 確認 / 取消
  - 超過任一上限：顯示訂單號 + 金額 + ⚠️ 警示訊息
                  確認按鈕文字變更為「確認退款 NTD X（超過上限）」
  ↓
操作者點擊「確認退款」
  ↓
bot 呼叫後端 POST /api/admin/refund
  ↓
更新每日退款統計（_consume_refund_quota）
  ↓
回報結果。若原本超過上限，訊息附註「本次退款超過建議上限，已記錄於每日統計」
```

### 警示訊息範例

單筆超過上限：

```
退款確認
訂單：OMG20260412001
金額：NTD 80,000

⚠️ 本次退款 NTD 80,000 超過建議單筆上限 NTD 50,000。

此動作無法復原，請再次確認是否執行退款。

[確認退款 NTD 80,000（超過上限）]
[取消]
```

每日總額將超標：

```
退款確認
訂單：OMG20260412002
金額：NTD 30,000

⚠️ 執行後今日退款總額將達 NTD 120,000，超過建議每日上限 NTD 100,000。

此動作無法復原，請再次確認是否執行退款。

[確認退款 NTD 30,000（超過上限）]
[取消]
```

### 稽核紀錄

所有超過建議上限的退款都會寫入 bot log（`log.info("refund executed ... warnings=...")`），便於事後稽核與異常分析。建議正式部署時將 log 集中收集至 SIEM 或 log aggregation 系統。

---

## 完整 template

可用檔案在 `templates/telegram-bot/`：

```
templates/telegram-bot/
├── bot.py              完整 bot（polling + notify HTTP server 同一 process）
├── .env.example        環境變數範本
└── requirements.txt    pip 依賴清單
```

跑法：

```bash
cd templates/telegram-bot
pip install python-telegram-bot httpx python-dotenv fastapi uvicorn
cp .env.example .env
# 編輯 .env，填 TG_BOT_TOKEN / BACKEND_URL / ADMIN_TOKEN
python bot.py
```

然後到你自己的 TG 聊天室，加 bot 當好友，輸入：

```
/bind <你的 ADMIN_TOKEN>
```

看到「✅ 已綁定」就代表完成。接下來每一次後端 webhook 成功處理付款，都會推播一張卡片到這裡。

---

## 新增 endpoint 時的 checklist

你每次在後端新增一支 admin endpoint（例如 `/api/admin/coupons/issue`），請執行：

- [ ] 在 `bot.py` 新增對應 `cmd_xxx` handler
- [ ] 在 `Application.add_handler(CommandHandler(...))` 註冊
- [ ] 在 `/help` 指令列表加上新指令說明
- [ ] 在本 guide 的「內建指令」表格新增一列
- [ ] 如果是敏感操作（退款 / 發點數 / 改狀態），必須有 inline keyboard 二次確認

這條 checklist 請釘在 repo 的 `CONTRIBUTING.md`。

---

## 安全提醒

1. **TG bot token 不要寫進 repo**，一律走 `.env`
2. **admin token 定期輪換**，外流後馬上 `/unbind` 所有聊天室
3. **bot 不應該直接碰 DB**，所有操作都透過後端 admin API
4. **notify endpoint 要驗 admin token**，否則任何人可以偽造推播
5. **bot log 不要印完整 payload**，可能含個資

---

## 常見問題

**Q：可以多個人 bind 同一個 bot 嗎？**
可以，只要每個人都拿得到 admin token，都可以 `/bind`。收到付款事件時 bot 會廣播給所有 bind 過的 chat_id。

**Q：如果 admin token 外流怎麼辦？**
先把 `.env` 的 `ADMIN_TOKEN` 改掉並重啟後端 + bot，然後到所有受影響的聊天室執行 `/unbind`（或直接刪掉 `.bind_state.json`）。

**Q：可以把 bot 部署到雲端嗎？**
可以，`bot.py` 跟 `backend.py` 可以分別跑。只要兩邊的 `BACKEND_URL` / `NOTIFY_PORT` 對得上、`ADMIN_TOKEN` 一致就可以。正式部署強烈建議套 reverse proxy + TLS，且 `NOTIFY_PORT` 不要對外開放。

**Q：為什麼 refund 要在 bot 層和後端層都做 quota？**
雙保險。bot 層 quota 是「擋在呼叫後端之前」，減少無效 API 呼叫。後端層 quota 是「即使 bot 被 bypass 或 hack，最後一道防線還在」。
