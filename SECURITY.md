# 安全政策

## 適用範圍

本安全政策適用於 `omg-payment-skill` repo 之程式碼、文件、模板與 skill 內容。本 skill 為社群維護，與 MacroWell OMG Digital Entertainment Co., Ltd. 無隸屬關係。

## 支援的版本

| 版本 | 支援狀態 |
|---|---|
| 2.x | 支援中 |
| 1.x | 僅接受安全性修正 |

## 回報安全性漏洞

若您發現本 skill 或其模板中有安全性問題（例：可能導致金鑰外洩、MAC 繞過、webhook 偽造、退款未授權執行等），請依下列方式回報：

1. **不要** 於 public issue 或 discussion 中直接貼出漏洞細節
2. 透過 GitHub 的 Private Vulnerability Reporting 功能提交
3. 或 Email 至 repo 維護者（聯絡方式見 repo 首頁）
4. 回報時請包含：
   - 受影響的檔案與版本
   - 重現步驟或 proof of concept
   - 可能的影響範圍
   - 建議的修正方向（可選）

## 回應時程

- 收到回報後 7 日內初步回覆
- 確認為有效漏洞後，視嚴重程度於 7 至 30 日內發布修正
- 修正發布後於 CHANGELOG 標註安全更新

本 skill 為社群維護，不保證修正時效。若為嚴重問題（例：可導致實際資金損失），建議回報者同時聯繫歐買尬官方客服。

## 使用者應遵守之安全原則

即使 skill 本身無漏洞，使用者整合時若未遵守下列原則，仍可能導致安全問題：

### 金鑰管理

- `HashKey`、`HashIV`、`ADMIN_TOKEN`、`TG_BOT_TOKEN`、`DISCORD_BOT_TOKEN` 等敏感資訊 **僅可寫入 `.env`**，不得提交至版本控制
- 正式環境金鑰不得與測試環境共用
- 正式環境金鑰須先至 <https://www.funpoint.com.tw/member/register> 申請會員並通過審核，於 FunPoint 商家後台取得
- 若金鑰疑似外流，應立即於 FunPoint 商家後台輪換並檢視近期交易與退款紀錄
- 不得將金鑰於對話、log、錯誤訊息中完整輸出

### Webhook 處理

- Webhook endpoint 必須驗證 `CheckMacValue`，未通過者不得寫入交易紀錄
- Webhook endpoint 不得依賴來源 IP 過濾作為主要驗證（歐買尬 IP 可能變動）
- Webhook handler 必須實作冪等性（見 `guides/05-webhook-idempotency.md`），避免重複處理

### Admin 驗證

- 所有 admin endpoint 必須透過 `Authorization: Bearer {ADMIN_TOKEN}` 驗證
- 退款 endpoint 不得開放為未驗證的 public endpoint
- 建議於正式環境啟用 IP 白名單或 VPN 限制

### 退款

- 退款必須經過二次確認（見 `guides/10-refund-safety.md`）
- 超過建議上限之退款必須寫入 audit log
- 退款操作者身分（`operator` 欄位）必須可追溯

### 資料保護

- 不得於 log 或 console 輸出完整信用卡號、CVV
- 客戶個資（姓名、電話、地址）僅於必要時存取
- 資料庫備份應加密儲存
- 遵守個資法第 27 條之安全維護義務

### 儀表板暴露

- 測試儀表板預設 bind 於 `127.0.0.1`，不得對外開放
- 正式環境儀表板 URL 必須加上 admin 認證
- 若需團隊共享，建議加上 VPN 或基本認證

## 禁止事項

以下行為會於本 skill 的 issue / PR 被拒絕：

1. 將正式環境金鑰、商家 ID 直接寫入範例
2. 將 skill 發布為「官方」或「由歐買尬提供」
3. 建議繞過 MAC 驗證之做法
4. 建議將退款 endpoint 開放為未驗證
5. 於正式環境以 `create_order` 執行健康檢查
6. 於文件中貼出任何真實的訂單號、客戶資料、後台截圖

## 感謝

感謝所有負責任地回報安全問題的研究者與使用者。經確認之有效回報將於 CHANGELOG 之 Security 節致謝（若回報者同意）。
