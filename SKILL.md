# OMG Payment Gateway Integration Skill

> For AI Assistants - Claude Code / Cowork Skill for integrating OMG third-party payment gateway.

## Basic Info

| Item | Description |
|------|-------------|
| Payment Gateway | OMG (MacroWell OMG Digital Entertainment Co.) |
| API Version | AioCheckOut V5 |
| Production URL | https://payment.funpoint.com.tw/Cashier/AioCheckOut/V5 |
| Test URL | https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5 |
| Submit Method | HTTP POST (form-urlencoded), NOT JSON |
| Encryption | CheckMacValue (SHA256), NOT AES |

## Test Credentials

| Item | Value |
|------|-------|
| MerchantID | 1000031 |
| HashKey | 265fIDjIvesceXWM |
| HashIV | pOOvhGd1V2pJbjfX |
| Test Card | 4311-9522-2222-2222 |
| CVV | 222 |
| Expiry | Any future date |

## Payment Flow

### Standard Payment
1. Merchant builds order params
2. Calculate CheckMacValue (SHA256)
3. Form POST to OMG AioCheckOut/V5
4. User completes payment on OMG page
5. OMG Server POST to ReturnURL (notify merchant)
6. OMG Client POST to OrderResultURL (redirect user)
7. Merchant responds "1|OK"

### Recurring Payment
1. Build order params with PeriodAmount, PeriodType, Frequency, ExecTimes
2. Calculate CheckMacValue (SHA256)
3. Form POST to OMG AioCheckOut/V5
4. User authorizes first payment
5. First result POST to ReturnURL
6. Subsequent charges POST to PeriodReturnURL
7. Always respond "1|OK"

## CheckMacValue Calculation (CRITICAL)

### Algorithm Steps
1. Sort all params (exclude CheckMacValue) by key name A-Z (case-insensitive)
2. Join as key=value with & separator
3. Prepend HashKey=xxx& and append &HashIV=xxx
4. URL encode the entire string
5. Convert to lowercase
6. Replace .NET URL encode special characters (see table)
7. SHA256 hash
8. Convert to uppercase

### .NET URL Encode Replacement Table (MANDATORY)

| URL Encode | Replace With |
|------------|-------------|
| %2d | - |
| %5f | _ |
| %2e | . |
| %21 | ! |
| %2a | * |
| %28 | ( |
| %29 | ) |

### Python Implementation

import hashlib
from urllib.parse import quote

DOTNET_REPLACEMENTS = {
    "%2d": "-", "%5f": "_", "%2e": ".",
    "%21": "!", "%2a": "*", "%28": "(", "%29": ")",
}

def generate_check_mac_value(params, hash_key, hash_iv):
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue"}
    sorted_keys = sorted(filtered.keys(), key=lambda k: k.lower())
    param_str = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
    raw = f"HashKey={hash_key}&{param_str}&HashIV={hash_iv}"
    encoded = quote(raw, safe="").lower()
    for old, new in DOTNET_REPLACEMENTS.items():
        encoded = encoded.replace(old, new)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()

## Required API Parameters (AioCheckOut/V5)

| Parameter | Type | Max | Description |
|-----------|------|-----|-------------|
| MerchantID | String | 10 | Merchant ID |
| MerchantTradeNo | String | 20 | Order number (unique) |
| MerchantTradeDate | String | 20 | yyyy/MM/dd HH:mm:ss |
| PaymentType | String | 20 | Fixed: aio |
| TotalAmount | Int | - | Amount in NT$ (integer) |
| TradeDesc | String | 200 | Trade description |
| ItemName | String | 400 | Item name (use # to separate) |
| ReturnURL | String | 200 | Server POST notification URL |
| ChoosePayment | String | 20 | Credit, ATM, CVS, ALL |
| CheckMacValue | String | 64 | SHA256 verification code |
| EncryptType | Int | 1 | Fixed: 1 (SHA256) |

## Recurring Payment Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| PeriodAmount | Int | Amount per period |
| PeriodType | String | D=Day, M=Month, Y=Year |
| Frequency | Int | D:1-365, M:1-12, Y:fixed 1 |
| ExecTimes | Int | D:max 999, M:max 99, Y:max 9 |
| PeriodReturnURL | String | Recurring notification URL |

Notes:
- ChoosePayment must be Credit for recurring
- TotalAmount = PeriodAmount
- First result -> ReturnURL
- 2nd period onwards -> PeriodReturnURL

## Payment Result (ReturnURL)

| Parameter | Description |
|-----------|-------------|
| MerchantID | Merchant ID |
| MerchantTradeNo | Order number |
| RtnCode | Status: 1 = Success |
| RtnMsg | Status message |
| TradeNo | OMG transaction number |
| TradeAmt | Transaction amount |
| PaymentDate | Payment time |
| CheckMacValue | Must verify |

CRITICAL: Must respond plain text "1|OK" after receiving notification.

## Cancel Recurring

| Environment | URL |
|-------------|-----|
| Production | https://payment.funpoint.com.tw/Cashier/CreditCardPeriodAction |
| Test | https://payment-stage.funpoint.com.tw/Cashier/CreditCardPeriodAction |

Parameters: MerchantID, MerchantTradeNo, Action=Cancel, CheckMacValue

## Common Errors

1. CheckMacValue wrong: Check sorting, HashKey/HashIV position, .NET replacements, uppercase
2. Duplicate order: MerchantTradeNo must be unique, max 20 chars
3. No notification: ReturnURL must be public, respond "1|OK"
4. No 2nd period: Check PeriodReturnURL is set and different from ReturnURL

## Environment Variables

OMG_MERCHANT_ID=1000031
OMG_HASH_KEY=265fIDjIvesceXWM
OMG_HASH_IV=pOOvhGd1V2pJbjfX
OMG_PRODUCTION=false
