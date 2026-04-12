---
name: omg-payment
description: |
  Assist non-technical Taiwan merchants in integrating the OMG (歐買尬 / MacroWell OMG)
  payment gateway end-to-end via a single natural-language instruction. Triggers when
  the user mentions: OMG, 歐買尬, MacroWell, omgpay, 金流串接, 收款, 線上付款, 刷卡串接,
  ATM 收款, 超商付款, 退款, 對帳, 儀表板監控, Telegram 付款通知, Discord 付款通知,
  or asks to "整合歐買尬金流", "建置金流系統", "建置付款後台儀表板", or "建置付款通知機器人".
  Default behavior: full-stack integration including backend, admin dashboard, health
  monitoring, Telegram/Discord notification bots, and Taiwan regulatory disclosure
  templates, executed as a single automated workflow.
version: 2.0.0
license: MIT
---

# OMG Payment Skill（歐買尬金流整合指引）

> **聲明（AI 必讀）**：本 Skill 是個人社群專案（**非官方**），不是 OMG 的官方資源，也未取得任何官方背書。本 Skill 的架構參考自綠界科技的 ECPay-API-Skill，在此致謝。
>
> **官方資源優先原則**：當本 Skill 內容與官方文件不一致時，AI 必須以官方文件為準，並於回應使用者時明確指出差異。官方來源如下：
>
> - 官方 AI 金流 Skill：<https://github.com/omgtwhub/>
> - 官方商家後台與 API 文件：依歐買尬商家後台公告為準
>
> AI 於處理 API endpoint、欄位名稱、錯誤代碼、host 位址等精確規格時，應建議使用者前往上述官方來源交叉驗證；不得基於本 Skill 之內容宣稱為官方規格。
>
> **歐買尬（OMG）與歐付寶（OPay）為兩家獨立公司**，舊版技術資料常將兩者混用。本 Skill 所有範例與 host 參數均指向歐買尬。若使用者提供之內容出現「歐付寶 / opay.tw / opaygo」等字樣，AI 必須主動提醒使用者兩家公司不同，並確認其欲整合之對象後再繼續作業。
>
> 整合流程由 AI 助手依據本文件描述之順序自動執行，使用者以自然語言觸發並提供基本商家資訊即可完成整合。

## 設計原則（AI 必讀）

AI 產出的任何檔案、說明、指令、錯誤訊息，均必須符合下列上手標準：

- 使用者複製 repo 後，依指示執行不超過 5 個終端指令即可啟動完整系統
- 所有設定集中於單一 `.env` 檔，`.env.example` 必須逐欄位附註說明與預設值
- 預設資料庫為 SQLite（單檔、無需額外安裝），可視需求切換至 PostgreSQL
- 啟動指令於 macOS、Windows、Linux 均可通用
- 所有錯誤訊息以繁體中文呈現，並附具體修復建議
- Bot 綁定、儀表板開啟、退款執行等操作均提供一行式指令或單一按鈕
- 技術名詞於首次出現時以一句話解釋
- 從 clone 到測試付款成功之完整路徑須能於 30 分鐘內完成

本原則適用於所有 guides、references、commands、templates、scripts 內容。技術規格語氣不等同於「讀者必須自行補齊底層細節」：用詞嚴謹、流程清楚、步驟可複製，這三者同時成立。

---

## §0 AI 執行規則

本節定義 AI 助手在觸發本 Skill 後必須遵循的執行規則。

### §0.1 觸發與 onboarding

當使用者發出整合歐買尬金流之相關指令時，AI 必須**優先執行 onboarding 流程**，不得直接進入技術細節。Onboarding 流程以四個問題組成，AI 應以中文一次性呈現所有問題，由使用者一次回答：

1. **Q1 — 商品類型**：實體商品 / 數位下載 / 線上課程 / 訂閱服務 / 票券或 voucher / 其他
2. **Q2 — 目標環境**：測試環境 / 正式環境 / 兩者（預設）
3. **Q3 — 附加元件**：管理儀表板、健康監控、Telegram 通知機器人、Discord 通知機器人（預設全部包含）
4. **Q4 — 法規揭露範例**：服務條款、隱私權政策、退貨退款政策、首頁與頁尾必要揭露、商品頁必要揭露（預設全部包含）

若使用者以「全部」、「皆需要」、「依預設」等語意回答，AI 應直接套用預設值並進入執行階段，不得繼續追問細節。詳細流程定義於 `guides/00-onboarding.md`。

