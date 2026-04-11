# 貢獻指南

感謝您對 `omg-payment-skill` 的興趣。本 skill 為社群維護之非官方資源，歡迎提交 Pull Request 修正錯誤、補充範例、翻譯文件或新增付款方式支援。

## 貢獻方式

### 回報問題

若您發現錯誤或有功能建議，請於 GitHub Issues 提交。請包含：

- 問題描述與重現步驟
- 受影響的檔案或 guide
- 使用之 Python 版本、作業系統
- 相關 log（請遮蔽敏感資訊）

**安全性問題請不要開公開 issue**，請依 `SECURITY.md` 之方式回報。

### 提交 Pull Request

1. Fork repo 並建立 feature branch
2. 進行修改
3. 執行自我檢查清單（見下方）
4. 提交 PR 並說明變更內容

### Commit 訊息

建議採用 Conventional Commits 格式：

```
feat: 新增 Discord bot 選單項目
fix: 修正 CheckMacValue 計算中字典序排序錯誤
docs: 補充 guides/17-troubleshooting.md 之錯誤代碼
refactor: 重構 idempotency handler 之錯誤處理
test: 新增 webhook 重送測試案例
```

## 自我檢查清單

提交前請逐項確認：

- [ ] 所有 `{{變數}}` 佔位符語法正確且用途明確
- [ ] 文件中未包含任何真實的金鑰、訂單號、客戶資料
- [ ] 文件中未使用「歐付寶」字樣（應為「歐買尬」）
- [ ] 退款相關變更採用警示但允許通過設計
- [ ] 正式環境相關變更未引入 `create_order` 作為健康檢查
- [ ] API endpoint 新增時已同步更新 bot 選單
- [ ] 新增的 guide 於 `SKILL.md` §3 章節索引中加入對應項目
- [ ] CHANGELOG 已更新
- [ ] 若為重大變更，已更新版本號

## 撰寫風格

### 文字

- 使用繁體中文，技術名詞首次出現時以英文括號輔助
- 技術規格語氣，避免口語敘述
- 避免使用表情符號與情緒化用詞
- 短句優於長句，段落之間保留空行

### 程式碼

- Python 程式碼遵循 PEP 8
- 函式與類別須有 docstring
- 複雜邏輯須加註解
- 避免硬寫金鑰或商家 ID，應使用 `settings.xxx` 或 `os.getenv()`

### 文件結構

- 每份 guide 以 `# Guide XX — 標題` 開頭
- 章節採三層以下（H1、H2、H3）
- 程式碼區塊標註語言（`python`、`sql`、`bash` 等）
- 表格以 markdown 標準語法
- 項目符號內容超過一行時應換行保持可讀性

## 新增 Guide

若新增一份 guide，請同步：

1. 於 `SKILL.md` §3 章節索引新增對應列
2. 於 `SKILL.md` §0.3 執行順序新增對應步驟（若為自動執行項目）
3. 於 `CHANGELOG.md` 加入變更紀錄
4. 若影響 AI 執行流程，更新 `commands/` 下之對應快捷指令

## 新增付款方式

若新增歐買尬支援之付款方式（例如未來新增之行動支付）：

1. 於 `references/api-endpoints.md` 加入對應欄位表
2. 於 `templates/omg-test-console/backend.py` 新增測試 endpoint
3. 於 `templates/omg-test-console/console.html` 加入測試按鈕
4. 於 `guides/01-quickstart.md` 提及該支援
5. 於 `README.md` 付款方式表格新增一列

## 法規範本

法規相關變更（guides/13 至 15）須特別謹慎：

- 不得聲稱「已符合法規」或「可直接使用」
- 每次修改須保留免責聲明
- 重大條款變更建議邀請熟悉台灣消費者保護法之貢獻者 review
- 不得加入特定律師或事務所之推薦

## 授權

本 repo 採 MIT License 授權。提交 PR 即表示您同意將貢獻內容以相同授權條款釋出。

## 社群守則

- 尊重其他貢獻者，即使有技術分歧亦應保持專業
- 不得於 issue / PR 中散布廣告或無關連結
- 不得以 PR 形式推廣特定商家或服務商
- 若發生爭議，維護者保留最終決定權

## 感謝

所有貢獻者將於 CHANGELOG 對應版本致謝。重大貢獻者將於 README 特別鳴謝。
