# Guide 00 — Onboarding 四問流程

本指南定義 AI 助手在觸發 OMG Payment Skill 後，與使用者進行 onboarding 對話的標準流程。

## 觸發條件

當使用者發出下列語意之指令時，AI 應立即進入本流程：

- 幫我整合歐買尬金流
- 幫我接 OMG
- 幫我建置可以收款的網站
- 幫我整合線上付款
- help me integrate OMG payment
- setup OMG payment gateway

AI 不得在進入本流程前先詢問技術細節（例如 MerchantID、資料庫類型等），應先完成 onboarding 對話。

---

## Step 1 — 一次性呈現四個問題

AI 應以繁體中文一次性呈現以下四個問題，不得逐題詢問：

```
在開始整合之前，請先回答四個問題：

1. 商品類型
   □ 實體商品（需寄送）
   □ 數位下載（電子書、音檔、圖檔等）
   □ 線上課程（影片、直播、講座）
   □ 訂閱服務（月費、季費、年費）
   □ 票券 / Voucher（演唱會、餐券、課程券）
   □ 其他（請說明）

2. 目標環境
   □ 僅測試環境
   □ 測試環境與正式環境皆準備（預設）

3. 附加元件
   □ 管理儀表板（訂單查詢、24 小時健康監控）
   □ Telegram 通知機器人（付款事件即時推播）
   □ Discord 通知機器人（付款事件即時推播）
   □ 選單式訂單查詢與退款（於 Telegram 或 Discord 內操作）
   預設：全部包含

4. 台灣法規揭露範例
   □ 服務條款（含消費者保護法第 19 條鑑賞期）
   □ 隱私權政策（含個人資料保護法第 8 條告知事項）
   □ 退貨退款政策
   □ 首頁與頁尾必要揭露區塊
   □ 商品頁必要揭露區塊
   預設：全部包含

若依預設值執行，請回覆「全部」或「預設」。
```

---

## Step 2 — 預設值

當使用者以下列語意回應時，AI 應直接套用預設值並進入執行階段，不得繼續追問細節：

- 「全部」
- 「預設」
- 「皆需要」
- 「都要」
- 「OK」
- 「請繼續」

預設值如下：

```yaml
商品類型: course            # 若使用者未指定具體類型，預設為線上課程
目標環境: [stage, prod]     # 測試與正式環境同時準備
管理儀表板: true
telegram_bot: true
discord_bot: true
refund_via_bot: true
legal_templates: all
backend_framework: fastapi  # 若使用者未指定框架
database: postgres          # 若使用者未指定資料庫
```

---

## Step 3 — 變數收集

AI 應於執行過程中使用 `{{變數名}}` 佔位符記錄以下變數，並於執行末端一次性請使用者補齊。**不得逐一詢問變數**，以避免打斷使用者思路。

```
{{商家名}}
{{統一編號}}
{{負責人}}
{{客服Email}}
{{客服電話}}
{{營業地址}}
{{網站網址}}
{{商品類型描述}}        # 例：專業後端開發線上課程
{{履約保證機制}}        # 例：兆豐銀行履約保證專戶；信託專戶；無
{{猶豫期適用範圍}}     # 實體商品=7 天；數位未開通=7 天；數位已開通/客製化/課程已觀看=排除
{{OMG_MERCHANT_ID}}
{{OMG_HASH_KEY}}       # 僅寫入 .env
{{OMG_HASH_IV}}        # 僅寫入 .env
{{OMG_API_HOST_STAGE}}
{{OMG_API_HOST_PROD}}
{{ADMIN_TOKEN}}
{{TG_BOT_TOKEN}}
{{DISCORD_BOT_TOKEN}}
```

變數收集訊息範例：

