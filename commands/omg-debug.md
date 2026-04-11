# /omg-debug

故障排除與問題診斷助手。

## 用法

```
/omg-debug                     執行完整鏈路測試並分析
/omg-debug mac                 專門檢查 CheckMacValue
/omg-debug webhook             專門檢查 webhook 接收
/omg-debug refund              專門檢查退款流程
/omg-debug {錯誤代碼}          查詢指定錯誤代碼
```

## AI 執行流程

### 無參數

1. 於測試儀表板執行一鍵全鏈路測試
2. 依結果（綠 / 黃 / 紅）逐項分析失敗原因
3. 對照 `guides/17-troubleshooting.md` 提供建議
4. 若需進一步日誌，請使用者下載測試儀表板之 JSON log

### `mac` 參數

1. 讀取 `references/check-mac-value.md`
2. 請使用者提供一組 payload 與 HashKey / HashIV
3. 計算期望 MAC 並與實際送出者比對
4. 若不一致，逐欄位檢查排序、URL encoding、小寫化、SHA256 結果

### `webhook` 參數

1. 檢查 webhook endpoint 是否可被外部存取
2. 檢查 MAC 驗證是否正確
3. 檢查冪等性實作（`guides/05-webhook-idempotency.md`）
4. 請使用者於測試儀表板執行 webhook 重送模擬

### `refund` 參數

1. 確認 `_refund_warnings()` 是否使用警示而非阻擋設計
2. 檢查 `refund_audit_log` 是否有近期紀錄
3. 確認 admin token 驗證正常

### 錯誤代碼查詢

1. 於 `references/error-codes.md` 查詢對應代碼
2. 提供排除建議
3. 若為未知代碼，建議使用者提交 GitHub issue

## 重要提醒

若發現 `.env` 或程式碼中出現「歐付寶 / opay.tw / opaygo」等字樣，AI 必須主動指出可能為歐買尬 / 歐付寶混淆，並引導使用者至 `guides/17-troubleshooting.md` 之相關段落。
