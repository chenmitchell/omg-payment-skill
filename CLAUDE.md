# Claude Code 使用指引

> [!IMPORTANT]
> **聲明**：本 Skill 是個人社群專案（**非官方**），不是 OMG 的官方資源，也未取得任何官方背書。若內容與官方文件不一致，請以 <https://github.com/omgtwhub/> 為準。本 Skill 的架構參考自綠界科技的 ECPay-API-Skill，在此致謝。
>
> **歐買尬、歐付寶、綠界的關係**：茂為歐買尬（統編 70444999）為歐付寶電子支付與綠界科技兩家公司的法人股東，依經濟部公司登記資料，兩家的董事長與法人董事均由茂為歐買尬指派，即 OPay 與 ECPay 皆為 OMG 旗下子公司。但三家各自運行完全獨立的金流 API，彼此沒有相容性。本 Skill 僅處理 OMG 自家的 FunPoint 全方位金流。

本文件為 Claude Code 使用者提供 `omg-payment-skill` 的載入與使用方式。

## 前置條件

- 已安裝 Claude Code（[安裝指南](https://docs.claude.com/claude-code)）
- 具備 Python 3.10 以上之環境
- 已於歐買尬商家後台取得測試環境金鑰

## 安裝方式

### 方式一：作為專案 skill

於您的專案根目錄執行：

```bash
mkdir -p .claude/skills
git clone https://github.com/<your-fork>/omg-payment-skill.git .claude/skills/omg-payment
```

Claude Code 將於下次啟動時自動載入 `.claude/skills/omg-payment/SKILL.md`。

### 方式二：作為使用者層級 skill

若您希望於所有專案均可使用本 skill：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/<your-fork>/omg-payment-skill.git ~/.claude/skills/omg-payment
```

### 方式三：直接於對話中載入

若不希望安裝，可於 Claude Code 對話中手動指定：

```
請讀取 omg-payment-skill/SKILL.md 並依該文件的 §0 執行規則協助我整合歐買尬金流
```

## 觸發方式

於 Claude Code 對話中輸入下列任一語句，即會自動載入本 skill：

- 「幫我整合歐買尬金流」
- 「建置付款系統使用歐買尬」
- 「設定 OMG 收款」
- 「幫我弄一個歐買尬收款後台」

Claude 將依 `guides/00-onboarding.md` 之四問流程展開整合需求收集。若您希望直接以預設值進入全自動整合：

```
請依 omg-payment skill 幫我整合歐買尬金流，全部依預設，我經營線上課程
```

## Claude Code 特有優勢

Claude Code 支援直接於終端機執行指令、修改檔案、查看 log，適合本 skill 所定義之整合流程：

1. **一次產出整個檔案樹**：Claude 可依 `SKILL.md` §0.3 之 17 步順序，一次性產出後端、儀表板、bot、法規文件
2. **自動執行測試儀表板**：產出完成後，Claude 可直接執行 `python templates/omg-test-console/backend.py` 並於終端機檢視結果
3. **即時調整**：若全鏈路測試失敗，Claude 可讀取 log 並自動修正問題
4. **長流程追蹤**：Claude Code 的 TODO 追蹤機制適合本 skill 之多步驟整合

## 建議工作流程

### 首次整合

```
1. 於專案目錄執行 git clone 安裝 skill
2. 開啟 Claude Code
3. 輸入：幫我依 omg-payment skill 整合歐買尬金流
4. 回答四個 onboarding 問題（或回覆「全部」）
5. Claude 產出整個檔案樹
6. Claude 自動執行 templates/omg-test-console/ 之全鏈路測試
7. 依提示補齊 .env 中之金鑰與商家資訊
8. 測試通過後切換至正式環境
```

### 日常維護

```
/omg-debug        故障排除
/omg-health       查詢金流健康狀態
/omg-refund       執行退款
/omg-legal        產出或更新法規範本
```

## 與 Claude Code 其他 skill 的整合

若您已安裝其他 skill（例：docx、pptx、pdf），本 skill 可與之協作：

- **docx skill**：將服務條款、隱私權政策轉為 Word 文件供法務顧問審閱
- **pdf skill**：將退貨退款政策產出為 PDF 供客戶下載
- **pptx skill**：將金流串接流程製作為簡報供商家教育訓練

範例：

```
請依 omg-payment skill 產出服務條款，並使用 docx skill 將其轉為 Word 文件
```

## 常見 Claude Code 使用情境

### 情境一：從零開始

```
user: 我要做一個賣線上課程的網站，還沒有付款系統，幫我用歐買尬做

claude: 好的。在開始之前，請先回答四個問題：
        1. 商品類型（預設為線上課程）
        2. 目標環境（測試 / 正式 / 兩者，預設兩者）
        3. 是否需要管理儀表板與 Telegram/Discord 通知機器人（預設需要）
        4. 是否需要台灣法規揭露範例（預設需要）

user: 全部

claude: 已收到。開始依 17 步執行...
        [產出檔案]
        [執行全鏈路測試]
        [提示補齊商家資訊]
```

### 情境二：已有後端，只要補齊儀表板與 bot

```
user: 我已經有自己寫的 webhook，只要幫我弄測試儀表板跟 Telegram bot 就好

claude: 好的。我將僅依 guides/06-test-dashboard.md 與 guides/08-telegram-bot.md
        產出儀表板與 Telegram bot 兩個模組，並保留您既有的 webhook 實作不動。
        請問您的後端 webhook endpoint URL 與 admin token 為何？
```

### 情境三：故障排除

```
user: 我收到 webhook 但訂單沒更新，幫我看一下

claude: [讀取專案目錄下的 webhook handler]
        [對照 guides/05-webhook-idempotency.md]
        [指出缺失的 MAC 驗證或冪等性步驟]
        [提出修正方案]
```

## 安全提醒

Claude Code 可直接讀取與修改您的檔案，請於使用本 skill 時遵守下列原則：

1. `.env` 中之金鑰不得於對話中貼出
2. 若需 Claude 協助產出 `.env`，應使用「CHANGEME」或空值佔位，實際金鑰由您於對話外填入
3. 不要將包含真實金鑰的截圖分享給 Claude
4. 若 Claude 產出之程式碼包含金鑰硬寫，應立即提醒並要求改為讀取 `.env`

## 疑難排解

**Q：Claude 不認得「歐買尬」這個詞**

A：請於對話中明確指定：「請讀取 omg-payment-skill/SKILL.md」。部分模型對台灣金流服務商名稱不熟悉，明確指向 SKILL 後即可運作。

**Q：Claude 於正式環境建議使用 `create_order` 做健康檢查**

A：此為違反本 skill 之 §0.4.2 硬性規則。請貼出該節內容並要求 Claude 重新生成。可能為 Claude 未讀取 SKILL.md 完整內容。

**Q：Claude 實作退款時採用硬性阻擋**

A：違反本 skill §0.4.3。請貼出該節內容並要求調整為「警示但允許通過」。

## 更新 skill

```bash
cd .claude/skills/omg-payment
git pull origin main
```

請參閱 `CHANGELOG.md` 了解版本變更，`MIGRATION_NOTES.md` 了解升級步驟。
