# OMG 金流 (歐買尬第三方支付) 完整串接 Skill | OMG Payment Gateway Complete Integration Skill

> **For AI Assistants** - Claude Code / Cowork Skill for integrating OMG (歐買尬) third-party payment gateway.
> This is a **Taiwan (台灣)** third-party payment service provided by **茂為歐買尬數位科技股份有限公司 / MacroWell OMG Digital Entertainment Co., Ltd.**

---

## Basic Info | 基本資訊

| Item 項目 | Description 說明 |
|-----------|----------------|
| **Payment Gateway** | OMG 金流 (OhMyGod 金流) |
| **Company (中文)** | **茂為歐買尬數位科技股份有限公司** |
| **Company (English)** | **MacroWell OMG Digital Entertainment Co., Ltd.** |
| **Country** | **Taiwan (台灣)** |
| **API Document Version** | V 1.4.9 (2025-11) |
| **API Version** | AioCheckOut V5 |
| **Production URL** | `https://payment.funpoint.com.tw/Cashier/AioCheckOut/V5` |
| **Test/Staging URL** | `https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5` |
| **Submit Method** | HTTP POST (`application/x-www-form-urlencoded`), **NOT JSON** |
| **Encryption** | CheckMacValue (SHA256), **NOT AES** |
| **EncryptType** | Fixed `1` (SHA256) |

---

## Test Credentials | 測試環境帳號

| Item 項目 | Value 值 |
|-----------|---------|
| MerchantID | `1000031` |
| HashKey | `265fIDjIvesceXWM` |
| HashIV | `pOOvhGd1V2pJbjfX` |
| Test Credit Card 測試信用卡 | `4311-9522-2222-2222` |
| CVV 安全碼 | `222` |
| Expiry 有效期限 | Any future month/year 任意未過期月/年 |
| Vendor Backend 廠商後台 | `https://vendor-stage.funpoint.com.tw` |
| Backend Login 後台帳密 | `funstage001` / `test1234` |

---

## Complete API Endpoints | 完整 API 端點一覽

| # | API | URL Path | Method | Description 說明 |
|---|-----|----------|--------|----------------|
| 1 | **AioCheckOut/V5** | `/Cashier/AioCheckOut/V5` | POST (form) | 產生訂單 Create Order |
| 2 | **QueryTradeInfo/V5** | `/Cashier/QueryTradeInfo/V5` | POST (form) | 查詢訂單 Query Trade Info |
| 3 | **QueryCreditCardPeriodInfo** | `/Cashier/QueryCreditCardPeriodInfo` | POST (form) | 查詢定期定額訂單 Query Recurring Info |
| 4 | **CreditCardPeriodAction** | `/Cashier/CreditCardPeriodAction` | POST (form) | 定期定額訂單作業 Recurring Action (Cancel) |
| 5 | **DoAction** | `/CreditDetail/DoAction` | POST (form) | 信用卡請退款 Credit Card Capture/Refund/Cancel/Abandon |
| 6 | **QueryTrade/V2** | `/CreditDetail/QueryTrade/V2` | POST (form) | 查詢信用卡單筆明細 Query Credit Card Transaction Detail |

### Full URL Table | 完整網址對照

| API | Production 正式環境 | Test 測試環境 |
|-----|-----------------|-----------|
| AioCheckOut/V5 | `https://payment.funpoint.com.tw/Cashier/AioCheckOut/V5` | `https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5` |
| QueryTradeInfo/V5 | `https://payment.funpoint.com.tw/Cashier/QueryTradeInfo/V5` | `https://payment-stage.funpoint.com.tw/Cashier/QueryTradeInfo/V5` |
| QueryCreditCardPeriodInfo | `https://payment.funpoint.com.tw/Cashier/QueryCreditCardPeriodInfo` | `https://payment-stage.funpoint.com.tw/Cashier/QueryCreditCardPeriodInfo` |
| CreditCardPeriodAction | `https://payment.funpoint.com.tw/Cashier/CreditCardPeriodAction` | `https://payment-stage.funpoint.com.tw/Cashier/CreditCardPeriodAction` |
| DoAction | `https://payment.funpoint.com.tw/CreditDetail/DoAction` | `https://payment-stage.funpoint.com.tw/CreditDetail/DoAction` |
| QueryTrade/V2 | `https://payment.funpoint.com.tw/CreditDetail/QueryTrade/V2` | `https://payment-stage.funpoint.com.tw/CreditDetail/QueryTrade/V2` |

---

## Payment Flow | 串接流程

### Standard Payment | 一般付款流程

```
1. Merchant builds order params / 商店建立訂單參數
2. Calculate CheckMacValue (SHA256) / 計算 CheckMacValue
3. Form POST to OMG AioCheckOut/V5 / 以 form POST 提交至 OMG
4. User completes payment on OMG page / 使用者在 OMG 頁面完成付款
5. OMG Server POST to ReturnURL (notify merchant) / OMG POST 到 ReturnURL 通知商店
6. OMG Client POST to OrderResultURL (redirect user) / OMG POST 到 OrderResultURL 跳轉使用者
7. Merchant responds "1|OK" / 商店回應 "1|OK" 確認收到
```

### ATM / CVS / BARCODE Payment Flow | ATM/超商付款流程

```
1. Merchant builds order params (ChoosePayment=ATM/CVS/BARCODE)
2. Calculate CheckMacValue (SHA256)
3. Form POST to OMG AioCheckOut/V5
4. User gets payment info (ATM account / CVS code / Barcode)
5. OMG POST payment info to PaymentInfoURL (取號結果通知)
6. OMG POST redirect to ClientRedirectURL (使用者取號後跳轉)
7. User completes payment at ATM/CVS / 使用者至 ATM/超商完成付款
8. OMG POST payment result to ReturnURL / OMG 通知付款結果
9. Merchant responds "1|OK"
```

### Recurring Payment | 定期定額流程

```
1. Build order params with PeriodAmount, PeriodType, Frequency, ExecTimes
2. Calculate CheckMacValue (SHA256)
3. Form POST to OMG AioCheckOut/V5
4. User authorizes first payment / 使用者首次授權付款
5. First result POST to ReturnURL / 首次結果 POST 到 ReturnURL
6. Subsequent charges POST to PeriodReturnURL / 後續扣款結果 POST 到 PeriodReturnURL
7. Always respond "1|OK" / 每次通知都要回應 "1|OK"
```

### Credit Card Post-Authorization Flow | 信用卡請退款流程

```
1. User completes payment / 使用者完成付款
2. Merchant calls DoAction API with Action=C (Capture/關帳)
3. Or Action=R (Refund/退刷), Action=E (Cancel/取消), Action=N (Abandon/放棄)
4. OMG returns result (RtnCode=1 = success)
```

---

## API 1: Create Order (AioCheckOut/V5) | 產生訂單

### Required Parameters | 必填參數

| Parameter 參數 | Type 型態 | Max Length 長度 | Description 說明 |
|--------------|---------|--------------|----------------|
| MerchantID | String | 10 | Merchant ID 商店代號 |
| MerchantTradeNo | String | 20 | Order number (unique, alphanumeric) 商店訂單編號（唯一，英數字） |
| MerchantTradeDate | String | 20 | Trade date `yyyy/MM/dd HH:mm:ss` 交易日期 |
| PaymentType | String | 20 | Fixed: `aio` 固定填 `aio` |
| TotalAmount | Int | — | Amount in NT$ (integer, no decimals) 交易金額（整數，無小數） |
| TradeDesc | String | 200 | Trade description 交易描述 |
| ItemName | String | 400 | Item name (use `#` to separate multiple items) 商品名稱（多項用 `#` 分隔） |
| ReturnURL | String | 200 | Server POST notification URL 伺服器端通知網址 |
| ChoosePayment | String | 20 | Payment method 付款方式: `Credit`, `ATM`, `CVS`, `BARCODE`, `AFTEE`, `ALL` |
| CheckMacValue | String | 64 | SHA256 verification code 檢查碼 |
| EncryptType | Int | 1 | Fixed: `1` (SHA256) |

### Optional Parameters | 選填參數

| Parameter 參數 | Type 型態 | Max Length 長度 | Description 說明 |
|--------------|---------|--------------|----------------|
| StoreID | String | 20 | Sub-store ID 商店旗下店舖代號 |
| OrderResultURL | String | 200 | Client POST redirect URL 使用者端跳轉網址 |
| ClientBackURL | String | 200 | User cancel return URL 取消付款返回網址 |
| ItemURL | String | 200 | Product page URL 商品銷售網址 |
| Remark | String | 100 | Remark 備註 |
| NeedExtraPaidInfo | String | 1 | Need extra payment info 額外付款資訊 `Y`/`N` |
| ChooseSubPayment | String | 20 | Sub-payment type 付款子方式 (see Appendix 附錄3) |
| IgnorePayment | String | 100 | Hide payment methods 隱藏付款方式 (e.g. `ATM#CVS`) |
| PlatformID | String | 10 | Platform merchant ID 特約合作平台商代號 |
| InvoiceMark | String | 1 | Fixed: `N` (電子發票，固定填 N) |
| CustomField1 | String | 50 | Custom field 1 自訂欄位 1 |
| CustomField2 | String | 50 | Custom field 2 自訂欄位 2 |
| CustomField3 | String | 50 | Custom field 3 自訂欄位 3 |
| CustomField4 | String | 50 | Custom field 4 自訂欄位 4 |
| Language | String | 3 | Language 語系: `ENG`, `KOR`, `JPN`, `CHI` (default 預設 CHI) |
| RiskMerchantMemberID | String | 50 | Risk management member ID 風險管理用 |
| DeviceSource | String | 10 | Device source 裝置來源 (leave blank 留空即可) |

### ATM Specific Parameters | ATM 專用參數

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| ExpireDate | Int | ATM expiry days (1-60, default 3) ATM 繳費期限天數 |
| ExpireMinute | Int | ATM expiry minutes (10-1440, default 0=use days) 繳費期限分鐘數 |
| PaymentInfoURL | String | Payment info notification URL 取號結果通知網址 |
| ClientRedirectURL | String | Client redirect after getting info 取號後使用者跳轉網址 |
| ATMFromBankID | String | Payer bank code 繳費者銀行代碼 (for NeedExtraPaidInfo=Y) |
| ATMFromBankAcc | String | Payer bank account 繳費者帳號 (for NeedExtraPaidInfo=Y) |

### CVS Specific Parameters | 超商代碼專用參數

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| StoreExpireDate | Int | Expiry in minutes (default 10080=7days) 繳費期限分鐘數 |
| Desc_1 | String(20) | Description line 1 交易描述 1 |
| Desc_2 | String(20) | Description line 2 交易描述 2 |
| Desc_3 | String(20) | Description line 3 交易描述 3 |
| Desc_4 | String(20) | Description line 4 交易描述 4 |
| PaymentInfoURL | String | Payment info notification URL 取號結果通知網址 |
| ClientRedirectURL | String | Client redirect URL 取號後跳轉網址 |

### BARCODE Specific Parameters | 超商條碼專用參數

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| StoreExpireDate | Int | Expiry in days (1-30, default 7) 繳費期限天數 |
| Desc_1 | String(20) | Description line 1 交易描述 1 |
| Desc_2 | String(20) | Description line 2 交易描述 2 |
| Desc_3 | String(20) | Description line 3 交易描述 3 |
| Desc_4 | String(20) | Description line 4 交易描述 4 |
| PaymentInfoURL | String | Payment info notification URL 取號結果通知網址 |
| ClientRedirectURL | String | Client redirect URL 取號後跳轉網址 |

**Note 注意**: BARCODE returns 3 segment codes (Barcode1, Barcode2, Barcode3) that must be converted to Code39 format for printing.
超商條碼會回傳 3 段條碼 (Barcode1, Barcode2, Barcode3)，需轉為 Code39 格式列印。

