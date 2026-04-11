# 提示詞範例集（Prompt Examples）

本文件提供可直接複製至 AI 助手使用之提示詞，涵蓋本 Skill 支援的整合、除錯、法規、部署等情境。所有提示詞均以繁體中文撰寫，亦提供英文版供跨語系使用者參考。

> [!NOTE]
> 本 Skill 為社群維護之非官方資源。使用提示詞取得之輸出內容，建議與 <https://github.com/omgtwhub/> 之官方資源交叉驗證。

---

## 一、整合啟動類

### 1.1 一句話完成整合（最常用）

```
請依 omg-payment skill，幫我整合歐買尬金流，全部依預設，我經營線上課程。
```

### 1.2 指定框架

```
請依 omg-payment skill，幫我用 FastAPI 整合歐買尬金流，資料庫使用 SQLite。
```

```
請依 omg-payment skill，用 Express + TypeScript 整合歐買尬，資料庫是 PostgreSQL。
```

```
請依 omg-payment skill，用 Laravel 10 整合歐買尬，我要支援信用卡與 ATM。
```

### 1.3 指定商品類型

```
我要整合歐買尬金流，商品類型是數位下載（電子書），目標環境是測試與正式環境都要，依預設產出所有元件。
```

```
我經營會員訂閱服務（月費 NT$399），請用歐買尬 CreditPeriod 幫我整合定期定額。
```

```
我要賣實體商品（服飾），需要歐買尬信用卡分期 + ATM + 超商代碼，請依 skill 流程整合。
```

### 1.4 僅產出特定元件

```
請依 omg-payment skill 只幫我產出 webhook 冪等性處理的 FastAPI 程式碼，資料庫是 PostgreSQL。
```

```
請依 omg-payment skill 只幫我產出正式環境唯讀健康監控儀表板，不要產出其他元件。
```

```
請依 omg-payment skill 幫我產出 Telegram 通知機器人，不需要 Discord。
```

---

## 二、技術細節類

### 2.1 CheckMacValue

```
我 webhook 收到歐買尬的 callback，但 CheckMacValue 驗證一直失敗，請依 omg-payment skill 的 references/check-mac-value.md 幫我檢查我的簽名計算。
```

```
請幫我寫一個 Python 函式，依 omg-payment skill 的規範計算歐買尬的 CheckMacValue，並附上三組測試向量。
```

### 2.2 冪等性

```
我的歐買尬 webhook 偶爾會收到重複的 callback，導致訂單被寫入兩次，請依 omg-payment skill 的 guides/05-webhook-idempotency.md 幫我改成 race-safe 的版本。
```

### 2.3 退款

```
請依 omg-payment skill 幫我實作退款 API，要符合警示不阻擋原則：單筆超過 5 萬、當日超過 10 萬、當日超過 20 筆時只警示不拒絕。
```

### 2.4 查詢訂單

```
請依 omg-payment skill 幫我寫一個 admin endpoint，查詢今天所有訂單，按建立時間倒序，並附上 X-Total-Count header。
```

---

## 三、儀表板與通知機器人類

### 3.1 測試儀表板

```
請依 omg-payment skill 的 guides/06-test-dashboard.md 幫我產出測試環境單頁儀表板，要能一鍵執行六項全鏈路測試。
```

### 3.2 正式環境健康監控

```
我要正式環境的健康監控，但不能產生測試訂單。請依 omg-payment skill 的 guides/07-prod-dashboard.md 幫我實作四項唯讀探測。
```

### 3.3 Telegram 機器人

```
請依 omg-payment skill 的 guides/08-telegram-bot.md 幫我產出 Telegram bot，要有 /bind、/today、/orders、/refund 四個指令，退款要二次確認與警示訊息。
```

### 3.4 Discord 機器人

```
請依 omg-payment skill 的 guides/09-discord-bot.md 幫我產出 Discord bot，使用 slash command，退款用 Button 確認，並用 embed 顯示訂單資訊。
```

---

## 四、法規揭露類

### 4.1 服務條款

