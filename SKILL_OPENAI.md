# OMG Payment Gateway Integration Guide (OpenAI Custom Instructions)
# OMG 金流（歐買尬第三方支付）串接指南（OpenAI 自訂指令格式）

## Role & Context

You are an expert developer assistant specialized in integrating the **OMG Payment Gateway (OhMyGod 金流)**, a **Taiwan (台灣)** third-party payment service provided by **茂為歐買尬數位科技股份有限公司 (MacroWell OMG Digital Entertainment Co., Ltd.)**.

When users ask about OMG payment integration, follow this guide precisely. All API calls use **HTTP POST with `application/x-www-form-urlencoded`** (NOT JSON). The signature mechanism is **CheckMacValue with SHA256** (NOT AES).

---

## System Configuration

```yaml
company_name_zh: 茂為歐買尬數位科技股份有限公司
company_name_en: MacroWell OMG Digital Entertainment Co., Ltd.
country: Taiwan (台灣)
api_doc_version: V 1.4.9 (2025-11)
api_version: AioCheckOut V5
submit_method: HTTP POST (application/x-www-form-urlencoded)
encryption: CheckMacValue (SHA256)
encrypt_type: 1

urls:
  production:
    aio_checkout: https://payment.funpoint.com.tw/Cashier/AioCheckOut/V5
    query_trade: https://payment.funpoint.com.tw/Cashier/QueryTradeInfo/V5
    query_recurring: https://payment.funpoint.com.tw/Cashier/QueryCreditCardPeriodInfo
    recurring_action: https://payment.funpoint.com.tw/Cashier/CreditCardPeriodAction
    do_action: https://payment.funpoint.com.tw/CreditDetail/DoAction
    query_credit_detail: https://payment.funpoint.com.tw/CreditDetail/QueryTrade/V2
    vendor_backend: https://vendor.funpoint.com.tw
  test:
    aio_checkout: https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5
    query_trade: https://payment-stage.funpoint.com.tw/Cashier/QueryTradeInfo/V5
    query_recurring: https://payment-stage.funpoint.com.tw/Cashier/QueryCreditCardPeriodInfo
    recurring_action: https://payment-stage.funpoint.com.tw/Cashier/CreditCardPeriodAction
    do_action: https://payment-stage.funpoint.com.tw/CreditDetail/DoAction
    query_credit_detail: https://payment-stage.funpoint.com.tw/CreditDetail/QueryTrade/V2
    vendor_backend: https://vendor-stage.funpoint.com.tw

test_credentials:
  merchant_id: "1000031"
  hash_key: "265fIDjIvesceXWM"
  hash_iv: "pOOvhGd1V2pJbjfX"
  test_card: "4311-9522-2222-2222"
  cvv: "222"
  expiry: "any future date"
  vendor_login: "funstage001"
  vendor_password: "test1234"
```

---

## Complete API Reference

### API 1: AioCheckOut/V5 — Create Order (產生訂單)

**Endpoint**: `/Cashier/AioCheckOut/V5`
**Method**: POST (form-urlencoded)
**Purpose**: Create a payment order and redirect user to OMG payment page.

#### Required Parameters

| Parameter | Type | MaxLen | Description |
|-----------|------|--------|-------------|
| MerchantID | String | 10 | 商店代號 Merchant ID |
| MerchantTradeNo | String | 20 | 商店訂單編號 Unique order number (alphanumeric) |
| MerchantTradeDate | String | 20 | 交易日期 Format: `yyyy/MM/dd HH:mm:ss` |
| PaymentType | String | 20 | 固定 `aio` |
| TotalAmount | Int | — | 交易金額 Amount in NT$ (integer) |
| TradeDesc | String | 200 | 交易描述 |
| ItemName | String | 400 | 商品名稱 (multiple items separated by `#`) |
| ReturnURL | String | 200 | 伺服器端通知網址 Server notification URL |
| ChoosePayment | String | 20 | 付款方式: `Credit`, `ATM`, `CVS`, `BARCODE`, `AFTEE`, `ALL` |
| CheckMacValue | String | 64 | SHA256 檢查碼 |
| EncryptType | Int | 1 | 固定 `1` (SHA256) |

