# Reference R0 — 歐買尬全方位金流官方 API 事實表（Single Source of Truth）

> [!IMPORTANT]
> 本檔案是本 repo 所有關於 OMG 歐買尬全方位金流描述的**事實依據**。任何 `guides/`、`references/`、`templates/`、`scripts/` 的內容若與本檔案衝突，**以本檔案為準**。  
> 本檔案的所有資訊皆摘錄自歐買尬全方位金流**公開技術文件**（https://doc.omgpay.com.tw 等官方頁面），並以「事實清單」形式呈現，避免再次解讀歧義。  
> 本 Skill 為**社群非官方**專案，不隸屬歐買尬。官方 AI Skill 由 `https://github.com/omgtwhub/` 維護（若未來有）。

---

## 0. 名詞澄清 / Disambiguation

### 0.1 本 Skill 處理的對象

| 別名 | 對應 | 說明 |
|---|---|---|
| 歐買尬 / OMG / MacroWell / 茂為歐買尬 | ✅ 本 Skill 對象 | 公司全名：**茂為歐買尬數位科技股份有限公司**（統編 70444999）|
| 歐買尬全方位金流 / FunPoint | ✅ 本 Skill 對象 | 歐買尬**自家**經營的金流品牌，domain = `funpoint.com.tw` |
| **歐付寶 / OPay** | ❌ 本 Skill **不涵蓋** | 歐付寶電子支付股份有限公司，domain = `opay.tw` |
| **綠界 / ECPay** | ❌ 本 Skill **不涵蓋** | 綠界科技股份有限公司，domain = `ecpay.com.tw` |

### 0.2 集團關係（依經濟部公司登記公開資料）

過去社群資料常稱「OMG、OPay、ECPay 三家完全無關」，此說法**事實錯誤**。正確情況如下：

- **茂為歐買尬數位科技股份有限公司（統編 70444999）** 為**歐付寶電子支付**與**綠界科技**兩家公司的**法人股東**。
- **歐付寶電子支付股份有限公司**董事長及全體法人董事均由茂為歐買尬指派（董事長林秀芳，以法人董事代表身分就任）。
- **綠界科技股份有限公司**董事長及全體法人董事均由茂為歐買尬指派（董事長林雪慧，以法人董事代表身分就任）。
- 亦即 OPay 與 ECPay 均為 OMG 集團旗下子公司，與 OMG 為母子關係而非互相獨立的平行關係。

### 0.3 API 層面仍然是「三套完全不同的系統」

雖然三家同屬 OMG 集團，但**各自運行完全獨立的金流 API**，彼此**沒有**相容性：

| 項目 | OMG（FunPoint，本 Skill） | ECPay（綠界） | OPay（歐付寶） |
|---|---|---|---|
| Payment domain | `funpoint.com.tw` | `ecpay.com.tw` | `opay.tw` |
| 文件入口 | 歐買尬商家後台 / FunPoint 文件站 | ECPay 官方文件 | OPay 官方文件 |
| `ChoosePayment` 合法值 | 見本檔 §3 | 不同於 OMG，例如 ECPay 有 `BARCODE` 等 | 不同於 OMG |
| CheckMacValue 公式 | SHA256 + .NET URL encoding（見 §8） | 類似但字典表可能不同 | 不同 |
| Webhook 回應 | `1|OK`（純字串，無換行） | 官方另有規範 | 官方另有規範 |

> [!WARNING]
> **集團關係 ≠ API 相容**。請勿假設「OMG 能用的參數」ECPay 或 OPay 也能用，反之亦然。
> 本 Skill 僅處理 OMG 自家 FunPoint 金流（domain `funpoint.com.tw`）。若您要整合的是 ECPay 或 OPay，本 Skill **不適用**，請使用各家官方 Skill / SDK。

### 0.4 引用資料來源

本節「集團關係」依據之資料：

- 經濟部公司登記資料（歐付寶電子支付股份有限公司），最後更新日：2025-08-06
- 經濟部公司登記資料（綠界科技股份有限公司），最後更新日：2026-04-03
- 兩份資料均載明董事長與法人董事之代表法人為統編 70444999 茂為歐買尬數位科技股份有限公司

如上述登記資料於本 SSOT 更新後發生變更（例如股權移轉、董事改選），以經濟部公示資料為準，本 SSOT 應同步更新。

---

## 1. 環境與 Domain / Environments

