# Guide 17 — 故障排除與常見問題

本指南整理歐買尬金流整合過程中常見的錯誤與排除方式。若遇到本指南未涵蓋之問題，請依 `guides/06-test-dashboard.md` 執行全鏈路測試，並參考 log 內容進一步判斷。

## 常見概念混淆

### 歐買尬 vs 歐付寶

**這是最常見且最關鍵的混淆**。歐買尬（OMG / MacroWell OMG Digital Entertainment）與歐付寶（OPay / O'Pay）為兩家獨立公司，名稱相近但並無任何隸屬或合作關係。

| 項目 | 歐買尬（OMG） | 歐付寶（OPay） |
|---|---|---|
| 英文名 | MacroWell OMG | O'Pay Electronic Payment |
| 服務商 | MacroWell OMG Digital Entertainment Co., Ltd. | 歐付寶電子支付股份有限公司 |
| CheckMacValue 演算法 | SHA256 | SHA256 |
| API host | 歐買尬官方文件 | 與歐買尬不同 |

本 Skill 所有設定、範例、host 均指向 **歐買尬（OMG）**。若您於歷史資料、舊文件或 AI 產出之內容中看到「歐付寶」字樣且脈絡為 OMG 整合，該處極可能為錯誤引用，應改為「歐買尬」。

**特別提醒**：本 Skill v2.0.0 之主要修正項目之一即為「移除舊版中部分段落誤用『歐付寶』字樣」。若您曾使用過本 Skill 舊版，請務必重新確認 `.env` 中之 host 與金鑰是否指向歐買尬而非歐付寶。

## CheckMacValue 相關錯誤

### 錯誤訊息：「CheckMacValue Error」或回應碼 `10100050`

**可能原因**：

1. `HashKey` 或 `HashIV` 與歐買尬後台不一致
2. payload 欄位有漏掉（例：TimeStamp 未補上當前秒數）
3. 金額型態錯誤（例：送出 `"100.00"` 而非 `"100"`）
4. 中文欄位之 URL encoding 方式與歐買尬預期不符

**排除步驟**：

1. 於測試儀表板執行「計算 MAC」並逐欄位對照 payload
2. 確認 payload 中所有欄位值為字串（非整數、非浮點數）
3. 確認中文商品名稱經過 `urllib.parse.quote()` 編碼後送出
4. 確認 `HashKey` 與 `HashIV` 前後無多餘空白
5. 若多次失敗，將 payload 於測試儀表板之「驗證 MAC」按鈕反向驗證

`references/check-mac-value.md` 有完整的演算法與測試向量可供對照。

### 錯誤訊息：本機計算出的 MAC 與歐買尬回傳的 MAC 不一致

**原因**：通常為 payload 字典順序錯誤。歐買尬的 MAC 計算要求欄位依 **字典序** 排序後再串接。

**排除步驟**：

1. 確認 `compute_check_mac()` 內部使用 `sorted(params.items())`
2. 確認排序時 key 為字串（不是 bytes）
3. 確認串接格式為 `HashKey=xxx&K1=V1&K2=V2&...&HashIV=yyy`
4. 確認雜湊前先執行 URL encoding、小寫化
5. 最終結果須為大寫 hex

## Webhook 相關錯誤

### 問題：歐買尬表示已送出 webhook，但本機後端未收到

**可能原因**：

1. Webhook URL 未對外網公開（本機 localhost 無法被歐買尬存取）
2. 伺服器防火牆擋掉歐買尬 IP
3. Webhook URL 填寫錯誤（例：多了尾斜線或大小寫不符）

**排除步驟**：

1. 於歐買尬後台確認 ReturnURL 為完整可存取的 HTTPS URL
2. 於本機開發時使用 ngrok 或類似工具將本機服務暴露為公開 URL
3. 透過 `curl` 直接測試 webhook URL 是否可被外部呼叫
4. 檢視伺服器存取 log，確認是否有來自歐買尬的請求

### 問題：同一筆訂單收到多次 webhook，資料庫出現重複訂單

**原因**：Webhook handler 未實作冪等性，或 `idempotency_key` 計算不穩定。

**排除步驟**：

1. 參考 `guides/05-webhook-idempotency.md` 實作 race-safe handler
2. 確認 `payment_transactions.idempotency_key` 欄位設為 UNIQUE
3. 執行 `guides/06-test-dashboard.md` 之 webhook 重送模擬，驗證 N 次請求僅一筆紀錄

### 問題：Webhook 回傳 200，但資料庫未寫入任何紀錄

**可能原因**：

1. MAC 驗證失敗，handler 直接回傳 200 但未處理（此為錯誤行為）
2. 例外處理吞掉錯誤訊息
3. 資料庫交易未 commit

**排除步驟**：

1. 於 handler 中加入 log，確認執行路徑
2. MAC 驗證失敗時應回傳 400，而非 200
3. 確認 `session.commit()` 被呼叫
4. 檢查 `callback_logs` 表是否有對應紀錄

## 訂單查詢相關

### 錯誤訊息：「查無此筆交易」

**正常情境**：

- 正式環境唯讀探測時（使用假交易號）— 此為預期行為
- 訂單剛建立尚未同步至歐買尬查詢服務（通常於 1 分鐘內同步）