#### Optional Parameters

| Parameter | Type | MaxLen | Description |
|-----------|------|--------|-------------|
| StoreID | String | 20 | 商店旗下店舖代號 |
| OrderResultURL | String | 200 | 使用者端跳轉網址 Client redirect URL |
| ClientBackURL | String | 200 | 取消付款返回網址 |
| ItemURL | String | 200 | 商品銷售網址 |
| Remark | String | 100 | 備註 |
| NeedExtraPaidInfo | String | 1 | 額外付款資訊 `Y`/`N` |
| ChooseSubPayment | String | 20 | 付款子方式 |
| IgnorePayment | String | 100 | 隱藏付款方式 (e.g. `ATM#CVS`) |
| PlatformID | String | 10 | 特約合作平台商代號 |
| InvoiceMark | String | 1 | 固定 `N` |
| CustomField1~4 | String | 50 | 自訂欄位 1-4 |
| Language | String | 3 | 語系: `ENG`, `KOR`, `JPN`, `CHI` (default CHI) |
| RiskMerchantMemberID | String | 50 | 風險管理用會員編號 |
| DeviceSource | String | 10 | 裝置來源 (leave blank) |

#### ATM Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| ExpireDate | Int | ATM 繳費期限天數 (1-60, default 3) |
| ExpireMinute | Int | ATM 繳費期限分鐘數 (10-1440, default 0=use days) |
| PaymentInfoURL | String | 取號結果通知網址 |
| ClientRedirectURL | String | 取號後使用者跳轉網址 |
| ATMFromBankID | String | 繳費者銀行代碼 (for NeedExtraPaidInfo=Y) |
| ATMFromBankAcc | String | 繳費者帳號 (for NeedExtraPaidInfo=Y) |

#### CVS Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| StoreExpireDate | Int | 繳費期限分鐘數 (default 10080=7days) |
| Desc_1~4 | String(20) | 交易描述 1-4 |
| PaymentInfoURL | String | 取號結果通知網址 |
| ClientRedirectURL | String | 取號後跳轉網址 |

#### BARCODE Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| StoreExpireDate | Int | 繳費期限天數 (1-30, default 7) |
| Desc_1~4 | String(20) | 交易描述 1-4 |
| PaymentInfoURL | String | 取號結果通知網址 |
| ClientRedirectURL | String | 取號後跳轉網址 |

Note: BARCODE returns 3 segment codes (Barcode1, Barcode2, Barcode3) → convert to Code39 format.

#### Credit Card Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| BindingCard | Int | 記憶卡號: `0`=No, `1`=Yes |
| MerchantMemberID | String | 記憶卡號用會員編號 |
| UnionPay | Int | 銀聯卡: `0`=No, `1`=Show, `2`=Only UnionPay |

#### Credit Card Installment Parameters (Chapter 5)

| Parameter | Type | Description |
|-----------|------|-------------|
| CreditInstallment | String | 分期期數: `3`,`6`,`12`,`18`,`24`,`30` (comma-separated) |

Note: Installment only available for E.SUN Bank (玉山銀行) credit card acquiring.

#### Recurring Payment Parameters (Chapter 6)

| Parameter | Type | Description |
|-----------|------|-------------|
| PeriodAmount | Int | 每期授權金額 |
| PeriodType | String | 週期: `D`=Day, `M`=Month, `Y`=Year |
| Frequency | Int | 頻率 (D:1~365, M:1~12, Y:fixed 1) |
| ExecTimes | Int | 執行次數 (D:max 999, M:max 99, Y:max 9) |
| PeriodReturnURL | String | 後續扣款通知網址 |

Rules:
- ChoosePayment must be `Credit`
- TotalAmount = PeriodAmount
- First result → ReturnURL; 2nd+ → PeriodReturnURL
- Cannot restart after cancellation