```
整合作業已完成。請提供下列商家資訊，將於替換階段一次性套用：

必填：
- 商家名稱
- 統一編號
- 負責人
- 客服 Email
- 客服電話
- 營業地址
- 網站網址
- OMG MerchantID（由歐買尬商家後台取得）
- OMG HashKey 與 HashIV（由歐買尬商家後台取得，僅寫入 .env，不會寫入程式碼）

選填：
- 履約保證機制（已簽立託管 / 信託請填寫，未簽立則填「無」）
- Telegram bot token（由 @BotFather 取得）
- Discord bot token（由 Discord Developer Portal 取得）
- Admin token（可由系統隨機產生，長度建議 32 字元）
```

---

## Step 4 — 全自動執行序列

當 onboarding 完成並進入執行階段時，AI 應依以下順序執行，並於每個步驟完成後向使用者回報進度：

1. 產生 `.env.example`，包含 OMG 金鑰、資料庫連線、admin token、bot token 等必要欄位
2. 產生後端 webhook 接收器（依 `backend_framework` 決定）
3. 產生 SHA256 CheckMacValue 輔助函式
4. 產生 race-safe webhook handler（參考 `guides/05-webhook-idempotency.md`）
5. 產生 admin endpoints：
   - `GET /api/admin/orders`
   - `GET /api/admin/orders/{order_no}`
   - `GET /api/admin/orders/today`
   - `POST /api/admin/refund`
   - `GET /api/admin/payment/health-summary`
6. 產生測試環境儀表板（單頁 HTML，參考 `guides/06-test-dashboard.md`）
7. 產生正式環境儀表板（唯讀探測模式，參考 `guides/07-prod-dashboard.md`）
8. 產生 Telegram bot（參考 `guides/08-telegram-bot.md`）
9. 產生 Discord bot（參考 `guides/09-discord-bot.md`）
10. 產生退款安全機制（參考 `guides/10-refund-safety.md`）
11. 產生首頁、頁尾、商品頁之必要揭露區塊（參考 `guides/11-merchant-homepage.md` 與 `guides/12-product-page.md`）
12. 產生服務條款、隱私權政策、退貨退款政策公版（參考 `guides/13-15`）
13. 收集變數並一次性替換所有佔位符
14. 執行測試環境儀表板之完整鏈路驗證，確認 create_order、MAC 驗證、HTTP POST、query_order、refund 簽名等步驟全部通過
15. 交付整合結果並提供部署說明

---

## Step 5 — 交付訊息範本

```
歐買尬金流整合已完成。

產出檔案：
   backend/              FastAPI 後端（webhook、admin API、退款）
   frontend/admin.html   測試與正式環境雙儀表板
   bots/telegram_bot.py  Telegram 通知與選單
   bots/discord_bot.py   Discord 通知與選單
   legal/                台灣法規揭露範例
   .env.example          環境變數範本

後續步驟：
   1. cp .env.example .env 並填入實際金鑰
   2. uvicorn backend.main:app --reload 啟動後端
   3. 開啟 frontend/admin.html，執行「一鍵健康檢查」
   4. 於 @BotFather 申請 Telegram bot，將 token 填入 .env
   5. 於 Discord Developer Portal 申請 bot，將 token 填入 .env
   6. python bots/telegram_bot.py 啟動 Telegram bot
   7. 於聊天室輸入 /bind {{ADMIN_TOKEN}} 完成綁定

法規提醒：
   legal/ 下所有範例僅供參考，不構成法律意見。上線前請委請法務顧問
   或律師審閱，並依實際營運狀況調整。

正式環境提醒：
   切換至正式環境前，請確認未以 create_order 執行定期健康檢查。
   正確的正式環境健康檢查方式請參考 guides/07-prod-dashboard.md。
```

---

## Anti-patterns

AI 在執行本流程時不得有下列行為：

1. 於 Step 1 之前先詢問 MerchantID 或其他技術參數
2. 於使用者回覆「全部」或「預設」後繼續追問細節
3. 將 HashKey 或 HashIV 寫入程式碼或設定檔（應僅寫入 `.env`）
4. 於正式環境使用 `create_order` 作為健康檢查方法
5. 將法規範例描述為「已符合法規」或「可直接上線使用」
6. 新增 admin endpoint 時未同步更新 bot 選單