### Credit Card Specific Parameters | 信用卡專用參數

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| BindingCard | Int | Binding card 記憶卡號: `0`=No, `1`=Yes (default 0) |
| MerchantMemberID | String | Member ID for card binding 記憶卡號用會員編號 |
| UnionPay | Int | UnionPay 銀聯卡: `0`=No, `1`=Show, `2`=Only UnionPay |

### Credit Card Installment Parameters | 信用卡分期付款參數 (Chapter 5)

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| CreditInstallment | String | Installment periods 分期期數: `3`, `6`, `12`, `18`, `24`, `30` (comma-separated for multiple options) |

**Important 注意**: Installment is only available for E.SUN Bank (玉山銀行) credit card acquiring.
分期付款僅支援玉山銀行信用卡收單。

---

## API 1b: Recurring Payment Parameters | 信用卡定期定額參數 (Chapter 6)

Add these parameters on top of the standard AioCheckOut parameters:
在一般參數之外，額外加上以下參數：

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| PeriodAmount | Int | Amount per period 每期授權金額 |
| PeriodType | String | Period type 週期種類: `D`=Day/天, `M`=Month/月, `Y`=Year/年 |
| Frequency | Int | Frequency 執行頻率 (D:1~365, M:1~12, Y:fixed 1) |
| ExecTimes | Int | Total executions 執行次數 (D:max 999, M:max 99, Y:max 9) |
| PeriodReturnURL | String | Recurring payment notification URL 後續扣款通知網址 |

**Important Notes | 注意事項：**
- `ChoosePayment` must be `Credit` for recurring / 定期定額 ChoosePayment 必須為 `Credit`
- `TotalAmount` = `PeriodAmount` (first period = each period) / 首期金額等於每期金額
- First authorization result → `ReturnURL` / 首次授權結果通知 → ReturnURL
- 2nd period onwards → `PeriodReturnURL` / 第 2 期起通知 → PeriodReturnURL
- Cannot restart after cancellation / 停用後無法重新啟用

---

## Notification: ATM/CVS Payment Info (Chapter 7) | ATM/CVS 取號結果通知

When using ATM, CVS, or BARCODE, OMG will POST payment info to `PaymentInfoURL`.
使用 ATM、CVS、BARCODE 時，OMG 會 POST 取號資訊到 `PaymentInfoURL`。

### ATM Payment Info Return Parameters | ATM 取號回傳參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| MerchantID | Merchant ID 商店代號 |
| MerchantTradeNo | Order number 商店訂單編號 |
| RtnCode | Status code: `2` = ATM 取號成功 |
| RtnMsg | Status message 交易訊息 |
| TradeNo | OMG transaction number 交易編號 |
| TradeAmt | Transaction amount 交易金額 |
| PaymentType | `ATM_FIRST`, `ATM_CHINATRUST`, `ATM_UBOT`, `ATM_KGI` |
| TradeDate | Order creation time 訂單建立時間 |
| CheckMacValue | Verification code 檢查碼 (**must verify 必須驗證**) |
| BankCode | Bank code 銀行代碼 |
| vAccount | Virtual account number 虛擬帳號 |
| ExpireDate | Payment deadline 繳費期限 `yyyy/MM/dd` |

### CVS Payment Info Return Parameters | CVS 取號回傳參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| MerchantID | Merchant ID 商店代號 |
| MerchantTradeNo | Order number 商店訂單編號 |
| RtnCode | Status code: `10100073` = CVS 取號成功 |
| RtnMsg | Status message (e.g. "Get CVS Code Succeeded.") |
| TradeNo | OMG transaction number 交易編號 |
| TradeAmt | Transaction amount 交易金額 |
| PaymentType | `CVS_CVS`, `CVS_FAMILY`, `CVS_IBON` |
| TradeDate | Order creation time 訂單建立時間 |
| CheckMacValue | Verification code 檢查碼 |
| PaymentNo | CVS payment code 超商繳費代碼 |
| ExpireDate | Payment deadline 繳費期限 `yyyy/MM/dd HH:mm:ss` |

### BARCODE Payment Info Return Parameters | BARCODE 取號回傳參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| MerchantID | Merchant ID 商店代號 |
| MerchantTradeNo | Order number 商店訂單編號 |
| RtnCode | Status code: `10100073` = 取號成功 |
| TradeNo | OMG transaction number 交易編號 |
| TradeAmt | Transaction amount 交易金額 |
| PaymentType | Payment type 付款方式 |
| TradeDate | Order creation time 訂單建立時間 |
| CheckMacValue | Verification code 檢查碼 |
| Barcode1 | Barcode segment 1 條碼第一段 |
| Barcode2 | Barcode segment 2 條碼第二段 |
| Barcode3 | Barcode segment 3 條碼第三段 |
| ExpireDate | Payment deadline 繳費期限 |

**CRITICAL**: Must respond with plain text `1|OK` after receiving notification.
**重要**：收到通知後必須回應純文字 `1|OK`。

---

## Notification: Payment Result (Chapter 8) | 付款結果通知

### ReturnURL (Server POST) Parameters | 伺服器端回傳參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| MerchantID | Merchant ID 商店代號 |
| MerchantTradeNo | Order number 商店訂單編號 |
| RtnCode | Status code: **`1` = Success 成功** |
| RtnMsg | Status message 交易訊息 |
| TradeNo | OMG transaction number OMG 交易編號 |
| TradeAmt | Transaction amount 交易金額 |
| PaymentDate | Payment time 付款時間 |
| PaymentType | Payment method 付款方式 (see Appendix 4 附錄4) |
| TradeDate | Order creation time 訂單建立時間 |
| SimulatePaid | Simulated payment 模擬付款: `0`=Real, `1`=Simulated |
| CheckMacValue | Verification code (**must verify** 必須驗證) |
| CustomField1~4 | Custom fields 自訂欄位 (if provided) |

### OrderResultURL (Client POST) | 使用者端跳轉

Same parameters as ReturnURL. This is for redirecting the user's browser after payment.
參數同 ReturnURL，用於付款後跳轉使用者瀏覽器。

**Note**: The actual payment result should always be based on ReturnURL server notification, NOT OrderResultURL.
**注意**：實際付款結果應以 ReturnURL 伺服器通知為準，不以 OrderResultURL 為準。

### CRITICAL: Response Format | 重要：回應格式

After receiving the ReturnURL notification, you **MUST respond with plain text `1|OK`**, otherwise OMG will keep resending the notification.
收到通知後**必須回應純文字 `1|OK`**，否則 OMG 會持續重送通知。

```python
# FastAPI example
from fastapi.responses import PlainTextResponse

@app.post("/payment/notify")
async def notify(request: Request):
    form = await request.form()
    data = dict(form)
    # Verify CheckMacValue... / 驗證 CheckMacValue...
    # Process order... / 處理訂單...
    return PlainTextResponse("1|OK")
```

---

## API 2: Query Trade Info (QueryTradeInfo/V5) | 查詢訂單 (Chapter 9)

### Request Parameters | 請求參數

| Parameter 參數 | Type 型態 | Max Length 長度 | Description 說明 |
|--------------|---------|--------------|----------------|
| MerchantID | String | 10 | Merchant ID 商店代號 |
| MerchantTradeNo | String | 20 | Order number 商店訂單編號 |
| TimeStamp | String | — | Unix timestamp (must be within 3 minutes of current time) Unix 時間戳（需在當前時間前後 3 分鐘內） |
| CheckMacValue | String | 64 | SHA256 verification code 檢查碼 |

### Response Parameters | 回應參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| MerchantID | Merchant ID 商店代號 |
| MerchantTradeNo | Order number 商店訂單編號 |
| TradeNo | OMG transaction number OMG 交易編號 |
| TradeAmt | Transaction amount 交易金額 |
| PaymentDate | Payment time 付款時間 |
| PaymentType | Payment method 付款方式 |
| HandlingCharge | Handling charge 手續費 |
| PaymentTypeChargeFee | Payment type charge fee 付款方式手續費 |
| TradeDate | Order creation time 訂單建立時間 |
| TradeStatus | Trade status 交易狀態: `0`=Unpaid/未付款, `1`=Paid/已付款, `10200095`=Cancelled/取消 |
| ItemName | Item name 商品名稱 |
| CheckMacValue | Verification code 檢查碼 |
| CustomField1~4 | Custom fields 自訂欄位 |

**Important 重要**: `TimeStamp` must be Unix timestamp and be within 3 minutes of current time, or the query will be rejected.
`TimeStamp` 必須為 Unix 時間戳且需在當前時間前後 3 分鐘內，否則查詢會被拒絕。

---

## API 3: Extra Return Parameters (NeedExtraPaidInfo=Y) | 額外回傳參數 (Chapter 10)

When `NeedExtraPaidInfo` is set to `Y`, the following extra parameters will be returned in the notification:
當 `NeedExtraPaidInfo` 設為 `Y` 時，通知會額外回傳以下參數：

### Credit Card Extra Parameters | 信用卡額外參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| card4no | Last 4 digits of card 卡號後 4 碼 |
| card6no | First 6 digits of card 卡號前 6 碼 |
| red_dan | Bonus point deduction flag 紅利折抵旗標 |
| red_de_amt | Bonus deduction amount 紅利折抵金額 |
| red_ok_amt | Bonus actual deduction 紅利實際折抵金額 |
| red_yet | Remaining bonus points 剩餘紅利 |
| stage | Installment periods 分期期數 |
| stast | First installment amount 首期金額 |
| staed | Subsequent installment amount 後續各期金額 |
| eci | 3D verification code 3D 驗證碼 (5/6=3D, 7/2=Non-3D) |
| gwsr | Authorization code 授權碼 |
| process_date | Processing date 處理日期 |
| auth_code | Bank authorization code 銀行授權碼 |
| amount | Authorization amount 授權金額 |
| PayFrom | Payment source 付款來源 |
| UnionPay | UnionPay flag 銀聯卡旗標: `0`=Non-UnionPay, `1`=UnionPay |

### ATM Extra Parameters | ATM 額外參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| ATMAccBank | Payer bank code 繳款銀行代碼 |
| ATMAccNo | Payer account (masked) 繳款帳號（遮蔽） |

### CVS Extra Parameters | 超商額外參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| CVSStoreID | Store ID 超商店號 |
| CVSStoreName | Store name 超商店名 |

### Recurring Extra Parameters | 定期定額額外參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| PeriodType | Period type 週期種類 |
| Frequency | Frequency 執行頻率 |
| ExecTimes | Total executions 執行次數 |
| PeriodAmount | Period amount 每期金額 |
| TotalSuccessTimes | Total success times 已成功授權次數 |
| TotalSuccessAmount | Total success amount 已成功授權金額 |

---

## API 4: Query Recurring Payment Info (QueryCreditCardPeriodInfo) | 查詢定期定額 (Chapter 11)

### Request Parameters | 請求參數

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| MerchantID | String(10) | Merchant ID 商店代號 |
| MerchantTradeNo | String(20) | Original order number 原商店訂單編號 |
| TimeStamp | String | Unix timestamp (3-min validation) Unix 時間戳 |
| CheckMacValue | String(64) | SHA256 verification code 檢查碼 |