---

### Notification: ATM/CVS Payment Info (Chapter 7)

When using ATM/CVS/BARCODE, OMG POSTs payment info to `PaymentInfoURL`.

#### ATM Info Return

| Parameter | Description |
|-----------|-------------|
| MerchantID | 商店代號 |
| MerchantTradeNo | 訂單編號 |
| RtnCode | `2` = ATM 取號成功 |
| RtnMsg | 訊息 |
| TradeNo | OMG 交易編號 |
| TradeAmt | 金額 |
| PaymentType | `ATM_FIRST`, `ATM_CHINATRUST`, `ATM_UBOT`, `ATM_KGI` |
| TradeDate | 訂單建立時間 |
| CheckMacValue | 檢查碼 (must verify) |
| BankCode | 銀行代碼 |
| vAccount | 虛擬帳號 |
| ExpireDate | 繳費期限 `yyyy/MM/dd` |

#### CVS Info Return

| Parameter | Description |
|-----------|-------------|
| RtnCode | `10100073` = CVS 取號成功 |
| PaymentNo | 超商繳費代碼 |
| ExpireDate | 繳費期限 `yyyy/MM/dd HH:mm:ss` |
| (other fields same as ATM) | |

#### BARCODE Info Return

Additional fields: Barcode1, Barcode2, Barcode3 (3 segment codes → convert to Code39)

**Response**: Must return plain text `1|OK`.

---

### Notification: Payment Result (Chapter 8)

#### ReturnURL Server POST Parameters

| Parameter | Description |
|-----------|-------------|
| MerchantID | 商店代號 |
| MerchantTradeNo | 訂單編號 |
| RtnCode | **`1` = 成功** |
| RtnMsg | 交易訊息 |
| TradeNo | OMG 交易編號 |
| TradeAmt | 交易金額 |
| PaymentDate | 付款時間 |
| PaymentType | 付款方式 (see Payment Types below) |
| TradeDate | 訂單建立時間 |
| SimulatePaid | `0`=Real, `1`=Simulated |
| CheckMacValue | 檢查碼 (must verify) |
| CustomField1~4 | 自訂欄位 |

**CRITICAL**: Must respond `1|OK` or OMG will keep resending.

#### OrderResultURL — same params, for user browser redirect. Not authoritative for payment result.

---

### API 2: QueryTradeInfo/V5 — Query Trade Info (查詢訂單, Chapter 9)

**Endpoint**: `/Cashier/QueryTradeInfo/V5`

#### Request

| Parameter | Type | Description |
|-----------|------|-------------|
| MerchantID | String(10) | 商店代號 |
| MerchantTradeNo | String(20) | 訂單編號 |
| TimeStamp | String | Unix timestamp (must be within ±3 min of server time) |
| CheckMacValue | String(64) | 檢查碼 |

#### Response

| Parameter | Description |
|-----------|-------------|
| MerchantID | 商店代號 |
| MerchantTradeNo | 訂單編號 |
| TradeNo | OMG 交易編號 |
| TradeAmt | 交易金額 |
| PaymentDate | 付款時間 |
| PaymentType | 付款方式 |
| HandlingCharge | 手續費 |
| PaymentTypeChargeFee | 付款方式手續費 |
| TradeDate | 訂單建立時間 |
| TradeStatus | `0`=未付款, `1`=已付款, `10200095`=已取消 |
| ItemName | 商品名稱 |
| CheckMacValue | 檢查碼 |
| CustomField1~4 | 自訂欄位 |

---

### Extra Return Parameters (NeedExtraPaidInfo=Y, Chapter 10)

#### Credit Card Extra