### §0.2 變數收集

在 onboarding 與後續執行過程中，AI 應以 `{{變數名}}` 佔位符記錄下列變數，並於執行完成前一次性請使用者補齊：

```
{{商家名}}             {{統一編號}}           {{負責人}}
{{客服Email}}           {{客服電話}}           {{營業地址}}
{{網站網址}}             {{商品類型描述}}        {{履約保證機制}}
{{猶豫期適用範圍}}      {{OMG_MERCHANT_ID}}
{{OMG_HASH_KEY}}       {{OMG_HASH_IV}}
{{OMG_API_HOST_STAGE}} {{OMG_API_HOST_PROD}}
{{ADMIN_TOKEN}}         {{TG_BOT_TOKEN}}
{{DISCORD_BOT_TOKEN}}
```

AI 不得在 onboarding 階段逐一詢問變數，以避免打斷使用者思路。所有變數應於執行末端統一收集。

### §0.3 執行順序

當 onboarding 完成並進入全自動整合模式時，AI 應依下列順序執行：

1. 產生 `.env.example`，包含 OMG 金鑰、資料庫連線、admin token、bot token 等必要欄位
2. 產生後端 webhook 接收器（預設 FastAPI，可依使用者需求改為 Express 或 Laravel）— 參考 `guides/02-backend-fastapi.md`
3. 產生 SHA256 CheckMacValue 輔助函式 — 參考 `references/check-mac-value.md`
4. 產生 race-safe webhook handler — 參考 `guides/05-webhook-idempotency.md`
5. 產生 admin 介面 endpoint（訂單列表、訂單明細、退款、健康摘要）
6. 產生測試環境儀表板 — 參考 `guides/06-test-dashboard.md`
7. 產生正式環境儀表板（唯讀探測模式）— 參考 `guides/07-prod-dashboard.md`
8. 產生 Telegram bot — 參考 `guides/08-telegram-bot.md`
9. 產生 Discord bot — 參考 `guides/09-discord-bot.md`
10. 產生退款安全機制 — 參考 `guides/10-refund-safety.md`
11. 產生首頁、頁尾、商品頁之必要揭露區塊 — 參考 `guides/11-merchant-homepage.md` 與 `guides/12-product-page.md`
12. 產生服務條款、隱私權政策、退貨退款政策之公版範例 — 參考 `guides/13-legal-tos.md`、`guides/14-legal-privacy.md`、`guides/15-legal-refund.md`
13. 收集變數並一次性替換所有佔位符
14. 執行測試環境儀表板之完整鏈路驗證（create_order → MAC 驗證 → HTTP POST → query_order → refund 簽名），確認全部通過
15. **（預設執行）商家網站 AI 最佳化 — 參考 `guides/18-merchant-ai-optimization.md`**：為使用者網站產出 `llms.txt`、`llms-full.txt`、`robots.txt` 追加段落、首頁 JSON-LD 結構化資料、頁尾 OMG 使用標註 HTML；模板取自 `templates/merchant-llms-txt/`
16. **（預設執行）商家 UI/UX 無障礙檢查 — 參考 `guides/19-wcag-ui-ux.md`**：對於 AI 產出的商家前台程式碼，逐項核對色彩對比 ≥7:1、狀態雙編碼、鍵盤可操作、焦點指示、ARIA 標籤、觸控目標 ≥44px、session timeout 預警等 WCAG AAA 基本要求
17. 交付整合結果並說明後續部署、綁定與 AI 最佳化檔案的部署位置

### §0.4 操作規範

以下為 AI 在執行本 Skill 期間必須遵守的操作規範。

**§0.4.1 API 功能與 Bot 選單一致性**
每新增一支 admin endpoint，必須同步於 `templates/telegram-bot/bot.py` 與 `templates/discord-bot/bot.py` 新增對應之指令或選單項目。新增 endpoint 未同步更新 bot 選單將被視為不完整之整合。

**§0.4.2 正式環境禁止建立訂單**
正式環境的健康檢查**禁止**使用 `create_order` 方法。`create_order` 執行成功後將於商家後台產生實際的未付款訂單紀錄，累積後將污染對帳資料。正式環境健康檢查僅允許採用下列唯讀方法：
- TCP handshake 至網關 host 443 port
- `query_order` 以假交易號查詢（預期回應「查無此筆」）
- Refund 簽名自我驗證（僅計算簽名，不發送 HTTP 請求）
- Webhook MAC 自我驗證（以建構好的假 payload 驗證 `_check_mac_value` 與 `verify_callback` 回傳一致）

