# commands — AI 快捷指令範本

本資料夾存放可於 Claude Code、Cursor、Cowork 等支援 slash command 之 AI 平台中使用的快捷指令範本。每個 `.md` 檔對應一個指令，AI 於讀取後應依其定義之流程執行。

> [!NOTE]
> 本資料夾之指令僅為社群維護之範本，並非歐買尬官方 API。遇精確規格問題時請查閱 <https://github.com/omgtwhub/> 與歐買尬商家後台文件。

---

## 指令索引

| 指令檔 | 觸發語意 | 主要用途 |
|---|---|---|
| `omg-pay.md` | `/omg-pay` | 啟動完整歐買尬整合流程（四問 onboarding → 後端 → 儀表板 → 機器人 → 法規範例） |
| `omg-refund.md` | `/omg-refund` | 退款單筆訂單；包含警示提示（單筆上限、每日總額、每日次數） |
| `omg-health.md` | `/omg-health` | 執行當前環境健康檢查（測試環境：全鏈路；正式環境：四項唯讀探測） |
| `omg-bot.md` | `/omg-bot` | 啟動 Telegram 或 Discord 通知機器人設定流程 |
| `omg-legal.md` | `/omg-legal` | 產出台灣法規揭露範例（服務條款、隱私權、退款政策、首頁揭露） |
| `omg-debug.md` | `/omg-debug` | 診斷歐買尬整合問題（CheckMacValue、webhook 重送、host 錯用等） |

---

## 使用方式

### Claude Code

將本資料夾複製至 `~/.claude/commands/omg/` 後，於 Claude Code 中輸入 `/omg-pay` 即可觸發。

```bash
mkdir -p ~/.claude/commands/omg
cp commands/*.md ~/.claude/commands/omg/
```

### Cursor

於 Cursor 之 `.cursor/rules/` 目錄建立對應 rule，並引用本資料夾之內容。詳見 `SETUP.md`。

### Cowork

Cowork 會自動載入本 repo 下的 `commands/` 資料夾。輸入 `/omg-pay` 即可觸發。

---

## 指令定義格式

每個指令檔採下列 frontmatter：

```markdown
---
name: omg-pay
description: 啟動歐買尬金流完整整合流程
---

# 指令名稱

## 觸發語意
（何時執行此指令）

## 執行規則
（AI 必須依序執行的步驟）

## 參考文件
（本指令依賴的 guides / references 檔案）

## Anti-patterns
（執行時禁止的行為）
```

---

## 新增指令規則

1. **命名**：`omg-<動作>.md`，動作部分以連字號小寫英文
2. **描述**：description 欄位以一句繁體中文描述該指令之用途
3. **參考文件**：若指令依賴某份 guide，必須於「參考文件」章節列出
4. **一致性**：若新增之指令會呼叫 admin endpoint，必須同步確認 `guides/08-telegram-bot.md` 與 `guides/09-discord-bot.md` 之選單已涵蓋對應操作
5. **官方資源優先**：若指令涉及 API 精確規格，必須於輸出中提示使用者「以官方文件為準」並附上 <https://github.com/omgtwhub/> 連結
