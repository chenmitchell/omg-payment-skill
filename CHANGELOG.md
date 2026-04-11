# Changelog

所有重大變更均記錄於此文件，格式依據 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)。

## [2.0.0] — 2026-04-12

本版本為大幅度重寫，以 ECPay-API-Skill 之 repo 結構為參考，將原本單檔 `SKILL.md` 擴展為完整 skill 套件。

### 新增

- Onboarding 流程（`guides/00-onboarding.md`），以四個問題完成整合需求收集
- Quickstart 指南（`guides/01-quickstart.md`），支援零程式碼上手
- FastAPI 後端骨架（`guides/02-backend-fastapi.md`）
- Race-safe webhook 冪等性處理（`guides/05-webhook-idempotency.md`）
- 測試環境全鏈路儀表板（`guides/06-test-dashboard.md`、`templates/omg-test-console/`）
- 正式環境唯讀探測儀表板（`guides/07-prod-dashboard.md`），採 TCP handshake、假交易查詢、退款簽名自我驗證、webhook MAC 自我驗證四項探測方法
- Telegram 與 Discord 通知機器人（`guides/08-telegram-bot.md`、`guides/09-discord-bot.md`、`templates/telegram-bot/`、`templates/discord-bot/`），採 Bind / Notify / Menu 三段結構
- 退款安全機制（`guides/10-refund-safety.md`），採警示但允許通過之設計原則
- 台灣合規揭露範本：首頁與頁尾（`guides/11-merchant-homepage.md`）、商品頁（`guides/12-product-page.md`）
- 台灣法規公版範例：服務條款（`guides/13-legal-tos.md`）、隱私權政策（`guides/14-legal-privacy.md`）、退貨退款政策（`guides/15-legal-refund.md`）
- 定期定額訂閱指南（`guides/16-recurring-subscriptions.md`）
- 故障排除手冊（`guides/17-troubleshooting.md`）
- API reference（`references/api-endpoints.md`、`references/check-mac-value.md`、`references/error-codes.md`）
- 快捷指令（`commands/omg-pay.md`、`omg-refund.md`、`omg-health.md`、`omg-bot.md`、`omg-legal.md`、`omg-debug.md`）

### 變更

- **退款機制由硬性阻擋調整為警示但允許通過**：過去版本於退款超過上限時直接拒絕執行，新版改為顯示警示並保留執行權限給使用者。上限值 `REFUND_MAX_PER_ORDER`、`REFUND_DAILY_QUOTA`、`REFUND_DAILY_COUNT_CAP` 可由 `.env` 調整。
- **正式環境健康檢查改為唯讀探測模式**：舊版於正式環境使用 `create_order` 作為健康檢查，會於商家後台累積無效訂單。新版嚴禁此行為，並提供四項不會產生實際訂單之替代方案。
- README 與 SKILL.md 採技術規格語氣撰寫，移除口語敘述

### 修正

- 修正舊版中部分段落誤將「歐買尬（OMG / MacroWell OMG）」寫為「歐付寶（OPay）」。兩家為不同公司，本 Skill 僅覆蓋歐買尬。
- 修正部分文件中 API host 指向錯誤

### 移除

- 舊版單檔結構之內容（已拆解至各 guides 與 references）

## [1.x] — 歷史版本

原始版本以單一 `SKILL.md` 為主，內容以 API 規格為中心，不含 bot、儀表板、法規範本等擴充功能。詳細內容可於 git history 查詢。

---

**版本號原則**：本 skill 遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)：

- **MAJOR**：不相容於舊版的 SKILL 結構或 API 變更
- **MINOR**：向後相容的新功能（新增 guide、新增 command）
- **PATCH**：向後相容的修正（錯字、描述調整、範例修正）
