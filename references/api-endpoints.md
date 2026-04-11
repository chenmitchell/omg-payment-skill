# Reference R1 — OMG API Endpoint 速查

本文件彙整歐買尬核心 API 的用途、必要欄位與回應格式。實際 endpoint 路徑、欄位名稱與值請以歐買尬官方文件為準。

> [!IMPORTANT]
> 本 Skill 為**社群非官方**維護，資訊依據歐買尬全方位金流公開技術文件彙整。  
> 所有事實以 [`references/omg-official-api-spec.md`](omg-official-api-spec.md) 為 **Single Source of Truth**。若本檔案與該檔案衝突，以官方事實表為準。  
> 歐買尬（OMG）≠ 歐付寶（OPay）≠ 綠界（ECPay），三者為獨立不同公司。

## API 總覽

| # | API | 路徑 | 用途 |
|---|---|---|---|
| 1 | AioCheckOut | `/Cashier/AioCheckOut/V5` | 建立付款訂單 |
| 2 | QueryTradeInfo | `/Cashier/QueryTradeInfo/V5` | 查詢訂單狀態 |
| 3 | DoAction | `/CreditDetail/DoAction` | 信用卡關帳/退刷/取消/放棄（四種 Action）|
| 4 | QueryTrade | `/CreditDetail/QueryTrade/V2` | 查詢信用卡單筆明細 |
| 5 | QueryCreditCardPeriodInfo | `/Cashier/QueryCreditCardPeriodInfo` | 定期定額訂單查詢 |
| 6 | CreditCardPeriodAction | `/Cashier/CreditCardPeriodAction` | 定期定額停用 |

**環境 Domain：**

| 環境 | Domain | Webhook 發送來源 |
|---|---|---|
| 測試 | `payment-stage.funpoint.com.tw` | `postgate-stage.funpoint.com.tw` |
| 正式 | `payment.funpoint.com.tw` | `postgate.funpoint.com.tw` |

所有 API 共通要求：

- Method：`POST`；`Content-Type: application/x-www-form-urlencoded`
- Payload 必須包含 `CheckMacValue`；`EncryptType` 固定 `1`（SHA256）；`PaymentType` 固定 `aio`
- 僅支援 TLS 1.2 以上 HTTPS (443 port)
- 防火牆需綁 **domain name**（`postgate*.funpoint.com.tw`），**不得綁 IP**
- Webhook 商家必須於 body 回應純字串 `1|OK`（不加換行、不 JSON 化）

## 1. create_order（建立訂單）

用途：建立付款訂單，取得付款頁面 URL 或付款條碼。

### 主要欄位

| 欄位 | 型態 | 必填 | 說明 |
|---|---|---|---|
| MerchantID | String(10) | Y | 商店代號 |
| MerchantTradeNo | String(20) | Y | 商店訂單號，不可重複 |
| MerchantTradeDate | String(20) | Y | 建立時間，格式 `yyyy/MM/dd HH:mm:ss` |
| PaymentType | String(20) | Y | 固定值 `aio` |
| TotalAmount | Int | Y | 金額（整數 TWD） |
| TradeDesc | String | Y | 交易描述 |
| ItemName | String(400) | Y | 商品名稱，多品項以 `#` 分隔 |
| ReturnURL | String(200) | Y | 付款完成 callback URL |
| ChoosePayment | String(20) | Y | 付款方式（見下表） |
| ClientBackURL | String(200) | N | 客戶返回商店網址 |
| ItemURL | String(200) | N | 商品連結 |
| Remark | String(100) | N | 備註 |
| CheckMacValue | String(128) | Y | 簽章 |

### ChoosePayment 值（官方明定）

| 值 | 付款方式 | 說明 |
|---|---|---|
| `Credit` | 信用卡 + 銀聯卡 | 支援一次付清、分期、定期定額、記憶卡號；銀聯需申請開通 |
| `ATM` | ATM 虛擬帳號 | 預設 1 天，最長 60 天 |
| `CVS` | 超商代碼 | 預設 7 天（正式 10080 min / 測試 3012 min）|
| `BarcodeATM` | **超商快付** | 注意：名稱是「超商快付」，官方**沒有** `BARCODE` 這個值 |
| `AFTEE` | 先享後付 | 第三方後支付服務 |
| `ALL` | 消費者自選 | 搭配 `IgnorePayment`（`#` 分隔）可隱藏指定方式 |

> [!CAUTION]
> 官方禁止使用「超商代碼 CVS」與「超商快付 BarcodeATM」販售遊戲點數／遊戲虛寶，違者權益會被終止並追償損失。

### 付款方式特殊欄位

**信用卡分期**：

| 欄位 | 型態 | 說明 |
|---|---|---|
| CreditInstallment | String | 分期數，例：`3,6,12` |

**信用卡定期定額**：

| 欄位 | 型態 | 說明 |
|---|---|---|
| PeriodAmount | Int | 每期金額 |
| PeriodType | String | `D` / `M` / `Y` |
| Frequency | Int | 每幾個週期 |
| ExecTimes | Int | 總期數 |
| PeriodReturnURL | String | 後續扣款 callback URL |

**ATM**：

| 欄位 | 型態 | 說明 |
|---|---|---|
| ExpireDate | Int | 繳費期限（天） |
| PaymentInfoURL | String | 付款資訊通知 URL |

## 2. query_order（查詢訂單）

用途：依商店訂單號查詢訂單當前狀態。

### 主要欄位

| 欄位 | 型態 | 必填 | 說明 |
|---|---|---|---|
| MerchantID | String(10) | Y | 商店代號 |
| MerchantTradeNo | String(20) | Y | 商店訂單號 |
| TimeStamp | Int | Y | 當前 Unix timestamp |
| PlatformID | String(10) | N | 平台商代號，一般留空 |
| CheckMacValue | String(128) | Y | 簽章 |

