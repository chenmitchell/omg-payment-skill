# docs/images 說明

本資料夾存放 README 與其他文件所引用之截圖與圖檔。

## 規範

1. **不得包含個案商家之真實畫面**。若截自正式環境，必須以下列方式脫敏：
   - 商家名稱、MerchantID：以 `XXX商家`、`1000031` 覆蓋
   - 訂單號、交易號：以 `ORDER_2026XXXXX`、`OMG_2026XXXXX` 覆蓋
   - 金額：可保留
   - 客戶 Email、電話、姓名：必須以 `user@example.com`、`0900-000-000`、`王小明` 覆蓋
   - HashKey / HashIV：不得出現於任何截圖

2. **檔案命名**：使用小寫與連字號，例如 `claude-code-install.png`、`test-dashboard-green.png`。

3. **格式**：優先使用 PNG；若為 UI 截圖，寬度建議 1200–1600px，並以 `optipng` 壓縮。

4. **授權**：上傳至本 repo 之圖檔均視為依 MIT License 授權。

## 建議截圖清單

下列為 README 與 SETUP.md 可搭配之截圖。若貢獻者能補齊，請依上述規範處理後透過 PR 提交：

| 檔名建議 | 截自 | 內容 |
|---|---|---|
| `claude-code-install.png` | Claude Code 終端機 | 安裝 skill 之畫面 |
| `cursor-rules-install.png` | Cursor 設定頁 | `.cursor/rules` 目錄載入 Skill 之畫面 |
| `google-ai-studio-install.png` | Google AI Studio | System Instructions 貼入 Skill 內容之畫面 |
| `test-dashboard-green.png` | 瀏覽器 | 測試儀表板一鍵全鏈路測試六項綠燈之畫面 |
| `test-dashboard-red.png` | 瀏覽器 | CheckMacValue Error 顯示與修復建議之畫面 |
| `prod-dashboard-probes.png` | 瀏覽器 | 正式環境四項唯讀探測結果彙總之畫面 |
| `telegram-bot-notify.png` | Telegram | 付款成功事件推播之畫面 |
| `telegram-bot-refund-confirm.png` | Telegram | 退款二次確認選單與警示訊息之畫面 |
| `discord-bot-notify.png` | Discord | 付款事件 Embed 推播之畫面 |
| `discord-bot-refund-confirm.png` | Discord | 退款按鈕確認對話之畫面 |

貢獻者可依實際截圖補齊本清單。
