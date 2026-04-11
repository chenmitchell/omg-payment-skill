# Guide 06 — 測試環境儀表板

本指南說明如何建置歐買尬測試環境的整合驗證儀表板。測試儀表板的目的在於提供一鍵式的完整鏈路驗證，涵蓋從訂單建立、簽名驗證、HTTP 請求發送、訂單查詢、到退款簽名計算的全流程。

## 驗證鏈路

測試儀表板應依序執行下列步驟，並記錄每一步的結果與延遲：

1. **create_order 簽名與發送**：建立測試訂單 payload，計算 CheckMacValue，將 payload POST 至測試環境 API host
2. **CheckMacValue 驗證**：對步驟 1 的 payload 重新計算 CheckMacValue，與實際送出的值比對，確認一致
3. **query_order**：使用步驟 1 取得的訂單號，向測試環境發送 `query_order` 請求，確認可查詢到訂單資料
4. **refund 簽名**：使用步驟 1 的訂單號建立退款 payload，計算 CheckMacValue（本步驟僅計算簽名，不發送 HTTP 請求）
5. **Webhook 自我驗證**：以建構好的假 payload 驗證本機 webhook 接收器能否正確驗證 MAC 並回傳 200

每一步的結果應分別標示為綠燈（成功）、黃燈（警告）、紅燈（失敗），並記錄延遲毫秒數。

## 已提供之模板

本 repo 於 `templates/omg-test-console/` 提供可直接運行的測試儀表板：

```
templates/omg-test-console/
├── backend.py       FastAPI 後端（提供測試 API 與 webhook 接收器）
├── console.html     單頁儀表板介面
└── .env.example     環境變數範本
```

### 啟動方式

```bash
cd templates/omg-test-console
pip install fastapi uvicorn httpx python-dotenv
cp .env.example .env
# 編輯 .env，填入 OMG_MERCHANT_ID、OMG_HASH_KEY、OMG_HASH_IV、OMG_API_HOST_STAGE
python backend.py
```

啟動後於瀏覽器開啟 `http://localhost:8787/` 即可載入 console.html。

### 儀表板功能

| 功能 | 對應按鈕 | 後端 endpoint |
|---|---|---|
| 一鍵全鏈路測試 | 「一鍵全鏈路測試」 | `POST /api/test/full-chain` |
| 建立訂單（單步測試） | 「create_order」 | `POST /api/test/create-order` |
| 查詢訂單（單步測試） | 「query_order」 | `POST /api/test/query-order` |
| 退款簽名計算 | 「refund 簽名」 | `POST /api/test/refund-sign` |
| CheckMacValue 計算 | 「計算 MAC」 | `POST /api/test/mac-calculate` |
| CheckMacValue 驗證 | 「驗證 MAC」 | `POST /api/test/mac-verify` |
| Webhook 重送模擬 | 「重送 N 次」 | `POST /api/test/webhook-simulate` |
| Log 檢視與下載 | 「重新載入」、「下載 JSON」 | `GET /api/test/logs` |

### Webhook 重送模擬

此功能對本機 `/webhook` 接收器並行發送 N 次相同 payload，用以驗證冪等性實作是否正確。預期結果為：N 次請求全部回傳 200 OK，但實際寫入資料庫的 callback 紀錄僅有 1 筆，其餘 N-1 筆應為 `early-dup` 或 `absorbed`。

此驗證機制涵蓋 `guides/05-webhook-idempotency.md` 中定義的所有冪等性路徑，是上線前的必要測試。

## 付款方式覆蓋測試

測試儀表板提供下列付款方式之獨立測試按鈕，以確保各方式均可正確建立訂單：

- 信用卡一次付清（`ChoosePayment=Credit`）
- 信用卡分期 3 / 6 / 12 / 18 / 24 / 30 期（`ChoosePayment=Credit` + `CreditInstallment`）
- 信用卡定期定額（`ChoosePayment=Credit` + `PeriodAmount/PeriodType/Frequency/ExecTimes`）
- ATM 虛擬帳號（`ChoosePayment=ATM`）
- 超商代碼（`ChoosePayment=CVS`）
- 超商快付（`ChoosePayment=BarcodeATM` —— 注意：官方名稱是「超商快付」，`BarcodeATM` 是唯一合法值，沒有 `BARCODE`）
- AFTEE 先享後付（`ChoosePayment=AFTEE`）

建議於整合完成後，逐項執行所有付款方式的測試，確保各方式的 MAC 計算與 HTTP POST 均正常。

## Log 記錄

所有測試操作均寫入 in-memory ring buffer（最多保留 500 筆），可於儀表板下方 log panel 檢視。log 格式為：

```
[OK] full-chain → {"chain": [...], "total_ms": 1234}
[OK] create-order → {"url": "...", "status": 200, "latency_ms": 145}
[WARN] mac-verify → {"received": "ABC", "expected": "XYZ", "match": false}
[ERROR] create-order → {"url": "...", "error": "timeout"}
```

可透過「下載 JSON」按鈕將 log 匯出為 JSON 檔，便於事後分析或提交給開發者。

## 安全提醒

1. 測試儀表板僅應連線至測試環境 API host，不得指向正式環境
2. `.env` 不得提交至 repo（已於 `.gitignore` 排除）
3. 儀表板預設 bind 至 `127.0.0.1`，不對外開放
4. 若需於團隊內部共享，建議加上基本認證或 VPN 限制