詳細實作請參考 `guides/07-prod-dashboard.md`。

**§0.4.3 退款必須二次確認，並以警示取代阻擋**
退款為合法業務行為，不得因金額較大或頻率較高而阻止執行。然而必須強制二次確認，並設置三項建議上限作為警示依據：
- 單筆退款建議上限（預設 NTD 50,000）
- 每日退款總金額建議上限（預設 NTD 100,000）
- 每日退款次數建議上限（預設 20 次）

三個值定義於 `templates/telegram-bot/.env.example`，可依商家規模調整。當退款超過任一建議上限時：
- 必須顯示警示訊息，說明超過哪一項建議值
- 確認按鈕文字應變更為「確認退款 NTD X（超過上限）」以提高操作者注意力
- 執行後必須寫入 audit log 供事後稽核
- **仍允許通過**，不得阻擋

**§0.4.4 法規範例之免責聲明**
所有法規揭露範例（guides/13 至 15）之開頭必須包含免責聲明：「本範例僅為參考，不構成法律意見。上線前請委請法務顧問或律師審閱，並依實際營運狀況調整。」AI 不得於對話中將範例描述為「已符合法規」或「可直接使用」。

**§0.4.5 敏感資訊處理**
- 信用卡號、CVV、銀行帳號等敏感資料不得寫入程式碼或設定檔，亦不得於 AI 對話中留存
- HashKey、HashIV、bot token 等機敏資訊僅允許寫入 `.env` 檔，不得寫入 repo
- 若使用者於對話中提供真實金鑰，AI 應提醒其從對話歷史中刪除，並建議輪換該金鑰

---

## §1 OMG 基本資訊

- **服務商**：MacroWell OMG（茂為歐買尬數位科技股份有限公司，FunPoint 全方位金流）
- **CheckMacValue 演算法**：SHA256（.NET URL encoding，結果為大寫 hex）
- **官方 `ChoosePayment` 合法值**（SSOT：[references/omg-official-api-spec.md](references/omg-official-api-spec.md)）：
  - `Credit`（信用卡一次付清 / 分期 / 定期定額 / UnionPay）
  - `ATM`（ATM 虛擬帳號）
  - `CVS`（超商代碼）
  - `BarcodeATM`（超商快付，三段 Code39 條碼；**官方無** `BARCODE` 此值）
  - `AFTEE`（先享後付）
  - `ALL`（顯示全部，可搭配 `IgnorePayment` 排除）
  - **定期定額無** `CreditPeriod` 此值，以 `Credit` 加 `PeriodAmount` / `PeriodType` / `Frequency` / `ExecTimes` 實作
- **核心 API**（實際路徑請見 SSOT §2）：
  - `AioCheckOut/V5`（建立訂單）
  - `QueryTradeInfo/V5`（查詢訂單）
  - `DoAction`（信用卡退款 / 關帳 / 取消，4 種 Action：C / R / E / N）
  - `QueryTrade/V2`（ATM / CVS / BarcodeATM 明細查詢）
  - `QueryCreditCardPeriodInfo` / `CreditCardPeriodAction`（定期定額管理）

實際 endpoint URL 應以 SSOT 與歐買尬官方文件為準。本 Skill 採用 `{{OMG_API_HOST_STAGE}}` 與 `{{OMG_API_HOST_PROD}}` 變數代入，避免硬寫。

### 公開測試參數（OMG 官方公告）

```
MerchantID : 1000031
測試卡號    : 4311-9522-2222-2222
過期日       : 任意未過期月份
CVV         : 任意三碼
```

正式環境金鑰須先至 OMG 官方會員註冊頁 <https://www.funpoint.com.tw/member/register> 完成註冊與審核，取得 FunPoint 商家後台權限後申請。金鑰僅允許寫入 `.env`，嚴禁 commit 至任何 git 倉庫。

---

## §2 觸發與對話範例