**異常情境**：

- 訂單確實存在但查詢回傳查無 → 確認 `MerchantID` 是否正確
- 測試環境訂單於正式環境查詢 → 確認 host 是否切換正確

## 退款相關

### 錯誤訊息：「訂單狀態不允許退款」

**可能原因**：

- 訂單尚未付款完成
- 訂單已全額退款
- 訂單為 ATM 虛擬帳號且尚未對帳入帳

**排除步驟**：

1. 於管理後台確認訂單最新狀態
2. 若為 ATM 訂單，等待入帳後再執行退款
3. 若為已退款，檢視 `refund_audit_log` 確認歷史

### 問題：退款超過建議上限，bot 發出警示但應該通過

**正常行為**：本 Skill 之設計原則為「警示但允許通過」，詳見 `guides/10-refund-safety.md`。當退款超過任一建議上限時，bot 將顯示警示但仍允許執行。若遭遇阻擋，表示實作有誤，應檢視 `_refund_warnings()` 函式是否回傳列表而非 `(False, reason)` tuple。

### 問題：執行退款後，消費者信用卡未立即入帳

**說明**：這是正常現象。信用卡退款依發卡銀行作業時間，通常需 7 至 14 個工作日。應於客服回應與 FAQ 中明確說明此時程。

若超過 14 個工作日仍未入帳，請：

1. 於管理後台確認退款狀態為成功
2. 取得歐買尬提供之退款交易號
3. 請消費者向發卡銀行查詢

## 測試儀表板啟動問題

### `python backend.py` 無法啟動，顯示 `ModuleNotFoundError`

**原因**：未安裝相依套件。

**排除步驟**：

```bash
pip install -r requirements.txt
```

若已安裝但仍錯誤，可能為 Python 虛擬環境切換問題。確認當前終端機使用的 Python 與安裝套件的 Python 一致：

```bash
which python       # macOS / Linux
where python       # Windows
```

### 儀表板開啟後空白或無反應

**可能原因**：

1. 瀏覽器 console 有 JavaScript 錯誤（可按 F12 檢視）
2. `console.html` 路徑錯誤（確認與 `backend.py` 於同一資料夾）
3. `.env` 金鑰有誤導致後端無法初始化

**排除步驟**：

1. 開啟瀏覽器開發者工具檢視 console log
2. 檢視終端機之 `uvicorn` 輸出
3. 於網址列手動嘗試 `http://127.0.0.1:8787/api/test/logs` 確認後端 API 可回應

## Bot 綁定問題

### 問題：Telegram 或 Discord bot 無法接收訊息

**可能原因**：

1. Bot token 錯誤或已被輪換
2. Bot 未被加入目標 channel
3. 綁定的 admin token 與後端不一致
4. Notify server port 被防火牆擋住

**排除步驟**：

1. 於 TG / Discord 私訊 bot，確認其是否回應 `/start`
2. 檢視 bot 執行之終端機有無錯誤訊息
3. 使用 `curl http://127.0.0.1:9876/notify/paid` 直接測試 notify server
4. 確認 `.env` 之 `ADMIN_TOKEN` 與後端一致

## 其他常見問題

### 如何切換至正式環境

0. 先至 <https://www.funpoint.com.tw/member/register> 申請 OMG 會員並通過審核，於 FunPoint 商家後台取得正式環境的 `MerchantID`、`HashKey`、`HashIV`
1. 於 `.env` 中將 `ENVIRONMENT=prod`
2. 將 `OMG_API_HOST_PROD` 設定為 `https://payment.funpoint.com.tw`
3. 將 `OMG_MERCHANT_ID`、`OMG_HASH_KEY`、`OMG_HASH_IV` 替換為正式環境金鑰（嚴禁 commit 至任何 git 倉庫）
4. 將儀表板切換至唯讀探測模式（見 `guides/07-prod-dashboard.md`）
5. 不得於正式環境執行 `create_order` 作為健康檢查

### 如何同時整合多家金流服務商

本 Skill 僅覆蓋歐買尬，但架構設計上可與其他金流共存：

1. `payment_transactions.provider` 欄位區分不同服務商
2. 各金流服務商的 webhook endpoint 應獨立（例：`/webhook/omg`、`/webhook/other`）
3. `idempotency_key` 計算時應加入 `provider` 前綴避免碰撞
4. admin 介面應以 provider 為篩選條件

### 如何取得實際使用情況數據

建議每月產出下列報表：

- 當月訂單數、金額、成功率
- 付款方式分佈
- 退款次數、金額、超過建議上限之退款清單
- 健康探測成功率（正式環境唯讀探測儀表板）

報表可透過 cron job 自動產出並 Email 或 Bot 推送。

## 仍無法解決時

若上述步驟均未能排除問題，建議依下列順序尋求協助：

1. 於測試儀表板下載 log JSON，檢視詳細請求與回應
2. 將 log 中之敏感資訊（金鑰、訂單號、客戶資訊）遮蔽後，提交至本 Skill 的 GitHub Issue
3. 若為歐買尬服務本身之問題，請聯繫歐買尬商家客服並附上完整交易編號

本 Skill 為社群維護，問題回報將依 issue 優先級處理，不保證回應時限。