| 環境 | Payment domain | Webhook 發送來源（加入防火牆白名單） |
|---|---|---|
| 測試 / Test | `payment-stage.funpoint.com.tw` | `postgate-stage.funpoint.com.tw` |
| 正式 / Production | `payment.funpoint.com.tw` | `postgate.funpoint.com.tw` |
| 廠商後台（測試）| `vendor-stage.funpoint.com.tw` | — |

> [!NOTE]
> 官方規定：防火牆**必須綁 domain name**，**不得綁 IP**。  
> 僅支援 HTTPS (443 port)，TLS 1.2 以上。

### 1.1 會員申請與正式環境金鑰取得流程

| 項目 | 連結 |
|---|---|
| 會員註冊頁 | <https://www.funpoint.com.tw/member/register> |
| 會員登入頁 | <https://www.funpoint.com.tw/member/login> |
| 廠商後台（測試環境） | <https://vendor-stage.funpoint.com.tw> |

完成會員註冊並通過審核後，商家可於 FunPoint 商家後台取得正式環境的 `MerchantID`、`HashKey`、`HashIV` 三項金鑰。實際申請資料、審核天數、費率方案與簽約條件以官方公告為準。

> [!WARNING]
> 正式環境金鑰僅允許寫入 `.env`，嚴禁 commit 至任何公開或私有 git 倉庫，也嚴禁寫入本 Skill 的任何範例檔。
> 測試環境公開金鑰（MerchantID=1000031 等）僅供本機整合與 CI 使用，不得用於對外服務。

---

## 2. 核心 API Endpoint 清單 / Endpoint Map

| 用途 / Purpose | 正式環境 Path | 測試環境 Path |
|---|---|---|
| 建立訂單 (AioCheckOut) | `https://payment.funpoint.com.tw/Cashier/AioCheckOut/V5` | `https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5` |
| 查詢訂單 | `https://payment.funpoint.com.tw/Cashier/QueryTradeInfo/V5` | `https://payment-stage.funpoint.com.tw/Cashier/QueryTradeInfo/V5` |
| 信用卡關帳/退刷/取消/放棄 | `https://payment.funpoint.com.tw/CreditDetail/DoAction` | *(測試環境未提供實際授權)* |
| 信用卡單筆明細查詢 | `https://payment.funpoint.com.tw/CreditDetail/QueryTrade/V2` | *(測試環境未提供實際授權)* |
| 定期定額訂單查詢 | `https://payment.funpoint.com.tw/Cashier/QueryCreditCardPeriodInfo` | `https://payment-stage.funpoint.com.tw/Cashier/QueryCreditCardPeriodInfo` |
| 定期定額訂單作業（停用）| `https://payment.funpoint.com.tw/Cashier/CreditCardPeriodAction` | `https://payment-stage.funpoint.com.tw/Cashier/CreditCardPeriodAction` |

**共通請求格式：**

- Method：`POST`
- `Content-Type`：`application/x-www-form-urlencoded`
- `EncryptType`：固定 `1`（SHA256）
- `PaymentType`：固定 `aio`
- 所有請求皆必須附上 `CheckMacValue`

---

## 3. 官方支援的付款方式 / ChoosePayment Values

**完整列表（官方明載的 5 個具名值 + 1 個萬用值）：**

| `ChoosePayment` 值 | 付款方式 | 說明 |
|---|---|---|
| `Credit` | **信用卡**（含銀聯卡，銀聯需申請開通）| 支援一次付清、分期、定期定額、記憶卡號（均需對應參數） |
| `ATM` | **自動櫃員機**（虛擬帳號）| 允許 1–60 天繳費期限，或 10–1440 分鐘（僅中信／一銀／凱基）|
| `CVS` | **超商代碼**（7-ELEVEN、全家等）| 繳費期限預設 7 天，測試環境上限 3 天 |
| `BarcodeATM` | **超商快付** | 注意：**是「超商快付」不是「超商條碼」**，繳費期限以天為單位，預設 7 天 |
| `AFTEE` | **AFTEE 先享後付** | 第三方後支付服務 |
| `ALL` | 不指定 | 由歐買尬付款方式選擇頁面呈現所有可用選項 |

**隱藏付款方式（當 `ChoosePayment=ALL` 時）：**

使用 `IgnorePayment` 參數，多個值以 `#` 分隔。可用值：`Credit`、`ATM`、`CVS`、`BarcodeATM`。