### Response (JSON) | 回應（JSON 格式）

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| MerchantID | Merchant ID 商店代號 |
| MerchantTradeNo | Order number 訂單編號 |
| TradeNo | OMG transaction number 交易編號 |
| RtnCode | Status code (1=success) 狀態碼 |
| PeriodType | Period type 週期種類 (D/M/Y) |
| Frequency | Frequency 執行頻率 |
| ExecTimes | Total executions 執行次數 |
| PeriodAmount | Period amount 每期金額 |
| amount | Total amount 總金額 |
| gwsr | Authorization code 授權碼 |
| process_date | Processing date 處理日期 |
| auth_code | Bank authorization code 銀行授權碼 |
| card4no | Last 4 digits of card 卡號後 4 碼 |
| card6no | First 6 digits of card 卡號前 6 碼 |
| TotalSuccessTimes | Total success count 已成功次數 |
| TotalSuccessAmount | Total success amount 已成功金額 |
| ExecStatus | Execution status 執行狀態: `0`=Cancelled/已停用, `1`=Executing/執行中, `2`=Completed/已完成 |
| ExecLog | Execution log array 執行紀錄陣列 (JSON array) |

### ExecLog Array Element | ExecLog 陣列元素

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| RtnCode | Status code 狀態碼 (1=success) |
| RtnMsg | Status message 狀態訊息 |
| amount | Amount for this period 本期金額 |
| gwsr | Authorization code 授權碼 |
| process_date | Processing date 處理日期 |
| auth_code | Bank authorization code 銀行授權碼 |
| TradeNo | Transaction number 交易編號 |

---

## API 5: Recurring Payment Action (CreditCardPeriodAction) | 定期定額訂單作業 (Chapter 12)

### Request Parameters | 請求參數

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| MerchantID | String(10) | Merchant ID 商店代號 |
| MerchantTradeNo | String(20) | Original order number 原商店訂單編號 |
| Action | String | Fixed: `Cancel` 固定填 `Cancel`（停用） |
| CheckMacValue | String(64) | SHA256 verification code 檢查碼 |

### Response | 回應

Returns `RtnCode=1` if successful. 成功回傳 `RtnCode=1`。

**CRITICAL WARNING | 重要警告**: Once cancelled, recurring payment **CANNOT be restarted**. This is irreversible.
停用後**無法重新啟用**，此操作不可逆。

---

## API 6: Credit Card DoAction (CreditDetail/DoAction) | 信用卡請退款 (Chapter 14)

### Endpoint | 端點

| Environment 環境 | URL |
|-----------------|-----|
| Production 正式 | `https://payment.funpoint.com.tw/CreditDetail/DoAction` |
| Test 測試 | `https://payment-stage.funpoint.com.tw/CreditDetail/DoAction` |

### Request Parameters | 請求參數

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| MerchantID | String(10) | Merchant ID 商店代號 |
| MerchantTradeNo | String(20) | Original order number 原商店訂單編號 |
| TradeNo | String(20) | OMG transaction number OMG 交易編號 |
| Action | String | Action type 動作類型 (see below) |
| TotalAmount | Int | Action amount 操作金額 |
| CheckMacValue | String(64) | SHA256 verification code 檢查碼 |

### Action Types | 動作類型

| Action | Chinese 中文 | English | Description 說明 |
|--------|-----------|---------|----------------|
| `C` | 關帳 | Capture | Capture/close the transaction 關帳請款 |
| `R` | 退刷 | Refund | Refund the transaction 退刷退款 |
| `E` | 取消 | Cancel/Void | Cancel the authorization 取消授權 |
| `N` | 放棄 | Abandon | Abandon the transaction 放棄交易 |

### Response Parameters | 回應參數

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| MerchantID | Merchant ID 商店代號 |
| MerchantTradeNo | Order number 訂單編號 |
| TradeNo | OMG transaction number 交易編號 |
| RtnCode | Status code 狀態碼: `1` = Success 成功 |
| RtnMsg | Status message 狀態訊息 |

### Action Rules | 動作規則

```
Authorization (授權) → Capture/Close (關帳 C) → Refund (退刷 R)
Authorization (授權) → Cancel (取消 E)
Authorization (授權) → Abandon (放棄 N)
```

- **Capture (C/關帳)**: Must be done before settlement. Amount can be <= original amount.
  關帳必須在撥款前完成，金額可小於等於原授權金額。
- **Refund (R/退刷)**: Can only be done after Capture. Amount can be <= captured amount.
  退刷只能在關帳後執行，金額可小於等於關帳金額。
- **Cancel (E/取消)**: Cancel authorization before Capture. Full amount only.
  取消授權，僅能在關帳前執行，且為全額取消。
- **Abandon (N/放棄)**: Abandon the transaction entirely.
  放棄整筆交易。

---

## API 7: Query Credit Card Transaction Detail (QueryTrade/V2) | 查詢信用卡單筆明細 (Chapter 15)

### Endpoint | 端點

| Environment 環境 | URL |
|-----------------|-----|
| Production 正式 | `https://payment.funpoint.com.tw/CreditDetail/QueryTrade/V2` |
| Test 測試 | `https://payment-stage.funpoint.com.tw/CreditDetail/QueryTrade/V2` |

### Request Parameters | 請求參數

| Parameter 參數 | Type 型態 | Description 說明 |
|--------------|---------|----------------|
| MerchantID | String(10) | Merchant ID 商店代號 |
| CreditRefundId | String(20) | Credit refund ID 信用卡退款編號 |
| CreditAmount | Int | Credit amount 信用卡金額 |
| CreditCheckCode | String(64) | Credit check code (SHA256 of MerchantID+CreditRefundId+CreditAmount+HashKey+HashIV) |

### Response (JSON) | 回應（JSON 格式）

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| RtnMsg | Return message 回傳訊息 |
| RtnValue | JSON object with details 明細 JSON 物件 |

### RtnValue Object | RtnValue 物件

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| TradeID | Trade ID 交易編號 |
| amount | Original amount 原始金額 |
| clsamt | Captured amount 關帳金額 |
| authtime | Authorization time 授權時間 |
| status | Status 狀態: `要關帳`=Pending capture, `已關帳`=Captured, `要退款`=Pending refund, `已退款`=Refunded |
| close_data | Array of close/refund records 關帳/退款紀錄陣列 |

### close_data Array Element | close_data 陣列元素

| Parameter 參數 | Description 說明 |
|--------------|----------------|
| status | Record status 紀錄狀態 |
| sno | Serial number 序號 |
| amount | Amount 金額 |
| datetime | Date time 日期時間 |

---

## CheckMacValue Calculation | CheckMacValue 計算方式 (Chapter 13)

**This is the most critical part.** It must be 100% correct or OMG will reject the transaction.
**這是最關鍵的部分，必須完全正確，否則 OMG 會拒絕交易。**

### Algorithm Steps | 演算法步驟

```
Step 1: Sort all params (exclude CheckMacValue) by key name A→Z (case-insensitive)
        將所有參數（不含 CheckMacValue）依參數名稱 A→Z 排序（不分大小寫）

Step 2: Join as key=value with & separator
        組成 key=value 以 & 串接

Step 3: Prepend HashKey=xxx& and append &HashIV=xxx
        前方加上 HashKey=xxx&，後方加上 &HashIV=xxx

Step 4: URL encode the entire string
        整串做 URL encode

Step 5: Convert to lowercase
        轉小寫

Step 6: Replace .NET URL encode special characters (see table below)
        替換 .NET URL encode 特殊字元（見下表）

Step 7: SHA256 hash
        做 SHA256 雜湊

Step 8: Convert to uppercase
        轉大寫
```

### .NET URL Encode Replacement Table | .NET URL Encode 替換表

These replacements are **MANDATORY**. Without them, CheckMacValue will be wrong.
這些替換**必須執行**，否則 CheckMacValue 會計算錯誤。

| URL Encode Value | Replace With 替換為 |
|------------------|-------------------|
| `%2d` | `-` |
| `%5f` | `_` |
| `%2e` | `.` |
| `%21` | `!` |
| `%2a` | `*` |
| `%28` | `(` |
| `%29` | `)` |

**Additional Note 補充**: Space `%20` is replaced with `+` in .NET URL encoding, but Python's `urllib.parse.quote` uses `%20` (which is correct for this context since we do the .NET replacements separately).

### Python Implementation | Python 實作

```python
import hashlib
from urllib.parse import quote

DOTNET_REPLACEMENTS = {
    "%2d": "-", "%5f": "_", "%2e": ".",
    "%21": "!", "%2a": "*", "%28": "(", "%29": ")",
}

def generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    """Generate OMG CheckMacValue (SHA256). 產生 OMG 金流 CheckMacValue."""
    # 1. Remove CheckMacValue / 移除 CheckMacValue
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue"}

    # 2. Sort by key A-Z (case-insensitive) / 依 key A-Z 排序
    sorted_keys = sorted(filtered.keys(), key=lambda k: k.lower())

    # 3. Join as key=value / 組成 key=value 字串
    param_str = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)

    # 4. Prepend HashKey, append HashIV / 加上 HashKey/HashIV
    raw = f"HashKey={hash_key}&{param_str}&HashIV={hash_iv}"

    # 5. URL encode + lowercase / URL encode + 轉小寫
    encoded = quote(raw, safe="").lower()

    # 6. .NET replacements / .NET 替換
    for old, new in DOTNET_REPLACEMENTS.items():
        encoded = encoded.replace(old, new)

    # 7+8. SHA256 → uppercase / SHA256 → 大寫
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()
```

### Node.js Implementation | Node.js 實作

```javascript
const crypto = require('crypto');

const DOTNET_REPLACEMENTS = {
  '%2d': '-', '%5f': '_', '%2e': '.',
  '%21': '!', '%2a': '*', '%28': '(', '%29': ')',
};

function generateCheckMacValue(params, hashKey, hashIV) {
  const filtered = Object.entries(params)
    .filter(([k]) => k !== 'CheckMacValue');

  filtered.sort(([a], [b]) => a.toLowerCase().localeCompare(b.toLowerCase()));

  const paramStr = filtered.map(([k, v]) => `${k}=${v}`).join('&');
  let raw = `HashKey=${hashKey}&${paramStr}&HashIV=${hashIV}`;
  let encoded = encodeURIComponent(raw).toLowerCase();

  for (const [old, rep] of Object.entries(DOTNET_REPLACEMENTS)) {
    encoded = encoded.replaceAll(old, rep);
  }

  return crypto.createHash('sha256').update(encoded).digest('hex').toUpperCase();
}
```

### PHP Implementation | PHP 實作

```php
function generateCheckMacValue($params, $hashKey, $hashIV) {
    // Remove CheckMacValue
    unset($params['CheckMacValue']);

    // Sort by key A-Z (case-insensitive)
    uksort($params, function($a, $b) {
        return strcasecmp($a, $b);
    });

    // Join as key=value
    $paramStr = '';
    foreach ($params as $key => $value) {
        $paramStr .= "&{$key}={$value}";
    }

    // Prepend HashKey, append HashIV
    $raw = "HashKey={$hashKey}{$paramStr}&HashIV={$hashIV}";

    // URL encode + lowercase
    $encoded = strtolower(urlencode($raw));

    // .NET replacements
    $encoded = str_replace('%2d', '-', $encoded);
    $encoded = str_replace('%5f', '_', $encoded);
    $encoded = str_replace('%2e', '.', $encoded);
    $encoded = str_replace('%21', '!', $encoded);
    $encoded = str_replace('%2a', '*', $encoded);
    $encoded = str_replace('%28', '(', $encoded);
    $encoded = str_replace('%29', ')', $encoded);

    // SHA256 + uppercase
    return strtoupper(hash('sha256', $encoded));
}
```

### .NET/C# Implementation | .NET/C# 實作 (Appendix 6)