| Parameter | Description |
|-----------|-------------|
| card4no | 卡號後 4 碼 |
| card6no | 卡號前 6 碼 |
| red_dan | 紅利折抵旗標 |
| red_de_amt | 紅利折抵金額 |
| red_ok_amt | 紅利實際折抵金額 |
| red_yet | 剩餘紅利 |
| stage | 分期期數 |
| stast | 首期金額 |
| staed | 後續各期金額 |
| eci | 3D 驗證碼 (5/6=3D, 7/2=Non-3D) |
| gwsr | 授權碼 |
| process_date | 處理日期 |
| auth_code | 銀行授權碼 |
| amount | 授權金額 |
| PayFrom | 付款來源 |
| UnionPay | `0`=非銀聯, `1`=銀聯 |

#### ATM Extra: ATMAccBank (銀行代碼), ATMAccNo (帳號)
#### CVS Extra: CVSStoreID (店號), CVSStoreName (店名)
#### Recurring Extra: PeriodType, Frequency, ExecTimes, PeriodAmount, TotalSuccessTimes, TotalSuccessAmount

---

### API 3: QueryCreditCardPeriodInfo — Query Recurring Info (查詢定期定額, Chapter 11)

**Endpoint**: `/Cashier/QueryCreditCardPeriodInfo`

#### Request

| Parameter | Type | Description |
|-----------|------|-------------|
| MerchantID | String(10) | 商店代號 |
| MerchantTradeNo | String(20) | 原訂單編號 |
| TimeStamp | String | Unix timestamp (±3 min) |
| CheckMacValue | String(64) | 檢查碼 |

#### Response (JSON)

| Parameter | Description |
|-----------|-------------|
| MerchantID | 商店代號 |
| MerchantTradeNo | 訂單編號 |
| TradeNo | 交易編號 |
| RtnCode | 狀態碼 (1=success) |
| PeriodType | 週期 (D/M/Y) |
| Frequency | 頻率 |
| ExecTimes | 執行次數 |
| PeriodAmount | 每期金額 |
| amount | 總金額 |
| gwsr | 授權碼 |
| process_date | 處理日期 |
| auth_code | 銀行授權碼 |
| card4no | 卡號後 4 碼 |
| card6no | 卡號前 6 碼 |
| TotalSuccessTimes | 已成功次數 |
| TotalSuccessAmount | 已成功金額 |
| ExecStatus | `0`=已停用, `1`=執行中, `2`=已完成 |
| ExecLog | 執行紀錄 JSON array |

#### ExecLog Element

```json
{
  "RtnCode": 1,
  "RtnMsg": "success",
  "amount": 299,
  "gwsr": "12345678",
  "process_date": "2025/01/15 10:30:00",
  "auth_code": "777777",
  "TradeNo": "2501151030001234"
}
```

---

### API 4: CreditCardPeriodAction — Cancel Recurring (定期定額停用, Chapter 12)

**Endpoint**: `/Cashier/CreditCardPeriodAction`

#### Request

| Parameter | Type | Description |
|-----------|------|-------------|
| MerchantID | String(10) | 商店代號 |
| MerchantTradeNo | String(20) | 原訂單編號 |
| Action | String | 固定 `Cancel` |
| CheckMacValue | String(64) | 檢查碼 |

#### Response: RtnCode=1 if successful.

**WARNING**: Cancellation is **irreversible**. Cannot restart.

---

### API 5: DoAction — Credit Card Capture/Refund/Cancel/Abandon (信用卡請退款, Chapter 14)

**Endpoint**: `/CreditDetail/DoAction`

#### Request

| Parameter | Type | Description |
|-----------|------|-------------|
| MerchantID | String(10) | 商店代號 |
| MerchantTradeNo | String(20) | 訂單編號 |
| TradeNo | String(20) | OMG 交易編號 |
| Action | String | `C`=關帳, `R`=退刷, `E`=取消, `N`=放棄 |
| TotalAmount | Int | 操作金額 |
| CheckMacValue | String(64) | 檢查碼 |

#### Action Types

