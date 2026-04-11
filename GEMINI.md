# Google Gemini 使用指引

> [!IMPORTANT]
> **聲明**：本 Skill 是個人社群專案，不是 OMG 的官方資源，也未取得任何官方背書。若內容與官方文件不一致，請以 <https://github.com/omgtwhub/> 為準。本 Skill 的架構參考自綠界科技的 ECPay-API-Skill，在此致謝。
>
> **歐買尬、歐付寶、綠界的關係**：茂為歐買尬（統編 70444999）為歐付寶電子支付與綠界科技兩家公司的法人股東，依經濟部公司登記資料，兩家的董事長與法人董事均由茂為歐買尬指派，即 OPay 與 ECPay 皆為 OMG 旗下子公司。但三家各自運行完全獨立的金流 API，彼此沒有相容性。本 Skill 僅處理 OMG 自家的 FunPoint 全方位金流。

本文件為 Google Gemini 使用者提供 `omg-payment-skill` 的載入與使用方式。

## 適用版本

- Gemini 2.5 Pro（Web / API）
- Gemini CLI
- Gemini Code Assist（VS Code、JetBrains IDE）
- Vertex AI 上的 Gemini

## 載入方式

### Gemini Web / App

於 Gemini 對話中上傳下列檔案作為附件：

1. `SKILL.md`
2. `guides/00-onboarding.md`
3. `guides/05-webhook-idempotency.md`
4. `guides/10-refund-safety.md`
5. `references/check-mac-value.md`

於對話中輸入：

```
請參考上傳的 omg-payment skill 文件，依 SKILL.md 的 §0 執行規則協助我整合歐買尬金流。
我經營線上課程，全部依預設執行。
```

Gemini 之 context window 較大，可於一次對話中容納完整 skill 內容。

### Gemini CLI

安裝 Gemini CLI 後，於專案目錄執行：

```bash
gemini chat \
  --context omg-payment-skill/SKILL.md \
  --context omg-payment-skill/guides/00-onboarding.md \
  --context omg-payment-skill/guides/05-webhook-idempotency.md
```

於對話中輸入觸發語即可啟動整合流程。

### Gemini Code Assist

於 VS Code 或 JetBrains IDE 中安裝 Gemini Code Assist 擴充後：

1. 將本 skill clone 至專案目錄下
2. 於 Code Assist 對話中輸入：「讀取 `omg-payment-skill/SKILL.md` 並協助我整合歐買尬金流」
3. Code Assist 將依 skill 定義之流程執行

### Vertex AI（企業整合）

於 Vertex AI 中建立自訂 agent 時，將本 skill 上傳至 Grounding data source：

```python
from vertexai.generative_models import GenerativeModel, Part

model = GenerativeModel("gemini-2.5-pro")

with open("omg-payment-skill/SKILL.md") as f:
    skill_content = f.read()

response = model.generate_content([
    Part.from_text(skill_content),
    Part.from_text("請依此 skill 協助整合歐買尬金流"),
])
```

## Gemini 特有的考量

### Context window 利用

Gemini 2.5 Pro 支援超過 100 萬 token 的 context window，可於單次對話中載入本 skill 的完整內容（約 15 萬 token）。建議載入完整內容以避免 AI 因缺少 context 而誤解規則。

### Multi-modal 能力

若您有歐買尬商家後台的截圖或錯誤訊息圖片，Gemini 可直接讀取並協助解釋。提示範例：

```
[附上後台截圖]
這張圖是歐買尬商家後台的訂單頁面，幫我標註哪些欄位對應 skill 中的 payment_transactions 表
```

### Grounding with Google Search

Gemini 的 Google Search grounding 功能可用於查詢最新的歐買尬官方文件或法規變更。但請注意：

- 搜尋結果中若出現「歐付寶」字樣，可能與您目標的「歐買尬」不同
- 搜尋時請明確加上「MacroWell OMG」或「歐買尬 Payment」關鍵字
- 法規相關資訊應交叉比對官方公告

## 常見使用情境

### 情境一：完整整合

```
user: 我要開一個賣手作皮革包的網站，用歐買尬收款，你幫我做一套

gemini: [讀取 SKILL.md §0.1 onboarding 規則]
        好的，開始之前請回答四個問題：
        1. 商品類型（實體皮革包 → 實體商品）
        2. 目標環境
        3. 附加元件
        4. 法規揭露範例
        
        若依預設執行請回覆「全部」或「預設」。

user: 全部

gemini: [依 SKILL.md §0.3 的 15 步順序產出檔案]
```

### 情境二：僅產出法規範本

```
user: 我已經有金流了，只要幫我產出台灣的服務條款、隱私權、退貨退款政策三份

gemini: [讀取 guides/13-legal-tos.md, guides/14-legal-privacy.md, guides/15-legal-refund.md]
        請提供下列商家資訊以替換範本中的佔位符：
        - 商家名稱
        - 統一編號
        - 負責人姓名
        - 客服 Email 與電話
        - 營業地址
        - 網站網址
```

### 情境三：Debug MAC 錯誤

```
user: 我的 create_order 一直回傳 CheckMacValue Error，payload 貼給你看...

gemini: [讀取 references/check-mac-value.md]
        [分析 payload 是否依字典序排序]
        [計算期望的 MAC]
        [與使用者送出的 MAC 比對]
        [指出差異點]
```

## 注意事項

### Gemini 偶爾會混淆中文商家名稱

部分情境下，Gemini 可能將「歐買尬」誤讀為「歐付寶」。若發現 AI 產出內容中出現「歐付寶」、「opay.tw」等字樣，請明確糾正：

```
注意：我要整合的是歐買尬（MacroWell OMG Digital Entertainment），
不是歐付寶（OPay）。兩家為不同公司。請重新閱讀 SKILL.md 開頭的非官方聲明。
```

### 法規範本必須經律師審閱

本 skill 的 `guides/13-legal-tos.md`、`guides/14-legal-privacy.md`、`guides/15-legal-refund.md` 為公版範例。若 Gemini 宣稱「此範本已符合法規可直接使用」，請明確糾正並要求加上免責聲明。

### 不要將真實金鑰貼入對話

Gemini 對話內容會被 Google 用於改進模型（依您使用的產品計畫而定）。**絕對不要** 將歐買尬的 HashKey、HashIV 直接貼入對話。若需 debug，請使用遮蔽值（例：`HashKey=XXXX****XXXX`）。

## 更新

本 skill 的最新內容請參考 `CHANGELOG.md`。若您於對話中發現 Gemini 引用的內容與最新版不一致，請重新上傳最新版的 `SKILL.md` 與相關 guides。
