# /omg-bot

建置 Telegram 或 Discord 通知機器人。

## 用法

```
/omg-bot telegram        建置 Telegram bot
/omg-bot discord         建置 Discord bot
/omg-bot both            同時建置兩者（預設）
```

## AI 執行流程

1. 讀取 `guides/08-telegram-bot.md` 或 `guides/09-discord-bot.md`
2. 產出對應之 `templates/telegram-bot/` 或 `templates/discord-bot/` 檔案
3. 依三段結構實作：
   - **Bind**：`/bind` 指令綁定 admin token
   - **Notify**：推送付款成功、退款完成、webhook 失敗、健康告警
   - **Menu**：提供所有 admin endpoint 對應之指令或 button
4. 產出 `.env.example` 並列出必要欄位
5. 提供一行式啟動指令

## 硬性規則

**所有 admin endpoint 必須對應至 bot 選單項目**。若 bot 缺少某一 endpoint 之對應指令，該整合被視為不完整。

退款流程必須採用警示但允許通過之設計（見 `guides/10-refund-safety.md`），不得以硬性阻擋實作。

## 變數收集

- `{{TG_BOT_TOKEN}}` / `{{DISCORD_BOT_TOKEN}}`
- `{{BACKEND_URL}}`（bot 與後端通訊位址）
- `{{ADMIN_TOKEN}}`
- `{{REFUND_MAX_PER_ORDER}}` / `{{REFUND_DAILY_QUOTA}}` / `{{REFUND_DAILY_COUNT_CAP}}`
