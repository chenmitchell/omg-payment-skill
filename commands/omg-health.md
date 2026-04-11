# /omg-health

建置或查詢金流健康監控儀表板。

## 用法

```
/omg-health                    查詢目前健康狀態
/omg-health setup              建置健康監控儀表板（依環境自動選擇）
/omg-health setup prod         建置正式環境唯讀探測儀表板
/omg-health setup stage        建置測試環境全鏈路儀表板
```

## AI 執行流程

### 查詢模式

1. 讀取 `health_log` 表之最近 24 小時紀錄
2. 計算整體 uptime 與各探測方法之成功率
3. 列出最近一次失敗之錯誤訊息
4. 若 uptime 低於 95%，建議使用者檢查故障排除章節

### 建置模式

**測試環境**（參考 `guides/06-test-dashboard.md`）：

- 部署 `templates/omg-test-console/backend.py` 與 `console.html`
- 提供一鍵全鏈路測試（5 個步驟的綠黃紅燈狀態）
- 支援 webhook 重送模擬

**正式環境**（參考 `guides/07-prod-dashboard.md`）：

- 部署四項唯讀探測：TCP handshake、query_order(fake)、refund sign、webhook MAC self-verify
- 建立 `health_log` 表
- 設定每小時背景 job
- 告警整合至 Telegram / Discord bot

## 重要原則

**正式環境嚴禁使用 `create_order` 進行健康檢查**。任何於正式環境觸發 `create_order` 之需求都應被拒絕，並向使用者說明原因（會污染商家後台之訂單列表）。
