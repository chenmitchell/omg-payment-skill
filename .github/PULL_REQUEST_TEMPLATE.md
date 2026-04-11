# PR 說明

<!-- 一句話說明這個 PR 在做什麼 -->

## 變更類型

- [ ] 修正錯字 / typo
- [ ] 新增 guide / references / template
- [ ] 修正 guide / references 內容錯誤
- [ ] 新增或修正 validator 腳本
- [ ] 更新 CI workflow
- [ ] 更新 SKILL.md / CLAUDE.md / AGENTS.md / GEMINI.md 等平台入口
- [ ] 其他（請說明）：

## 影響範圍

<!-- 此 PR 影響哪些檔案 / 哪些平台 / 是否破壞向後相容 -->

## CI 檢查清單

請確認下列檢查於本機已通過（CI 會再執行一次）：

- [ ] `bash scripts/validate-version-sync.sh` PASS
- [ ] `bash scripts/validate-ai-index.sh` PASS
- [ ] `bash scripts/validate-agents-parity.sh` PASS
- [ ] `bash scripts/validate-bot-menu-parity.sh` PASS
- [ ] `bash scripts/validate-no-leaks.sh` PASS
- [ ] `bash scripts/validate-omg-not-opay.sh` PASS
- [ ] `python3 test-vectors/verify.py` 3/3 PASS（若涉及 CheckMacValue）
- [ ] `node test-vectors/verify-node.js` 3/3 PASS（若涉及 CheckMacValue）

## 文件同步檢查

- [ ] 若新增 guide，已於 `README.md` 與 `SKILL.md` 的指南索引加入對應條目
- [ ] 若新增 admin API endpoint，已於 `templates/telegram-bot/bot.py` 與 `templates/discord-bot/bot.py` 同步新增選單對應
- [ ] 若修改 `references/check-mac-value.md`，已同步更新 `test-vectors/check-mac-value.json`
- [ ] 若版本號變動，已同步更新 `SKILL.md` §0 宣告、`README.md` badge、`CHANGELOG.md`

## 隱私與安全檢查

- [ ] 未包含任何真實 HashKey / HashIV / 正式環境 MerchantID
- [ ] 未包含任何個案商家之內部路徑、服務名、hostname、真實訂單號
- [ ] 未將歐買尬（OMG）誤寫為歐付寶（OPay）
- [ ] 若內容引用官方資源，已於 PR 註明對應頁面（若連結失效請於 PR 標題加上 `[broken-link]`）

## 相關 Issue

<!-- Closes #xx / Related to #xx -->

## 截圖 / log（可選）

<!-- 若為 UI 相關改動（templates/ 下的 HTML / bot embed），請附截圖 -->
<!-- 若為 CI / validator 改動，請附執行 log -->

---

感謝您的貢獻！本 Skill 的存在就是因為有人「見賢思齊」，歡迎加入這份精神。
