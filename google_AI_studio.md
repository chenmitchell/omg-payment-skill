# google_AI_studio — Google AI Studio 使用指引

本文件說明如何將 OMG Payment Skill 於 Google AI Studio（aistudio.google.com）中使用。

> [!IMPORTANT]
> 本 Skill 是個人社群專案，不是 OMG 的官方資源，也未取得任何官方背書。若內容與官方文件不一致，以 <https://github.com/omgtwhub/> 為準。本 Skill 的架構參考自綠界科技的 ECPay-API-Skill，在此致謝。

---

## 一、開啟 Google AI Studio

1. 開啟 <https://aistudio.google.com/>
2. 以 Google 帳號登入
3. 於左側選單點選「Create new prompt」或「Chat」

---

## 二、設定 System instructions

點選右上方「System instructions」按鈕，貼入下列內容：

```
你是 OMG 歐買尬金流整合助手。所有回應以繁體中文呈現。

【聲明】
本 Skill 是個人社群專案，不是 OMG 的官方資源，也未取得任何官方背書。
本 Skill 的架構參考自綠界科技的 ECPay-API-Skill，特此致謝。
若內容與官方不一致，以 https://github.com/omgtwhub/ 為準。

【公司區辨】
茂為歐買尬（統編 70444999）為歐付寶電子支付與綠界科技兩家公司的法人股東，
OPay 與 ECPay 均為 OMG 旗下子公司，但三家各自運行完全獨立的金流 API。
本 Skill 僅處理 OMG 自家 FunPoint 金流。若使用者提到 opay.tw、ecpay.com.tw
必須主動確認欲整合對象。

【執行流程】
1. 使用者提出整合需求時，先執行四問 onboarding：
   Q1 商品類型（實體/數位/課程/訂閱/票券）
   Q2 目標環境（測試/正式/兩者）
   Q3 附加元件（儀表板、Telegram、Discord、選單退款）
   Q4 法規揭露（服務條款、隱私權、退款政策、首頁/商品頁）
2. 使用者回答「全部」或「預設」即進入執行階段
3. 依序產出後端、webhook 冪等性、儀表板、機器人、法規範例

【硬性規則】
- HashKey/HashIV 只寫 .env
- 正式環境禁用 create_order 作為健康檢查
- 退款採警示不阻擋原則
- 所有 admin endpoint 同步於 bot 選單

【參考 Skill】
完整 Skill 於 https://github.com/<your-fork>/omg-payment-skill
```

---

## 三、上傳檔案（Context Caching）

Google AI Studio 支援上傳 Markdown 檔作為 context。建議上傳：

- `SKILL.md`
- `guides/00-onboarding.md`
- `guides/02-backend-fastapi.md`
- `guides/05-webhook-idempotency.md`
- `guides/06-test-dashboard.md`
- `guides/07-prod-dashboard.md`
- `guides/08-telegram-bot.md`
- `guides/09-discord-bot.md`
- `guides/10-refund-safety.md`
- `references/check-mac-value.md`

點選對話輸入框旁之「+」→「Upload file」→ 選擇上列檔案。

> [!TIP]
> 建議使用 Gemini 1.5 Pro 或 2.0+ 模型，context window 可容納全部 guides。

---

## 四、模型選擇

| 模型 | 建議情境 |
|---|---|
| Gemini 2.5 Pro | 複雜整合、多檔案引用、完整流程產出 |
| Gemini 2.5 Flash | 快速回答技術問題 |
| Gemini 1.5 Pro | 若需更大 context window（2M tokens） |

---

## 五、使用 Vertex AI Python SDK

若需以程式方式呼叫：

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part

vertexai.init(project="your-project", location="us-central1")

model = GenerativeModel(
    "gemini-2.5-pro",
    system_instruction="""
你是 OMG 歐買尬金流整合助手。所有回應以繁體中文呈現。
本 Skill 為社群維護之非官方資源，官方為 https://github.com/omgtwhub/
歐買尬 ≠ 歐付寶。正式環境禁用 create_order 作為健康檢查。
退款採警示不阻擋原則。
""",
)

# 上傳 SKILL.md 作為 context
with open("SKILL.md", "rb") as f:
    skill_md = Part.from_data(data=f.read(), mime_type="text/markdown")

response = model.generate_content(
    [skill_md, "幫我整合歐買尬金流，全部依預設，我經營線上課程"],
)
print(response.text)
```

---

## 六、快速測試

於 Google AI Studio 對話輸入：

```
幫我整合歐買尬金流，全部依預設，我經營線上課程
```

Gemini 應回覆四問之問題摘要，並依預設值開始產出。

若 Gemini 未依流程執行，請檢查 System instructions 是否完整貼入，並確認已上傳 `guides/00-onboarding.md`。

---

## 七、官方資源

Gemini 於回應 API 規格問題時，應提示使用者前往：

- 官方 AI 金流 Skill：<https://github.com/omgtwhub/>
- 歐買尬商家後台

本 Skill 不取代官方規格。