### 回應主要欄位

| 欄位 | 說明 |
|---|---|
| TradeStatus | `0`=未付款 / `1`=已付款 / `10200095`=付款失敗 |
| TradeAmt | 交易金額 |
| PaymentDate | 付款時間 |
| PaymentType | 實際付款方式 |
| TradeNo | 歐買尬交易號 |

## 3. DoAction（信用卡請退款）

用途：對已授權的信用卡交易執行關帳、退刷、取消、放棄四種動作。

**端點：** `POST https://payment.funpoint.com.tw/CreditDetail/DoAction`  
**測試環境：** 因無法提供實際授權，故測試環境不支援此 API。

### 主要欄位

| 欄位 | 型態 | 必填 | 說明 |
|---|---|---|---|
| MerchantID | String(10) | Y | 商店代號 |
| MerchantTradeNo | String(20) | Y | 商店訂單號 |
| TradeNo | String(20) | Y | 歐買尬交易號 |
| Action | String(1) | Y | **`C` `R` `E` `N` 四種**，見下表 |
| TotalAmount | Int | Y | 金額 |
| PlatformID | String(10) | N | 專案合作平台商使用 |
| CheckMacValue | String(128) | Y | 簽章 |

### Action 四碼對照

| Action | 中文 | 適用階段 | 說明 |
|---|---|---|---|
| `C` | 關帳 | 已授權 | 向銀行請款 |
| `R` | 退刷 | 要關帳 / 已關帳 | 退回已關帳金額，可部份退；分期必須全額退 |
| `E` | 取消 | 要關帳 | 取消關帳、回到「已授權」 |
| `N` | 放棄 | 已授權 / 已取消 | 放棄授權，當日關帳前執行即不請款 |

**全額退款流程：**

- 已授權階段 → `Action=N`
- 要關帳階段 → `Action=E` 後 `Action=N`
- 已關帳階段 → `Action=R`

**部份退款：** 僅可於「要關帳／已關帳」以 `Action=R` 執行；分期訂單不支援部份退刷。

### 時段限制

> [!WARNING]
> **每日 20:15 ～ 20:30 禁止呼叫本 API**，因為歐買尬會於該時段自動關帳。

### 期限限制

- 授權後 **21 天內**必須完成手動關帳，否則無法以 API 方式關帳（需通知客服）。
- 超過 **90 天**未關帳的訂單將自動「放棄」，不請款。
- 帳戶餘額若低於退刷金額將無法退刷。

### 回應主要欄位

| 欄位 | 說明 |
|---|---|
| RtnCode | `1`=成功 / 其他為錯誤碼 |
| RtnMsg | 錯誤訊息 |

## 4. query_credit_card（查詢信用卡授權）

用途：查詢信用卡訂單的授權與請款明細。

### 主要欄位

| 欄位 | 型態 | 必填 | 說明 |
|---|---|---|---|
| MerchantID | String(10) | Y | 商店代號 |
| CreditRefundId | String(30) | Y | 歐買尬信用卡退款 ID |
| CreditAmount | Int | Y | 金額 |
| CreditCheckCode | String(30) | Y | 授權驗證碼 |
| CheckMacValue | String(128) | Y | 簽章 |

## 5. recurring_manage（定期定額管理）

用途：對定期定額訂閱執行取消或查詢。

### 主要欄位

| 欄位 | 型態 | 必填 | 說明 |
|---|---|---|---|
| MerchantID | String(10) | Y | 商店代號 |
| MerchantTradeNo | String(20) | Y | 定期定額原始訂單號 |
| Action | String(10) | Y | `Cancel` / `Status` |
| CheckMacValue | String(128) | Y | 簽章 |

## 6. query_trade_info（交易明細查詢）

用途：查詢特定期間內的交易明細報表。

### 主要欄位

| 欄位 | 型態 | 必填 | 說明 |
|---|---|---|---|
| MerchantID | String(10) | Y | 商店代號 |
| BeginDate | String(10) | Y | 起始日期 `yyyy-MM-dd` |
| EndDate | String(10) | Y | 結束日期 `yyyy-MM-dd` |
| PaymentType | String(20) | N | 付款方式篩選 |
| TimeStamp | Int | Y | 當前 Unix timestamp |
| CheckMacValue | String(128) | Y | 簽章 |

## Callback（Webhook）欄位

歐買尬於付款完成、退款成功等事件時，將以 form-data POST 至 `ReturnURL`。常見欄位：

| 欄位 | 說明 |
|---|---|
| MerchantID | 商店代號 |
| MerchantTradeNo | 商店訂單號 |
| TradeNo | 歐買尬交易號 |
| RtnCode | `1`=成功 / 其他為失敗 |
| RtnMsg | 訊息 |
| TradeAmt | 交易金額 |
| PaymentDate | 付款時間 |
| PaymentType | 付款方式 |
| PaymentTypeChargeFee | 手續費 |
| TradeDate | 交易建立時間 |
| SimulatePaid | `0`=實際付款 / `1`=測試模擬付款 |
| CheckMacValue | 簽章（必須驗證） |

**定期定額後續扣款** callback 將額外包含：

| 欄位 | 說明 |
|---|---|
| gwsr | 本期授權碼 |
| PeriodType | 週期類型 |
| Frequency | 頻率 |
| ExecTimes | 總期數 |
| TotalSuccessTimes | 已成功扣款次數 |
| TotalSuccessAmount | 已成功扣款總額 |

Webhook 處理必須先驗證 `CheckMacValue`，驗證失敗者不得寫入資料庫，且應記錄於稽核 log 以便追查。