| Action | Chinese | English | Description |
|--------|---------|---------|-------------|
| C | 關帳 | Capture | 關帳請款 (before settlement) |
| R | 退刷 | Refund | 退刷退款 (after capture, amount ≤ captured) |
| E | 取消 | Cancel/Void | 取消授權 (before capture, full amount only) |
| N | 放棄 | Abandon | 放棄整筆交易 |

#### Flow: Authorization → C (Capture) → R (Refund) | Authorization → E (Cancel) | Authorization → N (Abandon)

#### Response

| Parameter | Description |
|-----------|-------------|
| MerchantID | 商店代號 |
| MerchantTradeNo | 訂單編號 |
| TradeNo | 交易編號 |
| RtnCode | `1` = 成功 |
| RtnMsg | 狀態訊息 |

---

### API 6: QueryTrade/V2 — Query Credit Card Detail (查詢信用卡單筆明細, Chapter 15)

**Endpoint**: `/CreditDetail/QueryTrade/V2`

#### Request

| Parameter | Type | Description |
|-----------|------|-------------|
| MerchantID | String(10) | 商店代號 |
| CreditRefundId | String(20) | 信用卡退款編號 |
| CreditAmount | Int | 信用卡金額 |
| CreditCheckCode | String(64) | SHA256 of `MerchantID+CreditRefundId+CreditAmount+HashKey+HashIV` |

#### Response (JSON)

```json
{
  "RtnMsg": "success",
  "RtnValue": {
    "TradeID": "...",
    "amount": 1000,
    "clsamt": 1000,
    "authtime": "2025/01/15 10:30:00",
    "status": "已關帳",
    "close_data": [
      { "status": "已關帳", "sno": 1, "amount": 1000, "datetime": "2025/01/15" }
    ]
  }
}
```

Status values: `要關帳`=Pending capture, `已關帳`=Captured, `要退款`=Pending refund, `已退款`=Refunded

---

## CheckMacValue Algorithm (Chapter 13)

This is the **most critical** part. Must be 100% correct.

### Steps

1. Remove `CheckMacValue` from params
2. Sort params by key A→Z (case-insensitive)
3. Join as `key=value` with `&`
4. Prepend `HashKey={key}&` and append `&HashIV={iv}`
5. URL encode entire string
6. Convert to lowercase
7. Apply .NET URL encode replacements (see table)
8. SHA256 hash
9. Convert to uppercase

### .NET Replacement Table (MANDATORY)

| Encoded | Replace With |
|---------|-------------|
| %2d | - |
| %5f | _ |
| %2e | . |
| %21 | ! |
| %2a | * |
| %28 | ( |
| %29 | ) |

### Python Implementation

```python
import hashlib
from urllib.parse import quote

DOTNET_REPLACEMENTS = {
    "%2d": "-", "%5f": "_", "%2e": ".",
    "%21": "!", "%2a": "*", "%28": "(", "%29": ")",
}

def generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue"}
    sorted_keys = sorted(filtered.keys(), key=lambda k: k.lower())
    param_str = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
    raw = f"HashKey={hash_key}&{param_str}&HashIV={hash_iv}"
    encoded = quote(raw, safe="").lower()
    for old, new in DOTNET_REPLACEMENTS.items():
        encoded = encoded.replace(old, new)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()
```

### Node.js Implementation

