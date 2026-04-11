# MIGRATION NOTES — 從 v1.x 升級至 v2.0.0

本文件說明從 `omg-payment-skill` v1.x 升級至 v2.0.0 時需要注意的變更與遷移步驟。

## 重大變更摘要

v2.0.0 為結構性重寫，幾乎所有檔案均有調整。若您已於實際專案中使用 v1.x 的內容，升級前請先閱讀本文件並規劃遷移時間。

### 結構變更

v1.x 以單檔 `SKILL.md` 為主，v2.0.0 將內容拆解至下列目錄：

```
v1.x                      →    v2.0.0
SKILL.md（單檔）           →    SKILL.md（骨架） + guides/*.md + references/*.md + commands/*.md
（無）                     →    templates/omg-test-console/
（無）                     →    templates/telegram-bot/
（無）                     →    templates/discord-bot/
（無）                     →    scripts/
（無）                     →    test-vectors/
```

### 修正「歐付寶 / 歐買尬」混淆

v1.x 部分段落誤將「歐買尬（OMG / MacroWell OMG）」寫為「歐付寶（OPay）」。兩者為不同公司。

v2.0.0 已全面修正為「歐買尬」。若您於舊版產出之 `.env` 或程式碼中仍包含歐付寶相關設定，請依下列順序處理：

1. 於歐買尬商家後台重新取得正確的 HashKey / HashIV
2. 更新 `.env` 中之 `OMG_API_HOST_STAGE` 與 `OMG_API_HOST_PROD`
3. 確認 webhook URL 與實際商家設定一致
4. 執行 `templates/omg-test-console/` 之全鏈路測試驗證
5. 若已有線上交易，於下一期對帳時特別確認數字正確

### 退款機制設計原則調整

v1.x 之退款機制為硬性阻擋（超過上限直接拒絕執行），v2.0.0 改為警示但允許通過。

若您已實作 v1.x 的退款邏輯，升級時需要：

1. 將 `_check_refund_quota()` 函式改名為 `_refund_warnings()`
2. 回傳型別由 `(bool, str)` 改為 `list[str]`
3. 呼叫端不再以回傳值決定是否繼續，而是將 warnings 顯示於確認對話框並保留執行權
4. `refund_audit_log` 表需新增 `exceeded_single`、`exceeded_daily`、`exceeded_count` 三個布林欄位
5. 執行退款時無論是否超過上限，均寫入 audit log

詳細設計原則見 `guides/10-refund-safety.md`。

### 正式環境健康檢查機制

v1.x 於正式環境使用 `create_order` 作為健康檢查，會於商家後台累積未付款訂單。

v2.0.0 將此行為列為禁止事項，並提供四項唯讀探測方法替代：

- TCP handshake
- query_order 以假交易號查詢
- refund 簽名自我驗證
- webhook MAC 自我驗證

若您有排程 job 於正式環境呼叫 `create_order`，請立即停用並依 `guides/07-prod-dashboard.md` 調整為唯讀探測。

**已累積的無效訂單處理建議**：

1. 查詢後台近 N 日之未付款訂單，辨識出探測產生的訂單（通常金額固定或商品名稱固定）
2. 標註為 `cancelled` 狀態並加註原因
3. 若數量龐大，聯繫歐買尬商家客服協助清理

### Webhook 冪等性實作

v1.x 之 webhook handler 未必包含完整的 race-safe 實作。v2.0.0 於 `guides/05-webhook-idempotency.md` 定義了標準的 race-safe 流程，包含：

- `idempotency_key` 計算規則
- `SELECT FOR UPDATE` 搭配 rowcount 吸收
- 早期重複檢測與晚期重複檢測
- 金額不一致之處理

若您 v1.x 的 handler 僅以「檢查訂單是否存在 → 更新或插入」之簡單模式實作，強烈建議升級至 v2.0.0 的 race-safe 版本。在高並發情境下，舊模式可能導致重複寫入或 race condition。

### Bot 結構變更

v1.x 之 bot 範例為單檔簡易版本。v2.0.0 採 Bind / Notify / Menu 三段結構：

- **Bind**：獨立的綁定流程與 `bot_subscribers` 表
- **Notify**：專門的 notify server（port 9876 / 9877）
- **Menu**：所有 admin endpoint 對應之指令或 button

若您 v1.x 的 bot 僅實作了 notify 功能，v2.0.0 升級時需補齊 bind 與 menu 兩段。尤其是 menu 需與後端 admin endpoint 完全對應（見 `SKILL.md` §0.4.1 硬性規則）。

## 遷移步驟

1. **備份既有資料**：升級前請備份資料庫、`.env`、既有程式碼
2. **評估受影響範圍**：對照上述變更檢查哪些項目需要處理
3. **分階段升級**：
   - 第一階段：修正「歐買尬 / 歐付寶」混淆
   - 第二階段：調整 webhook handler 至 race-safe 版本
   - 第三階段：調整退款機制為警示但允許通過
   - 第四階段：停用正式環境 `create_order` 健康檢查
   - 第五階段：補齊 bot 的 Bind 與 Menu 段落
4. **測試環境驗證**：每個階段完成後於測試環境執行全鏈路測試
5. **正式環境部署**：於非尖峰時段部署，並密切監控首幾日之交易

## 不向後相容項目

- `SKILL.md` v1.x 版本將不再接受新功能更新，僅接受安全性修正
- v1.x 之檔案結構與 v2.0.0 不相容，直接覆蓋可能導致部分功能失效
- 建議新的整合專案直接使用 v2.0.0，不建議於舊專案中混用兩個版本

## 需要協助

若您於升級過程遭遇問題：

1. 參考 `guides/17-troubleshooting.md` 查詢常見錯誤
2. 於 GitHub Issues 提交問題描述
3. 若為涉及實際資金之關鍵問題，建議同時聯繫歐買尬商家客服

本 skill 為社群維護，不保證升級支援時效。請預留充足的遷移時間並做好回滾計畫。