> [!WARNING]
> ❌ **本 Skill 之前錯誤描述**：先前 `templates/merchant-llms-txt/footer-omg.html` 與 `references/api-endpoints.md` 曾將 `BarcodeATM` 誤植為「超商條碼（`BARCODE`）」。**這是錯誤的**。歐買尬官方文件從未出現 `BARCODE` 這個值，只有 `BarcodeATM` 且名稱為「超商快付」。已於 2026-04-12 修正。

> [!CAUTION]
> 官方明定：**「超商代碼」與「超商快付」不得用於販售遊戲點數（卡）、遊戲虛寶**。違反將由歐買尬與超商端終止本項服務權益並追償損失。若您的商家主要商品為遊戲類，請改用其他付款方式。

---

## 4. Credit 付款方式的子參數 / Credit Sub-Parameters

### 4.1 一般信用卡

| 參數 | 說明 |
|---|---|
| `BindingCard` | `1`=使用記憶卡號；`0`=不使用 |
| `MerchantMemberID` | 記憶卡號識別碼（MerchantID + 會員號）。僅支援 Visa / Mastercard / JCB，不支援銀聯卡 |

### 4.2 銀聯卡（需申請開通）

| 參數 | 值 | 說明 |
|---|---|---|
| `UnionPay` | `0` | 消費者於交易頁面可選是否使用銀聯（預設） |
| `UnionPay` | `1` | 強制銀聯卡，直接導至銀聯網站 |
| `UnionPay` | `2` | 隱藏銀聯選項 |

官方限制：銀聯卡**不支援**分期、紅利折抵、記憶卡號功能。

### 4.3 信用卡分期付款

| 參數 | 說明 |
|---|---|
| `CreditInstallment` | 期數：`3`、`6`、`12`、`18`、`24`、`30`（需先申請開通） |

> [!NOTE]
> 目前官方僅提供**玉山信用卡**分期。銀聯卡不支援分期。分期金額由銀行端切分，除不盡的餘額放在第一期（例：1733÷6 = 293, 288, 288, 288, 288, 288）。

### 4.4 信用卡定期定額

| 參數 | 說明 |
|---|---|
| `PeriodAmount` | 每次授權金額（必須等於 `TotalAmount`）|
| `PeriodType` | `D`=日 / `M`=月 / `Y`=年 |
| `Frequency` | 執行頻率 (D≤365 / M≤12 / Y≤1) |
| `ExecTimes` | 總執行次數 (D≤999 / M≤99 / Y≤9) |
| `PeriodReturnURL` | 後續授權結果通知 URL |

第一次授權結果會送到 `ReturnURL`；第二次以後送到 `PeriodReturnURL`。若第一次授權失敗，整筆訂單不進入排程，需重新建立。

---

## 5. 非即時付款方式的子參數（ATM / CVS / BarcodeATM）

### 5.1 ATM 虛擬帳號

| 參數 | 說明 |
|---|---|
| `ExpireDate` | 繳費有效天數（1–60，預設 1）|
| `ExpireMinute` | 繳費有效分鐘數（10–1440，僅中信／一銀／凱基；與 `ExpireDate` 不可同時帶）|
| `PaymentInfoURL` | 取號結果的 Server POST 通知 URL |
| `ClientRedirectURL` | 取號結果的 Client POST URL（與 `ClientBackURL` 互斥）|

### 5.2 CVS 超商代碼

| 參數 | 說明 |
|---|---|
| `StoreExpireDate` | 超商繳費截止分鐘數（正式上限 10080 = 7 天；測試上限 3012 ≈ 3 天）|
| `Desc_1` ~ `Desc_4` | 會顯示在超商繳費平台畫面上的描述 |
| `PaymentInfoURL` | 取號結果 Server POST 通知 URL |

### 5.3 BarcodeATM 超商快付

| 參數 | 說明 |
|---|---|
| `BarcodeATMExpireDate` | 繳費截止天數（上限 7，預設 7）|
| `PaymentInfoURL` | 取號結果 Server POST 通知 URL |

---

## 6. 取號結果通知 / 付款結果通知 Response Rules

### 6.1 取號結果通知 (ATM / CVS / BarcodeATM `PaymentInfoURL`)

- 方式：歐買尬以 Server POST form-data 送達
- 商家必須驗證 `CheckMacValue`
- 驗證成功後，商家必須於 HTTP body **回應純字串 `1|OK`**
- 若回應不正確，歐買尬將每 5–15 分鐘重發，當天重發 4 次

### 6.2 付款結果通知 (`ReturnURL` / `PeriodReturnURL`)