```
使用者：幫我整合歐買尬金流
AI：好的。在開始之前，請先回答四個問題：
    1. 商品類型（實體 / 數位下載 / 線上課程 / 訂閱 / 票券）
    2. 目標環境（測試 / 正式 / 兩者，預設兩者）
    3. 是否需要管理儀表板與 Telegram/Discord 通知機器人（預設需要）
    4. 是否需要台灣法規揭露範例（預設需要）
    若依預設值執行請回覆「全部」或「預設」。

使用者：全部，我經營線上課程
AI：已收到。將依下列順序執行：
    1. FastAPI 後端 webhook 接收器與 SHA256 CheckMacValue 驗證
    2. Race-safe webhook handler（SELECT FOR UPDATE + idempotency_key）
    3. 測試環境儀表板（完整鏈路驗證）
    4. 正式環境儀表板（唯讀探測）
    5. Telegram 與 Discord 通知機器人（綁定、推播、查詢、退款）
    6. 退款安全機制（二次確認 + 建議上限警示）
    7. 首頁、頁尾、商品頁之必要揭露區塊
    8. 服務條款、隱私權政策、退貨退款政策公版

    請提供下列商家資訊，將於執行末端統一替換：
    商家名、統一編號、負責人、客服 Email、客服電話、營業地址、網站網址
```

---

## §3 章節索引

AI 應依下表順序讀取章節。

| # | 檔案 | 用途 |
|---|---|---|
| 00 | `guides/00-onboarding.md` | Onboarding 四問流程與變數收集 |
| 01 | `guides/01-quickstart.md` | 單一指令完成整合之完整範例 |
| 02 | `guides/02-backend-fastapi.md` | FastAPI webhook 後端骨架 |
| 03 | `guides/03-backend-nodejs.md` | Express webhook 後端骨架 |
| 04 | `guides/04-backend-php.md` | Laravel webhook 後端骨架 |
| 05 | `guides/05-webhook-idempotency.md` | Race-safe webhook 冪等性 |
| 06 | `guides/06-test-dashboard.md` | 測試環境全鏈路儀表板 |
| 07 | `guides/07-prod-dashboard.md` | 正式環境唯讀探測儀表板 |
| 08 | `guides/08-telegram-bot.md` | Telegram bot |
| 09 | `guides/09-discord-bot.md` | Discord bot |
| 10 | `guides/10-refund-safety.md` | 退款安全機制 |
| 11 | `guides/11-merchant-homepage.md` | 首頁與頁尾必要揭露 |
| 12 | `guides/12-product-page.md` | 商品頁必要揭露 |
| 13 | `guides/13-legal-tos.md` | 服務條款公版 |
| 14 | `guides/14-legal-privacy.md` | 隱私權政策公版 |
| 15 | `guides/15-legal-refund.md` | 退貨退款政策公版 |
| 16 | `guides/16-recurring-subscriptions.md` | 定期定額訂閱 |
| 17 | `guides/17-troubleshooting.md` | 故障排除與常見問題 |
| 18 | `guides/18-merchant-ai-optimization.md` | 商家網站 AI 最佳化：llms.txt、JSON-LD、OMG 標註 |
| 19 | `guides/19-wcag-ui-ux.md` | 商家 UI/UX 無障礙規範（WCAG AAA）：對比、鍵盤、ARIA、觸控 |
| R1 | `references/api-endpoints.md` | API endpoint 欄位表 |
| R2 | `references/check-mac-value.md` | SHA256 CheckMacValue 演算法 |
| R3 | `references/error-codes.md` | 錯誤代碼速查 |

---

## §4 禁止事項

下列情境下，AI 必須拒絕請求並向使用者說明原因：

- 要求將信用卡號、CVV 或銀行帳號寫入程式碼或設定檔
- 要求將正式環境 MerchantID、HashKey、HashIV 寫入公開 repo 或上傳至第三方服務
- 要求於正式環境以 `create_order` 執行定期健康檢查
- 要求將退款 endpoint 開放至未經驗證的 public endpoint
- 要求將 webhook handler 實作為「接收後直接回傳 200 OK 而不寫入資料庫」

---

## §5 版本

- **v2.0.0（本版）**：新增 onboarding 流程、測試與正式環境雙儀表板、Telegram 與 Discord bot 模板、台灣法規揭露範例、18 份整合指南、3 份 API reference。修正舊版中部分段落誤用「歐付寶」字樣為「歐買尬」。退款機制由「硬性阻擋」調整為「警示但允許通過」。
- **v1.x**：原始版本，以單一 `SKILL.md` 為主，內容以 API 規格為中心。