```csharp
// .NET uses HttpUtility.UrlEncode which handles .NET URL encoding natively
// .NET 使用 HttpUtility.UrlEncode，原生處理 .NET URL 編碼
private string BuildCheckMacValue(string parameters, int encryptType = 0)
{
    string szCheckMacValue = String.Empty;
    // 產生檢查碼
    szCheckMacValue = String.Format("HashKey={0}{1}&HashIV={2}",
        this.HashKey, parameters, this.HashIV);
    szCheckMacValue = HttpUtility.UrlEncode(szCheckMacValue).ToLower();
    if (encryptType == 1)
    {
        // SHA256 編碼
        szCheckMacValue = SHA256Encoder.Encrypt(szCheckMacValue);
    }
    else
    {
        // MD5 編碼 (deprecated, use SHA256)
        szCheckMacValue = MD5Encoder.Encrypt(szCheckMacValue);
    }
    return szCheckMacValue;
}
```

**Note**: .NET's `HttpUtility.UrlEncode()` natively handles .NET URL encoding, so no manual replacements (`%2d`→`-`, etc.) are needed in C#. Python/Node.js/PHP must do these replacements manually.
**.NET 備註**：C# 的 `HttpUtility.UrlEncode()` 原生處理 .NET URL 編碼，因此 C# 不需手動替換。Python/Node.js/PHP 則必須手動執行替換。

---

## Supported Payment Methods | 支援的付款方式 (Appendix 3)

### ChoosePayment Values | ChoosePayment 值

| ChoosePayment | Description 說明 |
|---------------|----------------|
| `Credit` | Credit card (one-time, installment, recurring) 信用卡 |
| `ATM` | ATM virtual account ATM 虛擬帳號 |
| `CVS` | CVS payment code 超商代碼繳款 |
| `BARCODE` | CVS barcode 超商條碼繳款 |
| `AFTEE` | AFTEE buy now pay later 先享後付 |
| `ALL` | Show all available methods 顯示所有可用付款方式 |

### ChooseSubPayment Values | ChooseSubPayment 子方式

| Payment 付款方式 | SubPayment 子方式 | Description 說明 |
|-------------|---------------|----------------|
| ATM | `FIRST` | 第一銀行 ATM |
| ATM | `CHINATRUST` | 中國信託 ATM |
| ATM | `UBOT` | 聯邦 ATM |
| ATM | `KGI` | 凱基 ATM |
| Credit | *(none)* | 信用卡 MasterCard/JCB/VISA |
| CVS | `CVS` | 超商代碼繳款 |
| CVS | `FAMILY` | 全家便利商店代碼繳費 |
| CVS | `IBON` | 7-11 便利超商代碼繳款 |
| AFTEE | `AFTEE` | AFTEE 先享後付 |

### Return PaymentType Values | 回傳付款方式 (Appendix 4)

| PaymentType | Description 說明 |
|-------------|----------------|
| `ATM_FIRST` | 第一銀行 ATM |
| `ATM_CHINATRUST` | 中國信託 ATM |
| `ATM_UBOT` | 聯邦 ATM |
| `ATM_KGI` | 凱基 ATM |
| `Credit_CreditCard` | 信用卡 |
| `CVS_CVS` | 超商代碼繳款 |
| `CVS_FAMILY` | 全家便利商店代碼繳費 |
| `CVS_IBON` | 7-11 便利超商代碼繳費 |
| `AFTEE_AFTEE` | AFTEE 先享後付 |

---

## Quick Start: Test Environment Setup | 快速開始：測試環境建置

### Step 1: Environment Variables | 設定環境變數

```env
# OMG Payment Settings / OMG 金流設定
OMG_MERCHANT_ID=1000031
OMG_HASH_KEY=265fIDjIvesceXWM
OMG_HASH_IV=pOOvhGd1V2pJbjfX
OMG_PRODUCTION=false

# Your server URL (must be publicly accessible)
# 你的伺服器網址（必須是公開可存取的）
BASE_URL=https://your-domain.com
```

### Step 2: Make Your Server Publicly Accessible | 讓伺服器公開可存取

For local development, use ngrok to create a public tunnel:
本地開發時，使用 ngrok 建立公開通道：

```bash
# Install ngrok / 安裝 ngrok
# Visit https://ngrok.com/ to download

# Start your server / 啟動伺服器
uvicorn app:app --host 0.0.0.0 --port 8000

# In another terminal, create tunnel / 在另一個終端建立通道
ngrok http 8000

# Use the ngrok URL (e.g. https://abc123.ngrok.io) as BASE_URL
# 使用 ngrok 網址作為 BASE_URL
```

### Step 3: Test Credit Card Payment | 測試信用卡付款

```
Test Card 測試卡號: 4311-9522-2222-2222
CVV 安全碼: 222
Expiry 有效期限: Any future month/year (e.g. 12/28)
```

### Step 4: Verify in Vendor Backend | 在廠商後台驗證

```
URL: https://vendor-stage.funpoint.com.tw
Login 帳號: funstage001
Password 密碼: test1234
Path 路徑: 系統開發管理 → 交易狀態代碼查詢
```

### Step 5: Test All Payment Methods | 測試所有付款方式

1. **Credit Card 信用卡**: Use test card above / 使用上方測試卡號
2. **ATM**: Will generate virtual account / 會產生虛擬帳號（測試環境無需實際轉帳）
3. **CVS 超商代碼**: Will generate payment code / 會產生繳費代碼
4. **BARCODE 超商條碼**: Will generate 3-segment barcode / 會產生三段條碼

### Step 6: Test Notification (ReturnURL) | 測試通知

In test environment, use "Simulated Payment" (模擬付款) from vendor backend to trigger ReturnURL notification.
測試環境中，可從廠商後台使用「模擬付款」功能觸發 ReturnURL 通知。

When `SimulatePaid=1`, it's a simulated payment (not real money). Your system should handle this appropriately.
當 `SimulatePaid=1` 時為模擬付款（非真實金額），系統應適當處理。

---

## Error Codes Reference | 交易訊息代碼 (Appendix 2)

Error codes are continuously updated. For the latest error code list, please visit the vendor backend:
錯誤代碼持續新增中，最新代碼請至廠商管理後台查詢：

- **Production 正式**: `https://vendor.funpoint.com.tw` → 系統開發管理 → 交易狀態代碼查詢
- **Test 測試**: `https://vendor-stage.funpoint.com.tw` → 系統開發管理 → 交易狀態代碼查詢
- **Login 登入**: `funstage001` / `test1234` (test environment)

### Common RtnCode Values | 常見狀態碼

| RtnCode | Meaning 說明 |
|---------|------------|
| `1` | 交易成功 Transaction Success |
| `2` | ATM 取號成功 ATM Virtual Account Generated |
| `10100073` | CVS/BARCODE 取號成功 CVS/BARCODE Code Generated |
| `10200095` | 訂單已取消 Order Cancelled |
| `10200047` | CheckMacValue 驗證失敗 CheckMacValue Verification Failed |
| `10200058` | 訂單編號重複 Duplicate MerchantTradeNo |
| `10200069` | 交易金額有誤 Invalid TotalAmount |

**Note 注意**: The complete error code table is maintained in the vendor backend as codes are frequently added. Always check the latest codes there.
完整錯誤代碼表維護在廠商後台，因代碼持續新增，請務必至後台查詢最新代碼。

---

## Common Errors | 常見錯誤排除

### CheckMacValue Calculation Error | CheckMacValue 計算錯誤

Most common issue. Please verify: 最常見的問題，請確認：
1. Sorting is correct (A-Z by key name, case-insensitive) / 排序正確（不分大小寫）
2. HashKey/HashIV prepend/append positions are correct / 前後位置正確
3. .NET URL encode replacements are applied **after** URL encoding / URL encode **後**有做 .NET 替換
4. Final result is uppercase / 最後轉大寫
5. `EncryptType` is set to `1` (SHA256) / EncryptType 填 `1`
6. URL encode uses `quote(raw, safe="")` not `quote_plus` / 使用 `quote(raw, safe="")` 而非 `quote_plus`

### Duplicate Order Number | 訂單編號重複

`MerchantTradeNo` must be unique. Max 20 chars, alphanumeric only.
必須唯一，最長 20 碼，僅限英數字。
Suggested format: `prefix + timestamp + random` / 建議格式：前綴 + 時間戳 + 隨機碼

### ReturnURL Not Receiving Notifications | ReturnURL 沒收到通知

1. ReturnURL must be publicly accessible (not localhost) / 必須是公開網址
2. For testing, use ngrok or deploy to cloud / 測試用 ngrok 或部署到雲端
3. Must respond `1|OK` / 必須回應 `1|OK`
4. Check if OMG is retrying (check logs) / 檢查 OMG 是否在重送

### PeriodReturnURL Not Receiving 2nd Period | 定期定額第二期沒收到通知

Ensure `PeriodReturnURL` is set correctly and is different from `ReturnURL`.
確認 PeriodReturnURL 設定正確，且與 ReturnURL 不同。

### QueryTradeInfo TimeStamp Error | 查詢訂單時間戳錯誤

`TimeStamp` must be Unix timestamp and within 3 minutes of server time.
TimeStamp 必須為 Unix 時間戳且在伺服器時間前後 3 分鐘內。

### DoAction Failed | 信用卡請退款失敗

Check action sequence: 檢查動作順序：
- Capture (C) must be done before Refund (R) / 關帳 (C) 必須在退刷 (R) 之前
- Cancel (E) must be done before Capture / 取消 (E) 必須在關帳之前
- Amount must be <= authorized/captured amount / 金額不能超過授權/關帳金額

---

## Debug Guide | 除錯指南

### How to Debug CheckMacValue Errors | 如何除錯 CheckMacValue 錯誤

If you get a CheckMacValue error, follow this step-by-step debugging process:
如果遇到 CheckMacValue 錯誤，請按以下步驟除錯：

```python
# Debug: Print each step of CheckMacValue calculation
# 除錯：印出 CheckMacValue 計算每一步

def debug_check_mac_value(params: dict, hash_key: str, hash_iv: str):
    from urllib.parse import quote

    # Step 1: Filter out CheckMacValue
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue"}
    print(f"Step 1 - Filtered params count: {len(filtered)}")

    # Step 2: Sort keys
    sorted_keys = sorted(filtered.keys(), key=lambda k: k.lower())
    print(f"Step 2 - Sorted keys: {sorted_keys}")

    # Step 3: Join
    param_str = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
    print(f"Step 3 - Param string: {param_str[:100]}...")

    # Step 4: Add HashKey/HashIV
    raw = f"HashKey={hash_key}&{param_str}&HashIV={hash_iv}"
    print(f"Step 4 - Raw string: {raw[:100]}...")

    # Step 5: URL encode + lowercase
    encoded = quote(raw, safe="").lower()
    print(f"Step 5 - Encoded: {encoded[:100]}...")

    # Step 6: .NET replacements
    replacements = {"%2d": "-", "%5f": "_", "%2e": ".", "%21": "!", "%2a": "*", "%28": "(", "%29": ")"}
    for old, new in replacements.items():
        encoded = encoded.replace(old, new)
    print(f"Step 6 - After .NET replacements: {encoded[:100]}...")

    # Step 7+8: SHA256 + uppercase
    import hashlib
    result = hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()
    print(f"Step 7+8 - Final CheckMacValue: {result}")
    return result
```

### How to Debug Notification Issues | 如何除錯通知問題

```python
# Add logging to your notification endpoint
# 在通知端點加入日誌記錄

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("omg_payment")

@app.post("/notify")
async def payment_notify(request: Request):
    form = await request.form()
    data = dict(form)

    # Log all received data / 記錄所有收到的資料
    logger.info(f"Received notification: {data}")

    # Verify CheckMacValue
    if not verify_check_mac_value(data):
        logger.error(f"CheckMacValue FAILED!")
        logger.error(f"Received: {data.get('CheckMacValue')}")
        logger.error(f"Expected: {generate_check_mac_value(data)}")
        return PlainTextResponse("0|CheckMacValue Error")

    rtn_code = data.get("RtnCode", "")
    rtn_msg = data.get("RtnMsg", "")
    simulate = data.get("SimulatePaid", "0")

    logger.info(f"RtnCode={rtn_code}, RtnMsg={rtn_msg}, SimulatePaid={simulate}")

    if rtn_code == "1":
        logger.info("Payment SUCCESS")
    elif rtn_code == "2":
        logger.info("ATM Virtual Account Generated")
    elif rtn_code == "10100073":
        logger.info("CVS/BARCODE Code Generated")
    else:
        logger.warning(f"Unknown/Error RtnCode: {rtn_code} - {rtn_msg}")
        # Look up error code at vendor backend:
        # https://vendor-stage.funpoint.com.tw → 系統開發管理 → 交易狀態代碼查詢

    return PlainTextResponse("1|OK")
```