- 方式：歐買尬以 Server POST form-data 送達
- 商家必須驗證 `CheckMacValue`
- 判斷 `RtnCode == 1` 為成功；其他為失敗，不得出貨
- 必須回應純字串 `1|OK`（不要加換行、不要 JSON 化）
- 若商家未正確回應，歐買尬會每 5–15 分鐘重發，當天重發 4 次
- **務必實作冪等性**（見 `guides/05-webhook-idempotency.md`）

### 6.3 `SimulatePaid` 參數

| 值 | 意義 |
|---|---|
| `0` | 實際消費者付款 |
| `1` | **由廠商後台觸發的模擬付款**。即使 `RtnCode=1` 也**不得出貨**，歐買尬不會撥款 |

---

## 7. 退款 / 取消交易 Action 碼

歐買尬信用卡請退款使用 `CreditDetail/DoAction` 端點，`Action` 參數有**四個狀態**：

| Action | 中文 | 適用階段 | 說明 |
|---|---|---|---|
| `C` | 關帳 | 已授權 | 將授權交易送銀行請款 |
| `R` | 退刷 | 要關帳 / 已關帳 | 將已關帳金額退回。可部份退款；分期交易必須全額退刷 |
| `E` | 取消 | 要關帳 | 取消關帳，訂單回到「已授權」狀態 |
| `N` | 放棄 | 已授權 / 已取消 | 放棄授權，當日關帳前執行即不請款 |

**全額退款流程（已授權階段）：**

1. 直接 `Action=N`（放棄），釋放信用卡佔額。

**全額退款流程（要關帳階段）：**

1. `Action=E`（取消）→ 狀態回到已授權
2. `Action=N`（放棄）→ 釋放佔額

**部份退款流程（要關帳階段）：** `Action=R`（退刷）

**已關帳階段退款：** `Action=R`（退刷）

> [!WARNING]
> **每日 20:15 ～ 20:30 不得呼叫 `DoAction` API**。歐買尬每日 20:15 會自動關帳，此時段呼叫會衝突。

> [!IMPORTANT]
> - 訂單須於**授權後 21 天內**完成手動關帳，否則後續無法以 API 方式關帳，需通知客服。  
> - 超過 **90 天**未關帳的訂單，系統會自動執行「放棄」，不作請款。  
> - 若商家帳戶餘額低於退刷金額，將**無法退刷**，需預先儲值。

---

## 8. CheckMacValue 檢查碼機制

### 8.1 計算步驟（SHA256 + .NET-style URL encoding）

```
Step 1: 將所有傳遞參數依英文字母 A→Z 排序，以 & 串接
Step 2: 前綴 HashKey=xxx&   後綴 &HashIV=yyy
Step 3: 對整串字串做 URL encode
Step 4: 轉為小寫
Step 5: 套用 .NET urlencode 替換表（見 8.2）
Step 6: SHA256 hash 產生雜湊值
Step 7: 轉大寫 → CheckMacValue
```

### 8.2 .NET URL Encoding 替換表

PHP `urlencode()` 預設編碼與 .NET `HttpUtility.UrlEncode()` 有差異，需做字元替換：

| 字元 | PHP 編碼 | .NET 編碼（目標） |
|---|---|---|
| `-` | `%2d` | `-` |
| `_` | `%5f` | `_` |
| `.` | `%2e` | `.` |
| `!` | `%21` | `!` |
| `*` | `%2a` | `*` |
| `(` | `%28` | `(` |
| `)` | `%29` | `)` |

（即：上列特殊字元需在 urlencode 後再 str_replace 回原字元）

### 8.3 測試向量

見 `test-vectors/` 目錄下的 Python 與 Node.js 實作與預期輸出。本 Skill 的 Python / Node.js 範例產出的雜湊值**必須與官方文件範例 `AA5842FDA7E55ACEB7118D6353E9822CA6D6FF09A0D1FC129A879DD5CAF93266` 相符**。

---

## 9. 官方明文禁止事項 / Explicit Prohibitions

從官方「前置準備事項」摘錄：

