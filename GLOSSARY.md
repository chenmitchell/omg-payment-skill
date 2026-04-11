# Glossary — 名詞對照表

> 本 Skill 使用之專有名詞、縮寫、金流術語對照。AI 助手載入本 repo 時可將本檔作為消歧義（disambiguation）依據。

## 金流主體

| 名詞 | 說明 |
|---|---|
| **OMG / 歐買尬** | 本 Skill 目標整合對象。正式公司名稱為「茂為歐買尬數位科技股份有限公司」（MacroWell OMG，統編 70444999），提供 FunPoint 全方位金流服務（本 Skill 處理對象） |
| **OPay / 歐付寶** | 歐付寶電子支付股份有限公司。**依經濟部公司登記資料，其董事長與全體法人董事均由茂為歐買尬（統編 70444999）指派**——即 OPay 為 OMG 旗下電支子公司。雖同屬 OMG 集團，但 OPay 運行的是**另一套獨立的金流 API**（non-FunPoint），本 Skill 不適用 |
| **ECPay / 綠界科技** | 綠界科技股份有限公司。**依經濟部公司登記資料，其董事長與全體法人董事均由茂為歐買尬（統編 70444999）指派**——即 ECPay 亦為 OMG 旗下子公司。ECPay 運行的是**另一套獨立的金流 API**，本 Skill 不適用。ECPay 亦為本 Skill 架構的致敬對象，官方 repo <https://github.com/ECPay/ECPay-API-Skill> |
| **NewebPay / 藍新金流** | 台灣另一家主要金流服務商，與本 Skill 無關 |
| **TapPay / 遊戲橘子** | 台灣 tokenization 金流服務商，與本 Skill 無關 |

## 核心技術術語

| 名詞 | 說明 |
|---|---|
| **CheckMacValue** | OMG 金流使用之簽章機制。將參數按字母序排序後，加上 HashKey / HashIV，經 .NET URL encode 後取 SHA256，轉大寫得到最終簽章。詳見 `references/check-mac-value.md` |
| **HashKey / HashIV** | 由 OMG 商家後台提供之簽章金鑰對。測試環境與正式環境各一組，**嚴禁寫入 repo** |
| **MerchantID** | 商家編號。測試環境公開值為 `1000031`；正式環境須先至 OMG 官方會員註冊頁 <https://www.funpoint.com.tw/member/register> 註冊並通過審核，取得 FunPoint 商家後台權限後申請 |
| **MerchantTradeNo** | 商家訂單編號，長度通常限 20 字元，建議用 `timestamp + 亂數` 組合 |
| **TradeNo** | OMG 回傳之歐買尬端交易編號，與 MerchantTradeNo 一對一對應 |
| **RtnCode / RtnMsg** | OMG 回傳狀態碼與訊息。`RtnCode=1` 為成功 |
| **PaymentType** | 付款方式字串，如 `Credit_CreditCard`、`ATM_TAISHIN` 等 |
| **ChoosePayment** | 歐買尬官方付款方式參數。**官方合法值**僅：`Credit`、`ATM`、`CVS`、`BarcodeATM`、`AFTEE`、`ALL`。**官方沒有** `BARCODE`（超商條碼）這個值，也沒有 `CreditPeriod` — 定期定額是用 `Credit` + `PeriodAmount/PeriodType/Frequency/ExecTimes` 子參數。事實依據：`references/omg-official-api-spec.md` §3 |

## Skill / AI 相關術語

| 名詞 | 說明 |
|---|---|
| **AI Skill** | 一組 Markdown + 程式範本 + 測試向量組成之知識包，用於提高 AI 助手在特定領域的表現 |
| **SKILL.md** | Skill 的主入口，包含執行規則與指引順序。被多數 AI 平台（Claude Code / Cursor / Windsurf / Cowork）識別 |
| **llms.txt** | 站點級的 LLM 友善索引，類似 `robots.txt` 但目標是 LLM 爬蟲。提案見 <https://llmstxt.org> |
| **§0 執行規則** | SKILL.md 中強制 AI 優先遵守之規則段落，例如「涉及 webhook 必讀 guides/05」 |
| **Four-question onboarding** | `guides/00-onboarding.md` 定義之四問需求收集流程：商品性質 / 環境 / 儀表板 / 法規 |

## 架構設計術語