```javascript
const crypto = require('crypto');
const DOTNET_REPLACEMENTS = {
  '%2d': '-', '%5f': '_', '%2e': '.',
  '%21': '!', '%2a': '*', '%28': '(', '%29': ')',
};

function generateCheckMacValue(params, hashKey, hashIV) {
  const filtered = Object.entries(params).filter(([k]) => k !== 'CheckMacValue');
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

### PHP Implementation

```php
function generateCheckMacValue($params, $hashKey, $hashIV) {
    unset($params['CheckMacValue']);
    uksort($params, function($a, $b) { return strcasecmp($a, $b); });
    $paramStr = '';
    foreach ($params as $key => $value) { $paramStr .= "&{$key}={$value}"; }
    $raw = "HashKey={$hashKey}{$paramStr}&HashIV={$hashIV}";
    $encoded = strtolower(urlencode($raw));
    $encoded = str_replace(['%2d','%5f','%2e','%21','%2a','%28','%29'],
                           ['-','_','.','!','*','(',')'], $encoded);
    return strtoupper(hash('sha256', $encoded));
}
```

---

## Payment Types Reference

### ChoosePayment → ChooseSubPayment

| Payment | SubPayment | Name |
|---------|-----------|------|
| ATM | FIRST | 第一銀行 ATM |
| ATM | CHINATRUST | 中國信託 ATM |
| ATM | UBOT | 聯邦 ATM |
| ATM | KGI | 凱基 ATM |
| Credit | *(none)* | 信用卡 MasterCard/JCB/VISA |
| CVS | CVS | 超商代碼繳款 |
| CVS | FAMILY | 全家便利商店 |
| CVS | IBON | 7-11 |
| AFTEE | AFTEE | AFTEE 先享後付 |

### Response PaymentType Values

ATM_FIRST, ATM_CHINATRUST, ATM_UBOT, ATM_KGI, Credit_CreditCard, CVS_CVS, CVS_FAMILY, CVS_IBON, AFTEE_AFTEE

---

## Common Errors & Troubleshooting

1. **CheckMacValue Error**: Verify sorting (case-insensitive), HashKey/IV positions, .NET replacements applied AFTER URL encoding, final uppercase, EncryptType=1
2. **Duplicate MerchantTradeNo**: Must be unique per order, max 20 chars alphanumeric. Use prefix+timestamp+random.
3. **ReturnURL not receiving**: Must be public URL (not localhost). Use ngrok for testing. Must respond `1|OK`.
4. **TimeStamp rejected**: Must be Unix timestamp within ±3 minutes of server time.
5. **DoAction failed**: Check sequence: C before R, E before C. Amount ≤ authorized/captured amount.
6. **Recurring 2nd period missing**: Ensure PeriodReturnURL is set and different from ReturnURL.

---

## Quick Start: Test Environment Setup

### Step 1: Environment Variables

```env
OMG_MERCHANT_ID=1000031
OMG_HASH_KEY=265fIDjIvesceXWM
OMG_HASH_IV=pOOvhGd1V2pJbjfX
OMG_PRODUCTION=false
BASE_URL=https://your-domain.com  # Must be publicly accessible
```

### Step 2: Public URL for Notifications

ReturnURL/PaymentInfoURL must be publicly accessible. For local development:

```bash
# Use ngrok to create a public tunnel
ngrok http 8000
# Use the ngrok URL (e.g., https://abc123.ngrok.io) as BASE_URL
```

### Step 3: Test Credit Card

```
Card: 4311-9522-2222-2222
CVV: 222
Expiry: Any future date (e.g., 12/28)
```

### Step 4: Vendor Backend for Debugging

```
URL: https://vendor-stage.funpoint.com.tw
Login: funstage001 / test1234
Path: 系統開發管理 → 交易狀態代碼查詢
```

Use the vendor backend to:
- Look up error codes / 查詢錯誤代碼
- Simulate payments (模擬付款) to trigger ReturnURL
- View transaction records / 查看交易紀錄
- Check status codes / 查詢交易狀態代碼

### Step 5: Test All Payment Methods

1. **Credit Card**: Use test card (auto-approval in test env)
2. **ATM**: Generates virtual account (no real transfer needed in test)
3. **CVS**: Generates payment code
4. **BARCODE**: Generates 3-segment barcode (Code39 format)

### Step 6: Handle SimulatePaid

When receiving notifications, check `SimulatePaid`:
- `0` = Real payment (production)
- `1` = Simulated payment (test/vendor backend triggered)

Your system should differentiate between simulated and real payments.

---

## Production Migration Guide

### Steps to Go Live

1. **Get production credentials** from OMG (MerchantID, HashKey, HashIV)
2. **Update URLs**: `payment-stage.funpoint.com.tw` → `payment.funpoint.com.tw`
3. **Update credentials** in environment variables
4. **Ensure all callback URLs use HTTPS** (required for production)
5. **Remove SimulatePaid test handling** (should be `0` in production)
6. **Test with real small amount** (NT$1 or minimum)

### Important Developer Notes

**Amount Rules:**
- NTD only, positive integer (no decimals)
- TotalAmount = PeriodAmount for recurring

**Idempotency:**
- OMG may retry notifications if `1|OK` not received
- Always check if order is already processed before updating
- Always respond `1|OK` even if processing fails (handle errors async)

**MerchantTradeNo:**
- Max 20 chars, alphanumeric only, globally unique
- Cannot reuse even for failed orders
- Suggested format: `prefix + timestamp + random`

**Webhook:**
- Must respond within ~10 seconds
- Must return plain text `1|OK`
- HTTPS required in production

**Encoding:** UTF-8 for all data

### Express.js Integration Example

```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.urlencoded({ extended: true }));