### How to Debug DoAction Errors | 如何除錯信用卡請退款錯誤

Common DoAction errors and solutions:
常見 DoAction 錯誤和解決方案：

| Error Scenario 錯誤場景 | Cause 原因 | Solution 解決方案 |
|----------------------|----------|----------------|
| Action=C failed | 已經關帳 Already captured | Check status with QueryTrade/V2 first 先用 QueryTrade/V2 查詢狀態 |
| Action=R failed | 尚未關帳 Not yet captured | Must Capture (C) before Refund (R) 必須先關帳再退刷 |
| Action=E failed | 已經關帳 Already captured | Can only Cancel before Capture 只能在關帳前取消 |
| Amount error | 金額超過授權金額 Amount exceeds authorization | Check original amount 檢查原始金額 |
| TradeNo not found | 交易編號不存在 TradeNo doesn't exist | Verify with QueryTradeInfo/V5 先查詢訂單 |

### RtnCode Quick Reference | RtnCode 快速參考

| RtnCode | Context 情境 | Meaning 說明 |
|---------|-----------|-------------|
| `1` | ReturnURL / DoAction | 成功 Success |
| `2` | PaymentInfoURL (ATM) | ATM 取號成功 |
| `10100073` | PaymentInfoURL (CVS/BARCODE) | 超商取號成功 |
| `10200047` | Any | CheckMacValue 驗證失敗 |
| `10200058` | AioCheckOut | 訂單編號重複 Duplicate order |
| `10200069` | AioCheckOut | 金額有誤 Invalid amount |
| `10200095` | QueryTradeInfo | 已取消 Cancelled |
| Other | Any | 查詢廠商後台 Check vendor backend |

---

## Self-Check Table | 自行檢測表 (Chapter 16)

Before going live, verify: 上線前請確認：

1. ✅ CheckMacValue calculation correct / CheckMacValue 計算正確
2. ✅ ReturnURL returns "1|OK" / ReturnURL 回應 "1|OK"
3. ✅ Verify CheckMacValue on callback / 回調時驗證 CheckMacValue
4. ✅ Handle duplicate notifications (idempotent) / 處理重複通知（冪等性）
5. ✅ MerchantTradeNo unique for each order / 每筆訂單 MerchantTradeNo 唯一
6. ✅ Payment result based on ReturnURL, not OrderResultURL / 付款結果以 ReturnURL 為準
7. ✅ Handle SimulatePaid flag / 處理模擬付款旗標
8. ✅ Test all payment methods / 測試所有付款方式
9. ✅ Switch to production URL and credentials / 切換正式環境網址和憑證

---

## Glossary | 關鍵字一覽 (Appendix 1)

| Term 名稱 | Description 說明 |
|---------|----------------|
| 特店 | 提供歐買尬金流付款服務給消費者付款交易的賣家系統 |
| 特約店家 | 與歐買尬金流有特別專案簽訂合約的賣家特店 |
| 專案合作的平台商 | 與歐買尬金流有特別專案簽訂合約的平台廠商 |
| AioCheckOut | 歐買尬金流提供的 API 服務 |
| 歐買尬金流訂單 | 歐買尬金流確立特店訂單資料無誤後，於歐買尬金流產生特店的歐買尬金流訂單 |
| 檢查碼 | 傳送交易資料由檢查碼機制產生後的交易資料檢核字串 |
| OTP | 信用卡交易簡訊驗證服務 |

---

## Production Migration Guide | 正式環境遷移指南

When moving from test to production, follow these steps:
從測試環境切換到正式環境時，請按以下步驟：

### Checklist | 遷移清單

1. **Apply for production credentials 申請正式環境帳號**
   - Contact OMG to get your production MerchantID, HashKey, HashIV
   - 聯繫歐買尬取得正式環境 MerchantID、HashKey、HashIV

2. **Update all URLs 更新所有網址**
   ```
   Test 測試:  payment-stage.funpoint.com.tw
   Prod 正式:  payment.funpoint.com.tw
   ```

3. **Update credentials 更新憑證**
   ```env
   OMG_MERCHANT_ID=your_production_id
   OMG_HASH_KEY=your_production_hash_key
   OMG_HASH_IV=your_production_hash_iv
   OMG_PRODUCTION=true
   ```

4. **Ensure HTTPS 確保使用 HTTPS**
   - All callback URLs (ReturnURL, OrderResultURL, PaymentInfoURL, etc.) must use HTTPS in production
   - 所有回調網址在正式環境必須使用 HTTPS

5. **Remove SimulatePaid handling 移除模擬付款處理**
   - In production, SimulatePaid should always be `0`
   - 正式環境中 SimulatePaid 應為 `0`

6. **Test with real small amount 用小額實際測試**
   - Make a real NT$1 or minimum amount transaction to verify
   - 用最小金額做一筆真實交易驗證

---

## Important Developer Notes | 重要開發者注意事項

### Amount Rules | 金額規則

- Currency: **NTD only** (新台幣)
- Amount must be **positive integer** (no decimals) / 金額必須為正整數（無小數）
- Minimum amount varies by payment method / 最低金額依付款方式而異
- For recurring payments: `TotalAmount` must equal `PeriodAmount`

### Idempotency | 冪等性處理

OMG may send the same notification multiple times (e.g., if your server didn't respond `1|OK` in time).
OMG 可能會重複發送相同通知（例如你的伺服器未及時回應 `1|OK`）。

```python
# Example: Idempotent notification handling
# 範例：冪等性通知處理

@app.post("/notify")
async def payment_notify(request: Request):
    form = await request.form()
    data = dict(form)
    order_no = data.get("MerchantTradeNo", "")

    # Check if already processed / 檢查是否已處理過
    if await is_order_already_processed(order_no):
        return PlainTextResponse("1|OK")  # Already processed, just acknowledge

    # Verify and process / 驗證並處理
    if verify_check_mac_value(data) and data.get("RtnCode") == "1":
        await update_order_status(order_no, "paid")

    return PlainTextResponse("1|OK")  # Always respond 1|OK
```

### Webhook Response Time | 回調回應時間

- OMG expects a response within a reasonable time (typically < 10 seconds)
- If no `1|OK` response, OMG will **retry** the notification
- Always respond `1|OK` even if processing fails (handle errors asynchronously)
- OMG 預期在合理時間內收到回應（通常 < 10 秒）
- 若未收到 `1|OK`，OMG 會**重送**通知
- 即使處理失敗也要回應 `1|OK`（異步處理錯誤）

### MerchantTradeNo Best Practices | 訂單編號最佳實踐

```python
import secrets
from datetime import datetime

def generate_order_no(prefix: str = "O") -> str:
    """Generate unique order number (max 20 chars).
    產生唯一訂單編號（最長 20 碼）."""
    timestamp = datetime.now().strftime("%y%m%d%H%M%S")  # 12 chars
    random_part = secrets.token_hex(3).upper()  # 6 chars
    return f"{prefix}{timestamp}{random_part}"[:20]  # Total ≤ 20 chars

# Examples:
# O2501151030A1B2C3  (one-time payment)
# R2501151030D4E5F6  (recurring payment)
```

Rules:
- Max 20 characters / 最長 20 碼
- Alphanumeric only / 僅限英數字
- Must be globally unique / 必須全域唯一
- Cannot reuse even for failed orders / 即使失敗的訂單也不能重用

### Encoding Requirements | 編碼要求

- All data must be **UTF-8** encoded / 所有資料必須為 UTF-8 編碼
- ItemName supports Chinese characters / ItemName 支援中文
- TradeDesc supports Chinese characters / TradeDesc 支援中文
- URL parameters in ReturnURL etc. must be properly encoded / 回調網址中的參數需正確編碼

### Express.js (Node.js) Integration Example | Express.js 整合範例

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.urlencoded({ extended: true }));

const CONFIG = {
  merchantId: '1000031',
  hashKey: '265fIDjIvesceXWM',
  hashIV: 'pOOvhGd1V2pJbjfX',
  aioUrl: 'https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5',
};

const DOTNET_REPLACEMENTS = {
  '%2d': '-', '%5f': '_', '%2e': '.',
  '%21': '!', '%2a': '*', '%28': '(', '%29': ')',
};

function generateCheckMacValue(params) {
  const filtered = Object.entries(params).filter(([k]) => k !== 'CheckMacValue');
  filtered.sort(([a], [b]) => a.toLowerCase().localeCompare(b.toLowerCase()));
  const paramStr = filtered.map(([k, v]) => `${k}=${v}`).join('&');
  let raw = `HashKey=${CONFIG.hashKey}&${paramStr}&HashIV=${CONFIG.hashIV}`;
  let encoded = encodeURIComponent(raw).toLowerCase();
  for (const [old, rep] of Object.entries(DOTNET_REPLACEMENTS)) {
    encoded = encoded.replaceAll(old, rep);
  }
  return crypto.createHash('sha256').update(encoded).digest('hex').toUpperCase();
}

// Payment notification endpoint
app.post('/notify', (req, res) => {
  const data = req.body;
  const received = data.CheckMacValue;
  const expected = generateCheckMacValue(data);

  if (received !== expected) {
    console.error('CheckMacValue verification failed');
    return res.type('text/plain').send('0|Error');
  }

  if (data.RtnCode === '1') {
    console.log(`Payment success: ${data.MerchantTradeNo}`);
    // Update order status...
  }

  res.type('text/plain').send('1|OK');
});

