# SETUP — 於各 AI 平台安裝本 Skill

本文件說明如何將 `omg-payment-skill` 載入至不同 AI 平台或開發工具中使用。

## Claude Code

```bash
# 於您的專案目錄下
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/<your-fork>/omg-payment-skill.git omg-payment
```

Claude Code 將於下次啟動時自動讀取 `.claude/skills/omg-payment/SKILL.md`。觸發方式：於對話中輸入「幫我整合歐買尬金流」即會自動載入本 skill。

## Cowork 模式

本 skill 可作為 Cowork plugin 使用。將 repo 放置於 Cowork 支援的 skill 目錄後，於任務中輸入觸發語即可載入。

## Cursor

Cursor 支援透過 `.cursor/rules/` 加入 skill 內容：

```bash
mkdir -p .cursor/rules
cp omg-payment-skill/SKILL.md .cursor/rules/omg-payment.md
```

並於 Cursor 設定中啟用該 rule。

## Windsurf

將 `SKILL.md` 與 `guides/` 複製至專案根目錄或設定 Windsurf 的 `.windsurfrules` 指向本 skill。

## VS Code + GitHub Copilot

於專案根目錄建立 `.github/copilot-instructions.md`，內容參考 `SKILL.md` 之 §0 執行規則摘要。Copilot Chat 將於對話時納入參考。

## GitHub Copilot CLI

```bash
copilot suggest --context omg-payment-skill/SKILL.md "幫我整合歐買尬金流"
```

## ChatGPT（Web / Desktop）

1. 開啟新對話
2. 上傳 `SKILL.md` 與相關 `guides/*.md`
3. 於對話中貼上觸發語：「請依 omg-payment skill 幫我整合歐買尬金流，全部依預設」

或於自訂 GPT 中將本 skill 內容作為 knowledge base 上傳。

## Google Gemini

Gemini 支援上傳 markdown 檔案作為對話 context。將 `SKILL.md` 與必要 guides 上傳後，於對話中輸入觸發語即可。

## OpenAI Codex / Claude Agent SDK

若於自訂 agent 中使用，將本 skill 作為 knowledge source 或 system prompt extension 納入即可。建議載入以下檔案作為 context：

- `SKILL.md`
- `guides/00-onboarding.md`
- `guides/05-webhook-idempotency.md`
- `guides/10-refund-safety.md`
- `references/check-mac-value.md`

## Cline / Continue

於 Cline 或 Continue 的 workspace 設定中，將本 skill 目錄加入 context providers 或 knowledge sources。

## 通用方式：手動上傳

若您使用的 AI 平台未於上述列表，通用方式為：

1. 將 `SKILL.md` 全文貼入對話作為 system prompt 或初始訊息
2. 於後續對話中依需求貼入對應 guide 的內容
3. 使用觸發語開始整合

## 更新 skill

當本 skill 有新版本時：

```bash
cd path/to/omg-payment-skill
git pull origin main
```

請於 `CHANGELOG.md` 查看變更內容，並於 AI 對話中明確告知使用新版。

## 疑難排解

- **AI 未依 skill 行為執行**：確認 AI 已讀取 `SKILL.md` 完整內容；部分平台需明確指定載入 skill 檔案
- **AI 詢問本 skill 未定義之問題**：可能代表該 AI 未完整讀取 `SKILL.md` §0 執行規則，請提醒其參考該節
- **AI 於正式環境建議 `create_order`**：違反本 skill 之硬性規則。請貼出 `SKILL.md` §0.4.2 內容並要求重新生成
- **AI 以硬性阻擋方式實作退款上限**：違反本 skill 之退款設計原則。請貼出 `SKILL.md` §0.4.3 內容並要求調整

## 授權與來源

本 skill 採 MIT License，為社群維護之非官方資源。取自：

```
https://github.com/<your-fork>/omg-payment-skill
```

使用本 skill 不代表取得 MacroWell OMG Digital Entertainment Co., Ltd. 任何授權或背書。