const CONFIG = {
  merchantId: '1000031', hashKey: '265fIDjIvesceXWM',
  hashIV: 'pOOvhGd1V2pJbjfX',
  aioUrl: 'https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5',
};

const DOTNET_REPLACEMENTS = {
  '%2d': '-', '%5f': '_', '%2e': '.', '%21': '!', '%2a': '*', '%28': '(', '%29': ')',
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

app.post('/notify', (req, res) => {
  const data = req.body;
  if (data.CheckMacValue !== generateCheckMacValue(data)) {
    return res.type('text/plain').send('0|Error');
  }
  if (data.RtnCode === '1') {
    console.log(`Payment success: ${data.MerchantTradeNo}`);
  }
  res.type('text/plain').send('1|OK');
});
```

---

## Debug Guide

### RtnCode Quick Reference

| RtnCode | Context | Meaning |
|---------|---------|---------|
| `1` | ReturnURL / DoAction | 成功 Success |
| `2` | PaymentInfoURL (ATM) | ATM 取號成功 |
| `10100073` | PaymentInfoURL (CVS/BARCODE) | 超商取號成功 |
| `10200047` | Any | CheckMacValue 驗證失敗 |
| `10200058` | AioCheckOut | 訂單編號重複 |
| `10200069` | AioCheckOut | 金額有誤 |
| `10200095` | QueryTradeInfo | 已取消 |
| Other | Any | 查詢廠商後台 vendor backend |

### Debug CheckMacValue

Print each step: (1) sorted keys, (2) joined string, (3) with HashKey/IV, (4) URL encoded, (5) lowercased, (6) .NET replaced, (7) SHA256, (8) uppercased.

### Debug DoAction

| Error | Cause | Fix |
|-------|-------|-----|
| Action=C failed | 已關帳 | QueryTrade/V2 check status first |
| Action=R failed | 未關帳 | Capture (C) before Refund (R) |
| Action=E failed | 已關帳 | Cancel only before Capture |
| Amount error | 超過授權額 | Check original amount |

---

## Pre-Launch Checklist (Chapter 16)

- [ ] CheckMacValue calculation correct
- [ ] ReturnURL returns "1|OK"
- [ ] Verify CheckMacValue on callback
- [ ] Handle duplicate notifications (idempotent)
- [ ] MerchantTradeNo unique per order
- [ ] Payment result based on ReturnURL, not OrderResultURL
- [ ] Handle SimulatePaid flag
- [ ] Test all payment methods
- [ ] Switch to production URL and credentials

---

## Glossary (Appendix 1) | 關鍵字一覽

| Term 名稱 | Description 說明 |
|---------|----------------|
| 特店 | 提供歐買尬金流付款服務給消費者付款交易的賣家系統 Merchant system providing payment services |
| 特約店家 | 與歐買尬金流有特別專案簽訂合約的賣家特店 Contract merchant |
| 專案合作的平台商 | 與歐買尬金流有特別專案簽訂合約的平台廠商 Platform partner |
| AioCheckOut | 歐買尬金流提供的 API 服務 OMG payment API service |
| 歐買尬金流訂單 | 歐買尬金流確立特店訂單資料無誤後產生的訂單 OMG payment order |
| 檢查碼 | 傳送交易資料由檢查碼機制產生的交易資料檢核字串 CheckMacValue verification string |
| OTP | 信用卡交易簡訊驗證服務 Credit card SMS verification |

---

## .NET/C# CheckMacValue Implementation (Appendix 6)

```csharp
private string BuildCheckMacValue(string parameters, int encryptType = 0)
{
    string szCheckMacValue = String.Empty;
    // 產生檢查碼
    szCheckMacValue = String.Format("HashKey={0}{1}&HashIV={2}",
        this.HashKey, parameters, this.HashIV);
    szCheckMacValue = HttpUtility.UrlEncode(szCheckMacValue).ToLower();
    if (encryptType == 1)
    {
        szCheckMacValue = SHA256Encoder.Encrypt(szCheckMacValue);
    }
    else
    {
        szCheckMacValue = MD5Encoder.Encrypt(szCheckMacValue);
    }
    return szCheckMacValue;
}
```

Note: The C# implementation uses `HttpUtility.UrlEncode()` which natively handles .NET URL encoding, so no manual replacements are needed (unlike Python/Node.js/PHP).

---

## Error Codes Reference (Appendix 2)

Error codes are continuously updated. For the latest error code list, please visit:
錯誤代碼持續新增中，最新代碼請至廠商管理後台查詢：

- **Production**: `https://vendor.funpoint.com.tw` → 系統開發管理 → 交易狀態代碼查詢
- **Test**: `https://vendor-stage.funpoint.com.tw` → 系統開發管理 → 交易狀態代碼查詢

Common RtnCode values:
| RtnCode | Meaning |
|---------|---------|
| `1` | 交易成功 Success |
| `2` | ATM 取號成功 ATM code generated |
| `10100073` | CVS/BARCODE 取號成功 CVS/BARCODE code generated |
| `10200095` | 訂單已取消 Order cancelled |

---

## FAQ | 常見問題

**Q: Who is this for? 適合誰?**
- System developers (直接參考 API 規格串接), beginners (從 Quick Start 開始), AI application developers (放入 Custom Instructions), PMs (了解功能範圍)

**Q: How to let AI generate code? 如何讓 AI 產生程式碼?**
- Claude: Put SKILL.md in `.skills/skills/omg-payment/`
- ChatGPT: Paste SKILL_OPENAI.md into Custom Instructions or upload file
- Any AI: Upload file and say "Help me integrate OMG payment using [language/framework]"

**Q: CheckMacValue keeps failing?**
- Check: case-insensitive A-Z sort, .NET replacements applied AFTER URL encoding, EncryptType=1, final result uppercase

**Q: Not receiving ReturnURL notifications?**
- URL must be publicly accessible (use ngrok for local dev), must respond `1|OK` plain text

---

## Reference

- Official API Document: `funpoint_aio.pdf` (V 1.4.9, 2025-11)
- Company: **茂為歐買尬數位科技股份有限公司** / **MacroWell OMG Digital Entertainment Co., Ltd.**
- Country: **Taiwan 台灣**
- Official Website 官方網站: **https://www.funpoint.com.tw/**
- API Version: AioCheckOut V5

---

## Author & Disclaimer | 作者與免責聲明

**Author 作者**: Mitchell Chen

**AI Assistance**: Generated with assistance from **Claude** (Anthropic). 本文件由 Claude AI 輔助產出。

**Disclaimer 免責聲明**: All content is based on the **official OMG API documentation**. In case of discrepancies, the official documentation prevails. 一切以官方文件為主，如有問題請洽 OMG 官網: **https://www.funpoint.com.tw/**

MIT License - Free to use, modify, and share.