app.listen(8000, () => console.log('Server running on port 8000'));
```

---

## Python SDK Wrapper | Python 完整封裝類

This section provides a complete `OMGPaymentClient` class that simplifies integrating the Taiwan e-commerce payment gateway into your application. The SDK handles all 6 OMG payment APIs, manages test/production environment switching, and includes built-in retry logic with exponential backoff for reliability.

以下提供完整的 `OMGPaymentClient` 類別，簡化 OMG 金流串接流程。SDK 涵蓋所有 6 個 API，自動環境切換，內含重試機制。

```python
import hashlib
import hmac
import requests
import time
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OMGPaymentClient:
    """
    Complete OMG Payment Gateway (歐買尬金流) SDK wrapper for Taiwan e-commerce payment integration.
    Supports credit card payments, ATM virtual accounts, convenience store payments, and recurring subscriptions.

    台灣第三方支付 OMG 金流完整封裝 SDK，支持信用卡付款、ATM虛擬帳號、超商代碼繳款、定期定額扣款。
    """

    def __init__(self, merchant_id: str, hash_key: str, hash_iv: str, production: bool = False):
        """
        Initialize OMG Payment Client

        Args:
            merchant_id: Your merchant ID
            hash_key: Your hash key for CheckMacValue
            hash_iv: Your hash IV for CheckMacValue
            production: Use production API (True) or test API (False)
        """
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.production = production

        self.base_url = "https://payment.funpoint.com.tw" if production else "https://payment-stage.funpoint.com.tw"
        self.aio_checkout_url = f"{self.base_url}/Cashier/AioCheckOut/V5"
        self.query_trade_info_url = f"{self.base_url}/Cashier/QueryTradeInfo/V5"
        self.query_credit_card_period_url = f"{self.base_url}/Cashier/QueryCreditCardPeriodInfo"
        self.credit_card_period_action_url = f"{self.base_url}/Cashier/CreditCardPeriodAction"
        self.do_action_url = f"{self.base_url}/Cashier/DoAction"
        self.query_trade_v2_url = f"{self.base_url}/Cashier/QueryTrade/V2"

        self.max_retries = 3
        self.retry_backoff_factor = 2

        logger.info(f"OMGPaymentClient initialized (production={production}, merchant_id={merchant_id})")

    def _calculate_check_mac_value(self, data: Dict[str, Any]) -> str:
        """
        Calculate CheckMacValue for payment API security (SHA256).

        這是 OMG 金流串接的核心安全驗證機制，使用 SHA256 演算法。
        """
        # Sort parameters (case-insensitive)
        sorted_params = sorted(data.items(), key=lambda x: x[0].lower())

        # Build parameter string
        param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])

        # Add HashIV at the beginning and HashKey at the end
        mac_str = f"HashIV={self.hash_iv}&{param_str}&HashKey={self.hash_key}"

        # SHA256 hash and uppercase
        check_mac = hashlib.sha256(mac_str.encode('utf-8')).hexdigest().upper()

        return check_mac

    def _make_request(self, url: str, data: Dict[str, Any], max_retries: Optional[int] = None) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and exponential backoff.
        """
        if max_retries is None:
            max_retries = self.max_retries

        for attempt in range(max_retries):
            try:
                response = requests.post(url, data=data, timeout=10)
                response.raise_for_status()

                # Parse response
                if 'json' in response.headers.get('content-type', ''):
                    return response.json()
                else:
                    # Form-encoded or custom format
                    return self._parse_response(response.text)

            except requests.RequestException as e:
                wait_time = self.retry_backoff_factor ** attempt
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")

                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {max_retries} attempts")
                    raise

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse various response formats from OMG APIs"""
        result = {}
        for item in response_text.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                result[key] = value
        return result

    def create_order(self,
                    trade_no: str,
                    amount: int,
                    description: str,
                    return_url: str,
                    notify_url: str,
                    client_back_url: str,
                    payment_type: str = "aio",
                    choose_payment: Optional[str] = None,
                    items: Optional[list] = None,
                    **kwargs) -> Dict[str, Any]:
        """
        Create a payment order using AioCheckOut/V5 API.

        Supports credit card payments, ATM virtual accounts, and convenience store codes.
        支持信用卡付款、ATM虛擬帳號、超商代碼繳款等多種付款方式。

        Args:
            trade_no: Unique merchant trade number
            amount: Total amount (in TWD)
            description: Order description
            return_url: Customer return URL after payment
            notify_url: Server notification URL
            client_back_url: Return URL if customer cancels
            payment_type: "aio" (default), "Credit" (credit card only), etc.
            choose_payment: Specific payment method (e.g., "Credit", "ATM", "BARCODE")
            items: List of items (optional details)
            **kwargs: Additional parameters (CustomField1, PeriodAmount, etc.)

        Returns:
            Dict with RtnCode, RtnMsg, and payment form HTML or redirect URL
        """
        data = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': trade_no,
            'MerchantTradeDate': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'PaymentType': payment_type,
            'TotalAmount': amount,
            'TradeDesc': description,
            'ItemName': items[0]['name'] if items else description,
            'ReturnURL': return_url,
            'NotifyURL': notify_url,
            'ClientBackURL': client_back_url,
            'ChoosePayment': choose_payment or 'ALL',
            'EncryptType': 1,
        }

        # Add optional parameters
        if kwargs:
            data.update(kwargs)

        # Calculate CheckMacValue
        data['CheckMacValue'] = self._calculate_check_mac_value(data)

        logger.info(f"Creating order: {trade_no}, amount: {amount}")

        response = self._make_request(self.aio_checkout_url, data)
        return response

    def query_trade(self, trade_no: str) -> Dict[str, Any]:
        """
        Query payment transaction status using QueryTradeInfo/V5 API.

        用 QueryTradeInfo/V5 查詢線上付款交易狀態。

        Args:
            trade_no: Merchant trade number

        Returns:
            Dict with transaction details (RtnCode, TradeStatus, PaymentType, etc.)
        """
        data = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': trade_no,
            'TimeStamp': int(time.time()),
        }

        data['CheckMacValue'] = self._calculate_check_mac_value(data)

        logger.info(f"Querying trade: {trade_no}")

        response = self._make_request(self.query_trade_info_url, data)
        return response

    def query_recurring(self, trade_no: str) -> Dict[str, Any]:
        """
        Query recurring/subscription payment status using QueryCreditCardPeriodInfo.

        查詢定期定額扣款狀態，支持信用卡週期付款訂閱。

        Args:
            trade_no: Original merchant trade number

        Returns:
            Dict with recurring payment details
        """
        data = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': trade_no,
            'TimeStamp': int(time.time()),
        }

        data['CheckMacValue'] = self._calculate_check_mac_value(data)

        logger.info(f"Querying recurring payment: {trade_no}")

        response = self._make_request(self.query_credit_card_period_url, data)
        return response

    def cancel_recurring(self, trade_no: str, action: str = "C") -> Dict[str, Any]:
        """
        Cancel or suspend recurring subscription using CreditCardPeriodAction.

        取消或暫停信用卡定期定額扣款訂閱。

        Args:
            trade_no: Original merchant trade number
            action: "C" (Cancel), "R" (Resume), "E" (End contract), "N" (Change amount)

        Returns:
            Dict with operation result
        """
        data = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': trade_no,
            'TimeStamp': int(time.time()),
            'Action': action,
        }

        data['CheckMacValue'] = self._calculate_check_mac_value(data)

        logger.info(f"Recurring payment action: {trade_no}, action={action}")

        response = self._make_request(self.credit_card_period_action_url, data)
        return response

    def do_action(self, trade_no: str, action: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform transaction actions (Capture, Refund, Void, etc.) using DoAction API.

        執行交易動作：取消授權 (C)、退款 (R)、取消退款 (E)、取消交易 (N)。

        Args:
            trade_no: Original merchant trade number
            action: "C" (Cancel auth), "R" (Refund), "E" (Cancel refund), "N" (Void transaction)
            amount: Amount for the action (required for Refund/Cancel Refund)

        Returns:
            Dict with action result
        """
        data = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': trade_no,
            'TimeStamp': int(time.time()),
            'Action': action,
        }

        if amount is not None:
            data['TotalAmount'] = amount

        data['CheckMacValue'] = self._calculate_check_mac_value(data)

        logger.info(f"DoAction: {trade_no}, action={action}")

        response = self._make_request(self.do_action_url, data)
        return response

    def query_credit_detail(self, trade_no: str) -> Dict[str, Any]:
        """
        Query credit card transaction details using QueryTrade/V2 API.

        用 QueryTrade/V2 查詢信用卡交易詳情（退款退刷資訊）。

        Args:
            trade_no: Merchant trade number

        Returns:
            Dict with detailed transaction info
        """
        data = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': trade_no,
            'TimeStamp': int(time.time()),
        }

        data['CheckMacValue'] = self._calculate_check_mac_value(data)

        logger.info(f"Querying credit detail: {trade_no}")

        response = self._make_request(self.query_trade_v2_url, data)
        return response

    def verify_notification(self, callback_data: Dict[str, str]) -> bool:
        """
        Verify CheckMacValue from payment notification callback.

        驗證支付通知回調的 CheckMacValue，確保資料完整性。

        Args:
            callback_data: All parameters from OMG callback (including CheckMacValue)

        Returns:
            True if verification passes, False otherwise
        """
        received_mac = callback_data.get('CheckMacValue', '')

        # Create copy without CheckMacValue
        verify_data = {k: v for k, v in callback_data.items() if k != 'CheckMacValue'}

        # Calculate expected CheckMacValue
        expected_mac = self._calculate_check_mac_value(verify_data)

        is_valid = received_mac.upper() == expected_mac.upper()

        if is_valid:
            logger.info(f"Notification verified: {verify_data.get('MerchantTradeNo')}")
        else:
            logger.error(f"Notification verification failed: {verify_data.get('MerchantTradeNo')}")

        return is_valid


# Example usage:
if __name__ == "__main__":
    # Initialize client for test environment
    client = OMGPaymentClient(
        merchant_id="1000031",
        hash_key="265fIDjIvesceXWM",
        hash_iv="pOOvhGd1V2pJbjfX",
        production=False
    )

    # Create order
    result = client.create_order(
        trade_no="TEST2024030401",
        amount=1000,
        description="Test Payment Order",
        return_url="https://example.com/return",
        notify_url="https://example.com/notify",
        client_back_url="https://example.com/cancel",
        choose_payment="Credit"
    )
    print(f"Order created: {result}")

    # Query trade status
    # status = client.query_trade("TEST2024030401")
    # print(f"Trade status: {status}")

    # Verify callback
    # callback = {...callback params from OMG...}
    # if client.verify_notification(callback):
    #     print("Payment confirmed!")
```

---

## Admin Dashboard Generation | 管理後台生成指南

When building an e-commerce admin dashboard for OMG payment gateway integration, you need several key features to manage Taiwan payment transactions, monitor payment methods, and handle refunds efficiently.

建立 OMG 金流管理後台時，需要完整的交易管理、支付方式分析、退款管理等功能。

### Admin Dashboard Features Required | 管理後台必需功能

1. **Transaction List with Search/Filter** - Display all online payment transactions with search by trade number, date range, payment status, payment method
2. **Transaction Detail View** - Show full transaction info: amount, payment method (credit card vs ATM vs convenience store), timestamps, refund history
3. **Revenue Analytics** - Daily/monthly revenue charts, transaction count trends, average transaction value
4. **Payment Method Distribution** - Pie chart showing credit card vs ATM virtual account vs convenience store code distribution for financial analytics
5. **Refund Management** - Process refunds (退款退刷), track refund status, generate refund reports
6. **Recurring Payment Management** - For subscription-based payment models, manage active subscriptions, suspend/resume periodic deductions
7. **Real-time Notification Log** - Monitor webhook delivery status from OMG payment APIs, view callback logs
8. **Settlement Reports** - Track settlement cycles, view deposited amounts, reconcile with OMG backend

### Instruction for AI | AI 指令範本

When a user asks you to build an admin dashboard for OMG payment gateway integration, follow this template:

```
用戶要求：建立 OMG 金流管理後台

AI 應該做：
1. 使用 React/Next.js 創建應用
2. 實現上述 8 個功能
3. 串接 OMG Payment API (QueryTradeInfo/V5, QueryCreditCardPeriodInfo, DoAction 等)
4. 使用 Python/Node.js 後端處理 API 請求和 CheckMacValue 驗證
5. 使用資料庫 (PostgreSQL/MongoDB) 存儲交易快取
6. 實現即時更新和錯誤通知
```

### React Dashboard Component Example | React 儀表板元件範例

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const OMGPaymentDashboard = () => {
  const [transactions, setTransactions] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterPaymentStatus, setFilterPaymentStatus] = useState('all');
  const [filterMethod, setFilterMethod] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  useEffect(() => {
    fetchTransactions();
    fetchRevenueData();
    fetchPaymentMethods();
  }, [filterPaymentStatus, filterMethod, dateRange]);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/transactions', {
        params: {
          status: filterPaymentStatus,
          method: filterMethod,
          startDate: dateRange.start,
          endDate: dateRange.end,
        },
      });
      setTransactions(response.data);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    }
    setLoading(false);
  };

  const fetchRevenueData = async () => {
    try {
      const response = await axios.get('/api/revenue-analytics');
      setRevenueData(response.data);
    } catch (error) {
      console.error('Failed to fetch revenue data:', error);
    }
  };

  const fetchPaymentMethods = async () => {
    try {
      const response = await axios.get('/api/payment-methods-distribution');
      setPaymentMethods(response.data);
    } catch (error) {
      console.error('Failed to fetch payment methods:', error);
    }
  };

  const handleRefund = async (tradeNo, amount) => {
    if (window.confirm(`確認退款 ${amount} 元？`)) {
      try {
        await axios.post('/api/refund', { tradeNo, amount });
        alert('退款請求已提交');
        fetchTransactions();
      } catch (error) {
        alert(`退款失敗: ${error.message}`);
      }
    }
  };

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c'];

  return (
    <div className="dashboard-container">
      <h1>OMG Payment Admin Dashboard | OMG 金流管理後台</h1>

      {/* Filter Section */}
      <div className="filter-section">
        <input
          type="date"
          value={dateRange.start}
          onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
          placeholder="開始日期"
        />
        <input
          type="date"
          value={dateRange.end}
          onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
          placeholder="結束日期"
        />
        <select value={filterPaymentStatus} onChange={(e) => setFilterPaymentStatus(e.target.value)}>
          <option value="all">All Status</option>
          <option value="1">Success (成功)</option>
          <option value="0">Pending (待驗證)</option>
        </select>
        <select value={filterMethod} onChange={(e) => setFilterMethod(e.target.value)}>
          <option value="all">All Methods</option>
          <option value="Credit">Credit Card (信用卡)</option>
          <option value="ATM">ATM Virtual Account (ATM虛擬帳號)</option>
          <option value="BARCODE">Convenience Store (超商代碼)</option>
        </select>
      </div>

      {/* Revenue Chart */}
      <div className="chart-section">
        <h2>Daily Revenue | 日營收</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={revenueData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="amount" stroke="#8884d8" name="Amount (金額)" />
            <Line type="monotone" dataKey="transactions" stroke="#82ca9d" name="Transactions (交易數)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Payment Method Distribution */}
      <div className="chart-section">
        <h2>Payment Method Distribution | 付款方式分布</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={paymentMethods} cx="50%" cy="50%" label dataKey="value">
              {paymentMethods.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Transactions Table */}
      <div className="table-section">
        <h2>Recent Transactions | 最近交易</h2>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <table className="transactions-table">
            <thead>
              <tr>
                <th>Trade No (交易號)</th>
                <th>Amount (金額)</th>
                <th>Method (付款方式)</th>
                <th>Status (狀態)</th>
                <th>Date (日期)</th>
                <th>Action (操作)</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.tradeNo}>
                  <td>{tx.tradeNo}</td>
                  <td>TWD {tx.amount}</td>
                  <td>{tx.paymentMethod}</td>
                  <td>{tx.status === '1' ? 'Success ✓' : 'Pending'}</td>
                  <td>{new Date(tx.tradeDate).toLocaleString('zh-TW')}</td>
                  <td>
                    <button onClick={() => handleRefund(tx.tradeNo, tx.amount)}>
                      Refund (退款)
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default OMGPaymentDashboard;
```

---

## Integration Monitoring | 串接監控

Monitoring your OMG payment gateway integration ensures payment reliability and provides early warning for potential issues. This section provides monitoring strategies, health checks, and alert rules for production environments handling Taiwan e-commerce transactions.

監控 OMG 金流串接狀態對確保付款可靠性至關重要。以下提供監控策略、健康檢查、告警機制。

### Health Check Endpoint | 健康檢查端點

```python
from datetime import datetime, timedelta
import requests
import json

class OMGHealthMonitor:
    """
    Monitor OMG payment gateway health and integration status.

    監控 OMG 金流健康狀態和串接完整性。
    """

    def __init__(self, merchant_id: str, hash_key: str, hash_iv: str):
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.test_url = "https://payment-stage.funpoint.com.tw"
        self.prod_url = "https://payment.funpoint.com.tw"

    def check_api_connectivity(self, production: bool = False) -> Dict[str, Any]:
        """
        Ping OMG test/production API to verify connectivity.

        檢查 API 連線狀態。
        """
        url = self.prod_url if production else self.test_url

        try:
            response = requests.get(url, timeout=5)
            return {
                'status': 'healthy' if response.status_code == 200 else 'degraded',
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'timestamp': datetime.now().isoformat(),
            }
        except requests.RequestException as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
            }

    def calculate_transaction_success_rate(self, transactions: list) -> float:
        """
        Calculate success rate from transaction list.

        計算交易成功率。
        """
        if not transactions:
            return 100.0

        successful = sum(1 for tx in transactions if tx.get('status') == '1')
        return (successful / len(transactions)) * 100

    def check_success_rate(self, db_connection) -> Dict[str, Any]:
        """
        Check transaction success rate for last 1 hour.

        檢查過去 1 小時的交易成功率。
        """
        one_hour_ago = datetime.now() - timedelta(hours=1)

        # Query transactions from your database
        transactions = db_connection.query(
            f"SELECT * FROM transactions WHERE created_at > '{one_hour_ago}'"
        )

        success_rate = self.calculate_transaction_success_rate(transactions)

        return {
            'success_rate': success_rate,
            'total_transactions': len(transactions),
            'failed_transactions': len(transactions) - sum(1 for tx in transactions if tx.get('status') == '1'),
            'threshold': 95.0,
            'alert': success_rate < 95.0,
            'timestamp': datetime.now().isoformat(),
        }

    def check_webhook_delivery(self, db_connection) -> Dict[str, Any]:
        """
        Monitor webhook delivery status from OMG callback notifications.

        監控 OMG 回調通知狀態。
        """
        one_hour_ago = datetime.now() - timedelta(hours=1)

        # Query webhook logs
        callbacks = db_connection.query(
            f"SELECT * FROM webhook_logs WHERE created_at > '{one_hour_ago}'"
        )

        successful_callbacks = sum(1 for cb in callbacks if cb.get('verified'))
        failed_callbacks = len(callbacks) - successful_callbacks

        return {
            'total_callbacks': len(callbacks),
            'successful': successful_callbacks,
            'failed': failed_callbacks,
            'success_rate': (successful_callbacks / len(callbacks) * 100) if callbacks else 100,
            'timestamp': datetime.now().isoformat(),
        }

    def generate_health_report(self, db_connection, production: bool = False) -> Dict[str, Any]:
        """
        Generate comprehensive health report for OMG payment integration.

        產生完整的健康檢查報告。
        """
        api_health = self.check_api_connectivity(production=production)
        success_rate = self.check_success_rate(db_connection)
        webhook_health = self.check_webhook_delivery(db_connection)

        # Determine overall health
        overall_health = 'healthy'
        if api_health['status'] != 'healthy' or success_rate['alert'] or webhook_health['success_rate'] < 95:
            overall_health = 'unhealthy'
        elif api_health['status'] == 'degraded':
            overall_health = 'degraded'

        return {
            'overall_status': overall_health,
            'api_connectivity': api_health,
            'transaction_success': success_rate,
            'webhook_delivery': webhook_health,
            'timestamp': datetime.now().isoformat(),
            'environment': 'production' if production else 'test',
        }

# Example: Flask monitoring endpoint
from flask import Flask, jsonify

app = Flask(__name__)
monitor = OMGHealthMonitor("1000031", "265fIDjIvesceXWM", "pOOvhGd1V2pJbjfX")

@app.route('/health/omg-payment', methods=['GET'])
def omg_payment_health():
    """
    Health check endpoint for OMG payment integration monitoring.

    用於監控系統的 OMG 金流健康檢查端點。
    """
    # Get database connection (pseudocode)
    db = get_db_connection()

    report = monitor.generate_health_report(db, production=False)

    # Return appropriate HTTP status based on health
    status_code = 200 if report['overall_status'] == 'healthy' else 503

    return jsonify(report), status_code
```

### Alert Rules and Thresholds | 告警規則和閾值

```python
class AlertRule:
    """
    Define alert rules for OMG payment monitoring.

    定義 OMG 金流監控告警規則。
    """

    RULES = {
        'success_rate_critical': {
            'metric': 'transaction_success_rate',
            'threshold': 90,
            'condition': '<',
            'severity': 'critical',
            'message': 'Transaction success rate dropped below 90%',
        },
        'success_rate_warning': {
            'metric': 'transaction_success_rate',
            'threshold': 95,
            'condition': '<',
            'severity': 'warning',
            'message': 'Transaction success rate dropped below 95%',
        },
        'api_response_time': {
            'metric': 'api_response_time_ms',
            'threshold': 5000,
            'condition': '>',
            'severity': 'warning',
            'message': 'API response time exceeded 5 seconds',
        },
        'webhook_delivery_failure': {
            'metric': 'webhook_failure_rate',
            'threshold': 5,
            'condition': '>',
            'severity': 'warning',
            'message': 'Webhook delivery failure rate exceeded 5%',
        },
        'api_connectivity': {
            'metric': 'api_status',
            'threshold': 'healthy',
            'condition': '!=',
            'severity': 'critical',
            'message': 'OMG API connectivity issue detected',
        },
    }

    @staticmethod
    def evaluate_alert(metric_name: str, metric_value: float) -> Optional[str]:
        """
        Check if metric triggers any alert rule.

        評估指標是否觸發告警規則。
        """
        rule = AlertRule.RULES.get(metric_name)

        if not rule:
            return None

        threshold = rule['threshold']
        condition = rule['condition']

        triggered = False
        if condition == '<':
            triggered = metric_value < threshold
        elif condition == '>':
            triggered = metric_value > threshold
        elif condition == '!=':
            triggered = metric_value != threshold

        return rule['message'] if triggered else None
```

### Prometheus Metrics Example | Prometheus 指標範例

```python
from prometheus_client import Counter, Gauge, Histogram

# Define metrics for OMG payment integration
omg_transactions_total = Counter(
    'omg_transactions_total',
    'Total OMG payment transactions',
    ['status', 'payment_method']
)

omg_transaction_amount = Gauge(
    'omg_transaction_amount_twd',
    'Total transaction amount in TWD',
    ['payment_method']
)

omg_api_response_time = Histogram(
    'omg_api_response_time_seconds',
    'OMG API response time',
    ['api_name']
)

omg_webhook_deliveries = Counter(
    'omg_webhook_deliveries_total',
    'OMG webhook delivery attempts',
    ['status']
)

# Example usage
def record_transaction(amount: int, payment_method: str, success: bool):
    """Record transaction metrics"""
    status = 'success' if success else 'failed'
    omg_transactions_total.labels(status=status, payment_method=payment_method).inc()
    omg_transaction_amount.labels(payment_method=payment_method).set(amount)
```

---

## Automated Error Diagnosis | 自動錯誤診斷

When integrating OMG payment gateway for Taiwan e-commerce platforms, developers often encounter various error codes, CheckMacValue validation failures, and network issues. This section provides automated diagnostic tools to quickly identify and resolve problems.

在整合 OMG 金流時，開發者常遇到各種錯誤碼、CheckMacValue 驗證失敗、網路連線問題。本節提供自動診斷工具快速識別和解決問題。

```python
import re
import hashlib
import socket
from typing import Tuple, Dict, Any
from datetime import datetime

class ErrorDiagnosis:
    """
    Automated error diagnosis for OMG payment gateway integration.

    OMG 金流串接自動錯誤診斷工具。
    """

    # Error code mapping with solutions
    ERROR_CODES = {
        '0': {
            'message': 'System error',
            'cause': 'Unknown error from OMG system',
            'solutions': [
                'Check OMG status page: https://www.funpoint.com.tw/',
                'Verify API endpoint URL is correct',
                'Enable detailed logging to see server response',
            ]
        },
        '1': {
            'message': 'Success',
            'cause': 'Transaction completed successfully',
            'solutions': ['No action needed']
        },
        '-1': {
            'message': 'Merchant not found',
            'cause': 'MerchantID does not exist or is inactive',
            'solutions': [
                'Verify MerchantID is correct',
                'Confirm merchant account is active in OMG backend',
                'Check if using test MerchantID in production',
            ]
        },
        '-2': {
            'message': 'Parameter error',
            'cause': 'Missing or invalid parameters in request',
            'solutions': [
                'Verify all required parameters are provided',
                'Check parameter data types and formats',
                'Ensure date format is YYYY/MM/DD HH:MM:SS',
                'Verify amount is integer (no decimals)',
            ]
        },
        '-3': {
            'message': 'Invalid CheckMacValue',
            'cause': 'CheckMacValue validation failed - most common error',
            'solutions': [
                'Run diagnostic: diagnose_check_mac_value()',
                'Verify HashKey and HashIV are correct',
                'Check parameter sort order (case-insensitive)',
                'Ensure URL encoding is not applied',
                'For .NET: verify character replacement is done',
            ]
        },
        '-4': {
            'message': 'Insufficient payment amount',
            'cause': 'Transaction amount too small or too large',
            'solutions': [
                'Verify amount meets minimum (usually 1 TWD)',
                'Check amount does not exceed maximum',
                'Ensure amount is positive integer',
            ]
        },
        '10100001': {
            'message': 'Unsupported currency',
            'cause': 'Only TWD is supported',
            'solutions': [
                'Change currency to TWD only',
            ]
        },
        '10100002': {
            'message': 'Invalid item',
            'cause': 'Item information is invalid',
            'solutions': [
                'Verify ItemName is provided',
                'Check ItemName does not contain invalid characters',
            ]
        },
    }

    @staticmethod
    def diagnose_error(rtn_code: str) -> Dict[str, Any]:
        """
        Diagnose error from OMG RtnCode.

        診斷 OMG 錯誤碼含義和解決方案。

        Args:
            rtn_code: RtnCode from OMG API response

        Returns:
            Dict with error details and solutions
        """
        error_info = ErrorDiagnosis.ERROR_CODES.get(rtn_code, {
            'message': 'Unknown error code',
            'cause': f'RtnCode {rtn_code} not found in documentation',
            'solutions': [
                f'Search OMG documentation for code {rtn_code}',
                'Enable debug logging to see full response',
            ]
        })

        return {
            'error_code': rtn_code,
            'message': error_info['message'],
            'cause': error_info['cause'],
            'solutions': error_info['solutions'],
            'timestamp': datetime.now().isoformat(),
        }

    @staticmethod
    def diagnose_check_mac_value(
        data: Dict[str, str],
        received_mac: str,
        hash_key: str,
        hash_iv: str
    ) -> Dict[str, Any]:
        """
        Step-by-step diagnosis for CheckMacValue validation failure.

        逐步診斷 CheckMacValue 驗證失敗的原因。

        Args:
            data: Request parameters (without CheckMacValue)
            received_mac: Received CheckMacValue from response
            hash_key: Your HashKey
            hash_iv: Your HashIV

        Returns:
            Diagnostic results with expected vs actual values
        """
        diagnosis = {
            'step_1_parameters': {},
            'step_2_sort': [],
            'step_3_parameter_string': '',
            'step_4_mac_string': '',
            'step_5_calculated_mac': '',
            'step_6_comparison': {},
        }

        # Step 1: Verify parameters
        diagnosis['step_1_parameters'] = {
            'count': len(data),
            'keys': list(data.keys()),
            'has_check_mac_value': 'CheckMacValue' in data,
        }

        # Step 2: Sort parameters (case-insensitive)
        sorted_params = sorted(data.items(), key=lambda x: x[0].lower())
        diagnosis['step_2_sort'] = sorted_params

        # Step 3: Build parameter string
        param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        diagnosis['step_3_parameter_string'] = param_str

        # Step 4: Build MAC string with HashIV and HashKey
        mac_str = f"HashIV={hash_iv}&{param_str}&HashKey={hash_key}"
        diagnosis['step_4_mac_string'] = mac_str

        # Step 5: Calculate SHA256
        calculated_mac = hashlib.sha256(mac_str.encode('utf-8')).hexdigest().upper()
        diagnosis['step_5_calculated_mac'] = calculated_mac

        # Step 6: Compare
        is_match = calculated_mac.upper() == received_mac.upper()
        diagnosis['step_6_comparison'] = {
            'expected': calculated_mac,
            'received': received_mac.upper(),
            'match': is_match,
        }

        if not is_match:
            diagnosis['recommendation'] = 'CheckMacValue mismatch detected. See steps 1-5 to identify differences.'

        return diagnosis

    @staticmethod
    def check_network_connectivity(hostname: str = "payment.funpoint.com.tw", port: int = 443) -> Dict[str, Any]:
        """
        Check network connectivity to OMG servers.

        檢查到 OMG 伺服器的網路連線。

        Args:
            hostname: OMG domain (default: production)
            port: HTTPS port (default: 443)

        Returns:
            Connectivity test results
        """
        try:
            sock = socket.create_connection((hostname, port), timeout=5)
            sock.close()

            return {
                'hostname': hostname,
                'port': port,
                'connectivity': 'success',
                'message': 'Successfully connected to OMG server',
                'timestamp': datetime.now().isoformat(),
            }
        except socket.timeout:
            return {
                'hostname': hostname,
                'port': port,
                'connectivity': 'timeout',
                'message': 'Connection timeout - network may be slow or blocked',
                'solutions': [
                    'Check firewall rules',
                    'Verify you can ping the server',
                    'Check network connectivity',
                    'Try from different network',
                ],
                'timestamp': datetime.now().isoformat(),
            }
        except socket.error as e:
            return {
                'hostname': hostname,
                'port': port,
                'connectivity': 'failed',
                'error': str(e),
                'solutions': [
                    'Verify hostname is correct',
                    'Check firewall/proxy settings',
                    'Ensure port 443 is open',
                    'Try from command line: openssl s_client -connect ' + hostname,
                ],
                'timestamp': datetime.now().isoformat(),
            }

    @staticmethod
    def check_timestamp_sync() -> Dict[str, Any]:
        """
        Check system time synchronization.

        檢查系統時間同步狀態。某些 OMG API 對時間敏感。

        Returns:
            System time vs NTP server time
        """
        import ntplib

        try:
            ntp_client = ntplib.NTPClient()
            response = ntp_client.request('pool.ntp.org', version=3)

            local_time = datetime.now().timestamp()
            ntp_time = response.tx_time
            time_diff = abs(local_time - ntp_time)

            return {
                'local_time': datetime.fromtimestamp(local_time).isoformat(),
                'ntp_time': datetime.fromtimestamp(ntp_time).isoformat(),
                'time_difference_seconds': time_diff,
                'sync_status': 'synced' if time_diff < 5 else 'out_of_sync',
                'message': 'Time is in sync' if time_diff < 5 else 'System time is out of sync - this may cause API errors',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                'sync_status': 'unknown',
                'error': str(e),
                'message': 'Could not verify time sync - ensure system time is correct',
            }


# Example usage
if __name__ == "__main__":
    # Diagnose error code
    error_result = ErrorDiagnosis.diagnose_error('-3')
    print(f"Error diagnosis: {error_result}")

    # Diagnose CheckMacValue
    test_data = {
        'MerchantID': '1000031',
        'MerchantTradeNo': 'TEST123',
        'TotalAmount': '1000',
    }

    mac_diagnosis = ErrorDiagnosis.diagnose_check_mac_value(
        test_data,
        'RECEIVED_MAC_VALUE',
        '265fIDjIvesceXWM',
        'pOOvhGd1V2pJbjfX'
    )
    print(f"CheckMacValue diagnosis: {mac_diagnosis}")

    # Check connectivity
    connectivity = ErrorDiagnosis.check_network_connectivity()
    print(f"Connectivity: {connectivity}")
```

---

## FAQ | 常見問題

### Q: 這份 Skill 適合誰使用？ Who is this Skill for?

**系統開發者 System Developers**: 直接參考 API 規格和程式碼範例來串接金流，包含 Python、Node.js、PHP、.NET 四種語言的 CheckMacValue 實作，以及完整的 FastAPI 範例。

**新手開發者 Beginners**: 從「Quick Start 快速開始」章節開始，按步驟設定測試環境，用測試卡號進行第一筆交易，再逐步擴展到其他付款方式。

**AI 應用開發者 AI Application Developers**: 將此 Skill 檔案放入 `.skills` 資料夾（Claude）或貼入 Custom Instructions（OpenAI），AI 助手就能自動理解 OMG 金流規格並產生正確的串接程式碼。

**專案經理/PM Project Managers**: 可快速了解 OMG 金流支援哪些付款方式、API 功能範圍，以及上線前需要完成的檢測項目。

### Q: 如何讓 AI 幫我寫串接程式碼？ How to let AI write integration code?

```
方法一（Claude Code / Cowork）:
  把 SKILL.md 放入 .skills/skills/omg-payment/ 資料夾

方法二（ChatGPT / OpenAI）:
  把 SKILL_OPENAI.md 內容貼入 Custom Instructions，或上傳檔案

方法三（任何 AI）:
  上傳 SKILL.md 或 SKILL_OPENAI.md 後說：
  「請根據這份文件幫我用 [語言/框架] 串接 OMG 金流」
```

### Q: 測試環境和正式環境有什麼差別？ Test vs Production?

| Item 項目 | Test 測試 | Production 正式 |
|---------|--------|--------------|
| URL | payment-**stage**.funpoint.com.tw | payment.funpoint.com.tw |
| MerchantID | 1000031 | (Your own 你自己的) |
| Real money 真金白銀 | No 否 | Yes 是 |
| HTTPS required | No 否 | Yes 是 |
| SimulatePaid | Can be 1 | Always 0 |

### Q: 為什麼收不到 ReturnURL 通知？ Why am I not receiving ReturnURL notifications?

1. ReturnURL 必須是公開可存取的網址（不能是 localhost）
2. 本地開發用 ngrok 建立公開通道
3. 伺服器必須回應 `1|OK`（純文字）
4. 檢查 OMG 廠商後台的交易紀錄

### Q: CheckMacValue 一直驗證失敗怎麼辦？ CheckMacValue keeps failing?

使用 Debug 章節的 `debug_check_mac_value()` 函式，逐步印出每一步的結果，通常問題出在：排序方式不對（必須不分大小寫）、.NET 替換沒做、URL encode 方式不對。

---

## Reference | 參考文件

- OMG Payment Official API Document: `funpoint_aio.pdf` (V 1.4.9, 2025-11)
- Company 公司: **茂為歐買尬數位科技股份有限公司** / **MacroWell OMG Digital Entertainment Co., Ltd.**
- Country 國家: **Taiwan 台灣**
- Official Website 官方網站: **https://www.funpoint.com.tw/**
- API Version: AioCheckOut V5
- Vendor Backend 廠商後台: `https://vendor.funpoint.com.tw` (Production) / `https://vendor-stage.funpoint.com.tw` (Test)

---

## Author & Disclaimer | 作者與免責聲明

**Author 作者**: Mitchell Chen

**AI Assistance AI 輔助**: This document was generated with assistance from **Claude** (Anthropic). 本文件由 **Claude** (Anthropic) AI 輔助產出。

**Disclaimer 免責聲明**:

- 本文件一切內容以 **OMG 官方文件**為主，如有出入請以官方文件為準。
- All content in this document is based on the **official OMG API documentation**. In case of discrepancies, the official documentation prevails.
- 如有任何問題，請洽 OMG 官網: **https://www.funpoint.com.tw/**
- For any questions, please contact the official OMG website: **https://www.funpoint.com.tw/**
- 本文件為開源專案，採用 MIT License，可自由使用、修改、分享。
- This document is open source under MIT License, free to use, modify, and share.
