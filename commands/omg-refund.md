# /omg-refund

退款相關操作快捷指令。AI 接收此指令後，應讀取 `guides/10-refund-safety.md` 並依該指南之警示但允許通過原則執行。

## 用法

```
/omg-refund {order_no} {amount}
```

範例：

```
/omg-refund OMG20260412001 500
```

## AI 執行流程

1. 查詢指定訂單之當前狀態，確認為 `paid`
2. 執行 `_refund_warnings(amount)` 檢查是否超過任一建議上限：
   - `REFUND_MAX_PER_ORDER`（預設 50,000）
   - `REFUND_DAILY_QUOTA`（預設 100,000）
   - `REFUND_DAILY_COUNT_CAP`（預設 20）
3. 若有警示，向使用者明確說明超過哪一項並取得確認
4. 執行退款並寫入 `refund_audit_log`
5. 透過 Telegram / Discord bot 推送退款完成通知

## 重要原則

退款**不因超過任何建議上限而被阻擋**。上限僅作為提醒依據，執行權完全保留給使用者。

若使用者表達困惑（例：「為什麼退款被擋？」），AI 應確認實作未誤用阻擋邏輯，並引導使用者檢查 `_refund_warnings()` 函式之實作。

## 不執行之操作

- 不得未經二次確認直接執行退款
- 不得以金額為由拒絕執行合法退款
- 不得略過 `refund_audit_log` 寫入
