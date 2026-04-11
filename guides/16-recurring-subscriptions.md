# Guide 16 — 信用卡定期定額訂閱

本指南說明歐買尬信用卡定期定額功能的整合方式，適用於訂閱制商家（例：月訂閱課程、會員費、SaaS 訂閱）。

## 功能說明

信用卡定期定額允許商家於取得消費者首次授權後，依預設週期自動扣款。歐買尬提供以下週期設定：

- 每月扣款
- 每兩個月扣款
- 每三個月扣款
- 每半年扣款
- 每年扣款

首次授權時，歐買尬系統與發卡銀行確認卡片有效後即建立授權紀錄，後續依週期由歐買尬自動觸發扣款並以 webhook 通知商家。

## 建立訂閱訂單

建立定期定額訂單時，`PaymentType` 參數設定為 `CreditPeriod`，並於 payload 中加入下列定額相關欄位：

| 欄位 | 說明 | 範例 |
|---|---|---|
| `PeriodAmount` | 每期扣款金額（TWD） | `500` |
| `PeriodType` | 週期類型（`D`=日 / `M`=月 / `Y`=年） | `M` |
| `Frequency` | 每幾個週期扣款一次 | `1`（每月一次）|
| `ExecTimes` | 總執行次數 | `12`（扣款 12 期後停止）|
| `PeriodReturnURL` | 後續扣款成功之 callback URL | `https://example.com/webhook` |

範例 payload（節錄）：

```python
params = {
    "MerchantID": settings.OMG_MERCHANT_ID,
    "MerchantTradeNo": order_no,
    "MerchantTradeDate": now_str,
    "PaymentType": "aio",
    "TotalAmount": "500",
    "TradeDesc": "月訂閱",
    "ItemName": "月訂閱會員",
    "ReturnURL": settings.WEBHOOK_URL,
    "ChoosePayment": "Credit",
    "PeriodAmount": "500",
    "PeriodType": "M",
    "Frequency": "1",
    "ExecTimes": "12",
    "PeriodReturnURL": settings.WEBHOOK_URL,
}
params["CheckMacValue"] = compute_check_mac(params, hash_key, hash_iv)
```

## Webhook 處理差異

定期定額之 callback 與一般訂單 callback 在結構上有下列差異：

1. **首次授權**：與一般 Credit 交易相同，包含授權碼、卡號後四碼等欄位
2. **後續扣款成功**：每期扣款成功後，歐買尬將送出一筆新的 callback，內含下列特有欄位：
   - `gwsr`：該期的扣款授權碼
   - `PeriodType`、`Frequency`、`ExecTimes`：訂閱條件
   - `TotalSuccessTimes`：至今成功扣款次數
   - `TotalSuccessAmount`：至今成功扣款總額
3. **扣款失敗**：若該期扣款被拒絕，歐買尬會標記失敗並可能於一段時間後自動重試

Webhook handler 處理定期定額時，應：

1. 驗證 `CheckMacValue`（與一般訂單相同）
2. 依 `MerchantTradeNo` 判斷對應之原訂閱訂單
3. 為該期扣款建立獨立的 `subscription_charge` 紀錄，記錄 `period_no`、`gwsr`、`amount`、`charged_at`
4. 更新原訂閱之累計扣款次數與金額
5. 若該期為取消或失敗，應通知客服或使用者

## 建議資料庫 schema

```sql
CREATE TABLE IF NOT EXISTS subscriptions (
    id                BIGSERIAL PRIMARY KEY,
    order_no          VARCHAR(40) UNIQUE NOT NULL,
    user_id           VARCHAR(64),
    plan_name         VARCHAR(100),
    period_amount     INTEGER NOT NULL,
    period_type       VARCHAR(2)  NOT NULL,
    frequency         INTEGER NOT NULL,
    exec_times        INTEGER NOT NULL,
    total_success     INTEGER NOT NULL DEFAULT 0,
    total_amount      INTEGER NOT NULL DEFAULT 0,
    status            VARCHAR(20) NOT NULL DEFAULT 'active',
    next_charge_at    TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS subscription_charges (
    id                BIGSERIAL PRIMARY KEY,
    subscription_id   BIGINT REFERENCES subscriptions(id),
    period_no         INTEGER NOT NULL,
    amount            INTEGER NOT NULL,
    gwsr              VARCHAR(40),
    status            VARCHAR(20) NOT NULL,
    charged_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (subscription_id, period_no)
);
```

`subscription_charges.UNIQUE (subscription_id, period_no)` 為重要之冪等性保障，確保同一期不會被重複記錄。

## 取消訂閱

歐買尬提供定期定額取消 API（`recurring_manage`），允許商家於消費者要求或預期結束前提前終止訂閱。取消後不再觸發後續扣款。

建議於 admin 介面提供「取消訂閱」按鈕，執行流程：

1. 操作者點擊取消按鈕
2. 系統顯示確認對話框（二次確認），列出剩餘期數與對應金額
3. 確認後呼叫歐買尬 `recurring_manage` API
4. 更新本地 `subscriptions.status` 為 `cancelled`
5. 寫入稽核 log（`subscription_audit_log`）
6. 若符合，發送通知至 Telegram / Discord bot

## 訂閱者權益與法規

依消費者保護法相關規定，訂閱制商家應於商品頁與服務條款明確揭露：

- 每期金額、扣款週期、總期數
- 首次扣款日與後續扣款日
- 自動續約或到期結束之條件
- 取消流程與取消後之退款政策
- 升級 / 降級方案之處理方式
- 未成功扣款之通知與處理方式

建議於使用者儀表板提供「當前訂閱狀態」、「下次扣款日」、「取消訂閱」之自助操作，減少客服負擔並提升透明度。

## 首次付款失敗之處理

首次授權失敗時，定期定額訂閱不會建立。商家應於前端妥善處理此情境：

1. 向使用者顯示明確失敗原因（卡片拒絕、餘額不足、CVV 錯誤等）
2. 允許使用者更換卡片後重試
3. 不得自動重試相同卡片（避免觸發銀行風控）
4. 若使用者放棄，應清理相關暫存資料

## 後續扣款失敗之處理

定期扣款期間若某一期失敗，建議流程：

1. 記錄失敗原因與 `subscription_charges.status = 'failed'`
2. 立即通知使用者（Email / Bot 推播）
3. 提供「更換付款方式」之操作路徑
4. 若連續失敗次數達上限（建議 2 至 3 次），自動暫停訂閱並通知客服

## 安全提醒

1. 訂閱金額、扣款週期等參數一旦建立即由歐買尬保存，商家本地資料僅用於顯示，實際扣款以歐買尬記錄為準
2. 訂閱相關 webhook 必須與一般訂單 webhook 使用同一套 MAC 驗證邏輯
3. 取消訂閱為不可逆操作，建議保留取消前之完整訂閱紀錄於 audit log
4. 定期於後台列出「活躍訂閱」、「下次扣款日異常」等報表，確保系統與歐買尬雙方紀錄一致