| 名詞 | 說明 |
|---|---|
| **Webhook 冪等性** | 確保同一個 webhook 訊息被重送多次，系統狀態只被變更一次。本 Skill 使用 `idempotency_key` + `SELECT ... FOR UPDATE` 實作 |
| **Race-safe** | 在多執行緒 / 多 pod 同時處理同一筆 webhook 時，不會產生重複寫入的設計 |
| **idempotency_key** | 由 `MerchantTradeNo + TradeNo + RtnCode + PaymentDate` 等欄位 hash 產生之唯一鍵 |
| **Early-dup** | 特殊情況：訂單尚未寫入 DB，webhook 先到。此時 handler 應回覆 OMG 請求重送，而非吞掉訊息 |
| **Bind / Notify / Menu** | Telegram / Discord bot 之三段結構：綁定管理員 chat_id、事件推播、選單操作 |
| **警示不阻擋** | 退款設計原則：超過單筆 / 每日 / 次數上限時僅顯示警示，由操作者判斷是否執行，不自動拒絕 |
| **唯讀探測** | 正式環境健康檢查不得使用 `create_order`。改以 TCP handshake / `query_order(fake_no)` / refund 簽章自測 / webhook MAC 自測四項不產生新狀態之方法 |
| **API-Menu parity** | admin API 與 bot 選單之一對一對應原則。由 `scripts/validate-bot-menu-parity.sh` 自動驗證 |

## 台灣法規術語

| 名詞 | 說明 |
|---|---|
| **消費者保護法** | 《消費者保護法》。第 19 條為通訊交易解約期間（通稱「七天鑑賞期」）的來源 |
| **個人資料保護法 / 個資法** | 《個人資料保護法》。本 Skill 隱私權範本的主要依據 |
| **數位內容排除條款** | 消保法第 19 條第 2 項授權行政院訂定之排除清單。線上音樂、電子書、線上課程等符合要件者可排除七日解約權 |
| **電子商務**、**通訊交易** | 消保法第 2 條定義之商業類型 |

## 測試與驗證術語

| 名詞 | 說明 |
|---|---|
| **Test vector / 測試向量** | SSOT 測試資料，用於跨語言實作一致性驗證。本 Skill 於 `test-vectors/check-mac-value.json` 定義 3 組向量 |
| **SSOT / Single Source of Truth** | 單一真相來源原則。本 Skill 將 CheckMacValue 測試向量、admin API 列表等關鍵資訊僅維護於一處 |
| **Validator** | `scripts/validate-*.sh` 中的驗證腳本，於 CI 執行，擋下不符合 repo 規範之 PR |
| **Parity 檢查** | 確認兩份資料同步的驗證，如版本號同步、bot 選單與 admin API 同步 |

## 縮寫速查

| 縮寫 | 全稱 |
|---|---|
| **MAC** | Message Authentication Code（本 Skill 特指 CheckMacValue） |
| **WH** | Webhook |
| **CVV** | Card Verification Value |
| **3DS** | 3-D Secure（信用卡線上驗證） |
| **PTA** | Period Payment（定期定額） |
| **ToS** | Terms of Service（服務條款） |
| **PP** | Privacy Policy（隱私權政策） |
| **KYC** | Know Your Customer |
| **SDK** | Software Development Kit |
| **MCP** | Model Context Protocol |
| **CI/CD** | Continuous Integration / Continuous Deployment |

## 易混淆術語澄清

- **歐買尬 vs 歐付寶 vs 綠界（集團關係與 API 關係必須分開看）**：
  - **集團層面**：三家並非互相獨立。茂為歐買尬（統編 70444999）為歐付寶與綠界兩家的法人股東，依經濟部公開公司登記資料，兩家公司的董事長與法人董事席位均由茂為歐買尬指派，即 OPay 與 ECPay 均為 OMG 旗下子公司。
  - **API 層面**：三家各自運行**完全不同的金流 API**。本 Skill 僅處理 **OMG 自家** FunPoint 全方位金流（domain 為 `funpoint.com.tw`），不涵蓋 OPay 或 ECPay 的 API。整合 OPay 或 ECPay 者請另尋對應 Skill / SDK。
  - **混用的風險**：雖同屬一個集團，三家的 API endpoint、ChoosePayment 合法值、CheckMacValue 編碼細節、webhook 回應字串都不相同。**不可假設「OMG 的做法」= 「ECPay 的做法」= 「OPay 的做法」**。整合前務必比對該家官方文件。
- **BarcodeATM vs BARCODE**：歐買尬官方 `ChoosePayment` 合法值是 `BarcodeATM`（超商快付），實作上是三段 Code39 條碼。**官方沒有 `BARCODE` 這個值**。綠界與歐付寶有 `BARCODE`，但本 Skill 只處理歐買尬，請勿混用
- **CheckMacValue vs HMAC-SHA256**：CheckMacValue 使用的是純 SHA256（非 HMAC），輸入是經 .NET URL encode 後的字串
- **測試環境 vs 沙箱 vs Staging**：本 Skill 統一使用「測試環境」稱呼 OMG 提供之非正式環境
- **正式環境 vs Production vs 線上環境**：本 Skill 統一使用「正式環境」
- **webhook vs callback vs notify**：OMG 官方文件使用 callback / notify，本 Skill 統一使用 **webhook**