1. ❌ **iframe 內嵌**可能導致交易失敗，建議不要使用
2. ❌ iOS 消費者環境下**不要另開新視窗**
3. ❌ 傳送參數內容**不允許使用 HTML tag**（`<b>`、`<h1>` 等）
4. ❌ **不得將金流資訊存放或顯示於前端網頁**（JavaScript / HTML / CSS）
5. ❌ 連接 port **只支援 HTTPS (443)**，不支援 HTTP
6. ❌ **不支援中文網址**，需使用 punycode 編碼（`中文.tw` → `xn--fiq228c.tw`）
7. ❌ 傳輸參數**不支援特殊符號**（會造成建立訂單錯誤）
8. ❌ **僅支援 TLS 1.2 以上**
9. ❌ 信用卡交易時**不得無故拒絕**持卡人刷卡、不得限制金額、不得將手續費轉嫁
10. ❌ 防火牆**不得綁 IP**，必須綁 domain name (`postgate.funpoint.com.tw` / `postgate-stage.funpoint.com.tw`)
11. ❌ **超商代碼／超商快付不得販售遊戲點數／遊戲虛寶**
12. ❌ `ReturnURL`、`OrderResultURL`、`PaymentInfoURL` **不可設為同一位置**

---

## 10. 官方明文必做事項 / Explicit Requirements

1. ✅ 所有 API 請求以 `POST` + `application/x-www-form-urlencoded` 方式傳送
2. ✅ 主機須做**時間校正**（避免時差造成 API 失敗）
3. ✅ 商家必須檢查收到 webhook 的 `CheckMacValue`
4. ✅ 成功驗證後必須回應 `1|OK`
5. ✅ 必須判斷 `RtnCode == 1` 才處理出貨
6. ✅ 必須判斷 `SimulatePaid` 為 `0`（模擬付款不得出貨）
7. ✅ 商家必須申請開通防火牆，並 mail 商家名稱、`ReturnURL`、domain 至 `pointservice@funpoint.com.tw`
8. ✅ `MerchantTradeNo` 必須唯一（平台商底下所有商家之訂單編號亦不可重覆）

---

## 11. 測試環境公開測試資料 / Public Test Credentials

> 以下為歐買尬官方文件公開的測試環境資料，任何開發者皆可使用：

| 欄位 | 值 |
|---|---|
| MerchantID | `1000031` |
| 後台帳號 | `funstage001` |
| 後台密碼 | `test1234` |
| 身分證後四 / 統編 | `12345678` |
| 廠商後台（測試）URL | `https://vendor-stage.funpoint.com.tw` |
| HashKey | `265flDjIvesceXWM` |
| HashIV | `pOOvhGd1V2pJbjfX` |
| 成功測試卡號 | `4311-9522-2222-2222`（**唯一成功卡號**）|
| 測試安全碼 | `222` |
| 有效月/年 | 任意大於當下的 MM/YYYY |

> [!WARNING]
> 以上為**公開測試環境**資料，不得用於正式環境。正式環境的 MerchantID / HashKey / HashIV 請向歐買尬業務人員申請，並於廠商後台（系統開發管理 → 系統介接設定）中取得。

---

## 12. 參數總覽 Cheat Sheet / Parameter Cheat Sheet

| 類別 | 欄位 | 備註 |
|---|---|---|
| **共通必填** | `MerchantID` `MerchantTradeNo` `MerchantTradeDate` `PaymentType=aio` `TotalAmount` `ReturnURL` `ChoosePayment` `CheckMacValue` `EncryptType=1` | |
| **共通選填** | `StoreID` `TradeDesc` `ItemName` `ClientBackURL` `ItemURL` `Remark` `OrderResultURL` `NeedExtraPaidInfo` `IgnorePayment` `PlatformID` `InvoiceMark=N` `CustomField1~4` `Language` `RiskMerchantMemberID` | |
| **ATM 專屬** | `ExpireDate` `ExpireMinute` `ATMFromBankID` `ATMFromBankAcc` `PaymentInfoURL` `ClientRedirectURL` | |
| **CVS 專屬** | `StoreExpireDate` `Desc_1~4` `PaymentInfoURL` `ClientRedirectURL` | |
| **BarcodeATM 專屬** | `BarcodeATMExpireDate` `PaymentInfoURL` `ClientRedirectURL` | |
| **Credit 專屬** | `BindingCard` `MerchantMemberID` `UnionPay` `CreditInstallment` `PeriodAmount` `PeriodType` `Frequency` `ExecTimes` `PeriodReturnURL` | |

---

## 13. 版本歷程 / Changelog

- **2026-04-12**：首版。依據歐買尬全方位金流官方公開技術文件編寫。修正 `BarcodeATM` 錯誤描述，補齊 AFTEE、UnionPay、分期、定期定額、四種退款 Action、20:15 時段禁呼、21/90 天規則、iframe 禁用、中文網址禁用、TLS 1.2 要求、CheckMacValue 7 步驟等。

---

*本檔案由社群維護。若您發現與官方最新文件有出入，請開 issue 回報。本 Skill 從不聲稱具官方身分。*
