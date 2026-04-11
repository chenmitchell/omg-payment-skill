# Roadmap — OMG Payment Skill

> 本 repo 為社群維護之 AI Skill，無正式 release schedule。Roadmap 為維護者對未來方向的公開意圖，歡迎透過 Issue / PR 表達意見或提交貢獻。

## Now（進行中 / v2.x）

- [x] 多後端語言骨架（FastAPI / Express / Laravel）
- [x] Webhook 冪等性 race-safe 參考實作
- [x] 測試環境 + 正式環境雙儀表板模板
- [x] Telegram + Discord bot 模板（Bind / Notify / Menu）
- [x] 退款安全機制（警示不阻擋）
- [x] 台灣法規揭露公版（服務條款 / 隱私權 / 退款政策）
- [x] 定期定額訂閱整合指南
- [x] CheckMacValue SSOT 測試向量（Python + Node.js 雙驗證）
- [x] CI 驗證門禁（6 個 validator）
- [x] 多 AI 平台入口檔（Claude / GPT / Gemini / Cursor / Copilot / Codex）
- [x] llms.txt 索引
- [x] 非官方聲明與官方資源導引（指向 <https://github.com/omgtwhub/>）

## Next（下一階段 / v2.x → v3.0）

- [ ] **英文 README**（README.en.md）與 guides 英文翻譯（優先 00 / 05 / 10）
- [ ] **Go 語言後端骨架**（`guides/04b-backend-go.md`）
- [ ] **Java / Spring Boot 後端骨架**（`guides/04c-backend-spring.md`）
- [ ] **.NET / C# 後端骨架**（`guides/04d-backend-dotnet.md`）
- [ ] **Ruby on Rails 後端骨架**（`guides/04e-backend-rails.md`）
- [ ] **Docker Compose 全鏈路展示堆疊**（backend + postgres + bot + dashboard）
- [ ] **測試後台 React / Vue 版本**（取代 HTML only）
- [ ] **LINE Notify / LINE Bot 通知模板**（補齊繁體中文用戶主要通路）
- [ ] **Slack Bot 通知模板**
- [ ] **Sentry / OpenTelemetry 整合範例**（正式環境監控延伸）
- [ ] **webhook replay 工具**（再送上游 webhook 用於本機除錯）

## Later（長期規劃）

- [ ] **多幣別 / 跨境金流延伸**（OMG 開通海外卡後）
- [ ] **發票自動化**（電子發票 B2C / 載具 / 捐贈碼整合）
- [ ] **ESLint / pylint / PHPStan 一鍵掃描模板**
- [ ] **CodeQL / SAST 安全掃描 workflow**
- [ ] **影片教學**（10 分鐘內完成整合的實戰 demo）
- [ ] **部落格文章與案例研究**（`docs/case-studies/`）
- [ ] **整合至 awesome-payment-gateway / awesome-taiwan 等清單**
- [ ] **社群講座 / MOPCON / PyCon Taiwan 投稿**

## 不會做（Non-goals）

以下項目本 repo 明確不打算實作，請勿提 PR：

- ❌ **SDK 包裝**：本 Skill 的定位是「AI 可讀的知識包」，不是 SDK。SDK 請以官方 `omgtwhub` 為準
- ❌ **商用後台系統**：本 Skill 只提供模板與指引，不提供完整 SaaS 後台
- ❌ **破解 / 繞過金流風控**：任何涉及規避 MerchantID 驗證、偽造簽章、繞過 3DS 之內容，一律拒絕
- ❌ **涵蓋歐付寶（OPay）**：本 Skill 只針對歐買尬（OMG），歐付寶請另尋資源
- ❌ **真實金鑰 / MerchantID 範例**：所有範例僅使用 OMG 公開測試資訊（`1000031`），不接受真實商家資訊 PR

## 如何影響 Roadmap

1. **提 Issue**：對 Next / Later 項目有意見，或想提新項目，請開 Issue 標題加上 `[roadmap]`
2. **提 PR**：如果你想直接做 Next 或 Later 的項目，可直接開 PR。維護者會以 code review 的方式回饋
3. **Fork**：本 repo 沒有 gatekeeper。如果你不想等，歡迎 fork 之後自己做，並於自己的 README 標示 forked from 本 repo

## 版本策略

- **v1.x**：原始 FastAPI skeleton（僅供參考，已進入 maintenance-only）
- **v2.x**：本次大改版，加入多平台入口、多語言後端、儀表板、bot、法規、CI、測試向量
- **v3.x**：暫定為補齊英文化 + 多語言後端 + Docker 展示堆疊的版本
- **v4.x 起**：保留給重大架構變動（如支援歐買尬 API v2 或跨境金流）

語義化版本（[SemVer](https://semver.org/lang/zh-TW/)）原則：

- 破壞性變更（例：guides 編號重編、SKILL.md §0 執行規則大改） → major
- 新增 guide / template / validator / 支援平台 → minor
- 修正錯字 / 欄位誤解 / 更新 references → patch

詳細變更請見 [`CHANGELOG.md`](./CHANGELOG.md)。