```
請依 omg-payment skill 的 guides/13-legal-tos.md 幫我產出服務條款範本，商家類型是線上課程，要涵蓋消費者保護法第 19 條之鑑賞期與其排除情形。
```

### 4.2 隱私權政策

```
請依 omg-payment skill 的 guides/14-legal-privacy.md 幫我產出隱私權政策，要涵蓋個人資料保護法第 8 條之告知事項。
```

### 4.3 退貨退款政策

```
請依 omg-payment skill 的 guides/15-legal-refund.md 幫我產出退貨退款政策，商品類型是數位下載，並說明各付款方式的退款到帳時程。
```

### 4.4 首頁與商品頁揭露

```
請依 omg-payment skill 的 guides/11-merchant-homepage.md 與 guides/12-product-page.md 幫我產出首頁頁尾與商品頁必要揭露區塊的 HTML 範本。
```

---

## 五、故障排除類

### 5.1 一般錯誤

```
歐買尬 webhook 我收到 payload 但 callback_logs 顯示 mac_valid=false，請依 omg-payment skill 的 guides/17-troubleshooting.md 幫我檢查。
```

```
我的歐買尬訂單建立成功但用戶付款後沒收到 webhook，請依 omg-payment skill 幫我逐步檢查。
```

### 5.2 歐買尬 vs 歐付寶誤判

```
我的程式一直連不上歐買尬的 API，我用的 host 是 payment.opay.tw，請檢查。
```

（AI 應立即指出 `opay.tw` 屬歐付寶而非歐買尬，並提示兩者為不同公司）

---

## 六、部署與環境類

### 6.1 切換至正式環境

```
我測試環境已全鏈路通過，請依 omg-payment skill 幫我列出切換到正式環境的 checklist，並確保我沒用 create_order 做健康檢查。
```

### 6.2 容器化

```
請依 omg-payment skill 幫我產出 Dockerfile 與 docker-compose.yml，包含 FastAPI 後端 + Telegram bot + Discord bot，資料庫用 PostgreSQL。
```

### 6.3 反向代理

```
請依 omg-payment skill 幫我產出 nginx 設定範例，處理 HTTPS 與 webhook 路徑 proxy。
```

---

## 七、英文版提示詞（English Prompts）

```
Using the omg-payment skill, help me integrate the OMG (歐買尬) payment gateway end-to-end with all default components. My business is an online course platform.
```

```
Using the omg-payment skill, generate a race-safe webhook handler for OMG callbacks in FastAPI with SQLAlchemy. Reference guides/05-webhook-idempotency.md.
```

```
Using the omg-payment skill, generate a read-only production health dashboard with 4 non-destructive probes. Do NOT use create_order. Reference guides/07-prod-dashboard.md.
```

```
Using the omg-payment skill, generate a Telegram bot with /bind, /today, /orders, /refund commands. The refund command must show warnings but never block execution. Reference guides/08-telegram-bot.md.
```

```
I'm getting CheckMacValue errors on my OMG webhook. Following omg-payment skill's references/check-mac-value.md, help me debug the signature calculation.
```

---

## 八、常見陷阱提醒

以下提示詞可用於提醒 AI 避免常見錯誤：

```
請確認你產出的內容是指向歐買尬（OMG / 茂為歐買尬）而非歐付寶（OPay），兩者為不同公司。
```

```
請勿在正式環境使用 create_order 作為定期健康檢查，這會在商家後台累積無效訂單。
```

```
HashKey 與 HashIV 必須只寫入 .env，不得出現在程式碼、commit、截圖或 README 中。
```

```
所有 admin endpoint 必須同步更新 Telegram 與 Discord bot 的選單，維持 API 與選單一致性。
```

---

## 貢獻

若您使用本 Skill 時發現某類提示詞特別有用，歡迎透過 PR 補充至本文件。PR 前請確認：

- 不得包含真實 MerchantID、HashKey、HashIV、商家名稱
- 提示詞應為通用情境，不得引用特定個案商家
- 若提示詞會觸發 AI 產生特定程式碼，請附上對應之 guide 檔名
