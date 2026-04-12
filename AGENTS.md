# AGENTS.md — OpenAI Codex 與 Agent SDK 使用指引

> [!IMPORTANT]
> **聲明**：本 Skill 是個人社群專案（**非官方**），不是 OMG 的官方資源，也未取得任何官方背書。若內容與官方文件不一致，請以 <https://github.com/omgtwhub/> 為準。本 Skill 的架構參考自綠界科技的 ECPay-API-Skill，在此致謝。
>
> **歐買尬、歐付寶、綠界的關係**：茂為歐買尬（統編 70444999）為歐付寶電子支付與綠界科技兩家公司的法人股東，依經濟部公司登記資料，兩家的董事長與法人董事均由茂為歐買尬指派，即 OPay 與 ECPay 皆為 OMG 旗下子公司。但三家各自運行完全獨立的金流 API，彼此沒有相容性。本 Skill 僅處理 OMG 自家的 FunPoint 全方位金流。

本文件為使用 OpenAI Codex、Agent SDK 或類似自訂 agent 框架的開發者提供 `omg-payment-skill` 的整合方式。

## 適用對象

- 使用 OpenAI Codex CLI 之開發者
- 使用 OpenAI Agents SDK 建置自訂 agent 之開發者
- 使用 Claude Agent SDK、LangChain、LlamaIndex 等框架整合 AI 之開發者
- 希望於自家 AI 產品中加入歐買尬金流整合能力的團隊

## 載入方式

### 方式一：作為知識庫

將 `SKILL.md` 與 `guides/*.md`、`references/*.md` 上傳至 agent 的 knowledge base。執行時 agent 將依查詢動態檢索相關段落。

建議優先載入：

- `SKILL.md`（核心執行規則）
- `guides/00-onboarding.md`（需求收集流程）
- `guides/05-webhook-idempotency.md`（高頻引用）
- `guides/10-refund-safety.md`（退款設計原則）
- `references/check-mac-value.md`（MAC 演算法）
- `references/api-endpoints.md`（API 欄位）

### 方式二：作為 system prompt extension

將 `SKILL.md` 之 §0 執行規則節錄為 system prompt，並保留完整 guides/references 作為 tool-invocable knowledge。

範例：

```python
from openai import OpenAI

with open("omg-payment-skill/SKILL.md") as f:
    skill_content = f.read()

system_prompt = f"""
You are a payment integration assistant specialized in MacroWell OMG (歐買尬).
Follow the rules defined in the following skill document:

{skill_content}

Always respond in Traditional Chinese unless the user explicitly requests otherwise.
"""

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "幫我整合歐買尬金流"},
    ],
)
```

### 方式三：作為 tool 實作

將本 skill 的每個 guide 包裝為 agent tool：

```python
def get_omg_guide(section: str) -> str:
    """取得 omg-payment-skill 指定章節的內容。

    Args:
        section: 章節名稱，例如 'webhook-idempotency', 'refund-safety'
    """
    guide_map = {
        "onboarding": "guides/00-onboarding.md",
        "quickstart": "guides/01-quickstart.md",
        "fastapi": "guides/02-backend-fastapi.md",
        "webhook-idempotency": "guides/05-webhook-idempotency.md",
        "test-dashboard": "guides/06-test-dashboard.md",
        "prod-dashboard": "guides/07-prod-dashboard.md",
        "telegram-bot": "guides/08-telegram-bot.md",
        "discord-bot": "guides/09-discord-bot.md",
        "refund-safety": "guides/10-refund-safety.md",
        "merchant-homepage": "guides/11-merchant-homepage.md",
        "product-page": "guides/12-product-page.md",
        "legal-tos": "guides/13-legal-tos.md",
        "legal-privacy": "guides/14-legal-privacy.md",
        "legal-refund": "guides/15-legal-refund.md",
        "recurring": "guides/16-recurring-subscriptions.md",
        "troubleshooting": "guides/17-troubleshooting.md",
    }
    path = guide_map.get(section)
    if not path:
        return f"Unknown section: {section}"
    with open(f"omg-payment-skill/{path}") as f:
        return f.read()
```

## Agent 必須遵守的規則

所有使用本 skill 的 agent 均必須遵守 `SKILL.md` §0.4 之操作規範：

1. **API 與 bot 選單一致性**：新增 admin endpoint 時，必須同步更新 bot 選單
2. **正式環境禁止 create_order**：健康檢查僅能使用唯讀探測
3. **退款採警示不阻擋設計**：不得硬性拒絕執行合法退款
4. **法規範例需免責聲明**：不得宣稱「已符合法規」或「可直接使用」
5. **敏感資訊不得留存**：金鑰僅寫入 `.env`，不得於對話或 log 中輸出

Agent 框架應於 guardrails 層強制上述規則，不依賴 prompt 本身的遵從能力。

## 推薦的 Agent 架構

```
┌─────────────────────────────────────┐
│         User Request                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Onboarding Agent               │
│  (讀取 guides/00-onboarding.md)      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Orchestrator                   │
│  (依 SKILL.md §0.3 執行 17 步)      │
└──────────────┬──────────────────────┘
               │
       ┌───────┼────────┬─────────┐
       ▼       ▼        ▼         ▼
   ┌──────┐┌──────┐┌────────┐┌────────┐
   │Backend││Webhook││Dashboard││  Bot  │
   │Agent ││ Agent ││ Agent   ││ Agent │
   └──────┘└──────┘└────────┘└────────┘
       │       │        │         │
       └───────┼────────┴─────────┘
               ▼
┌─────────────────────────────────────┐
│      Validator                      │
│  (執行 templates/omg-test-console/)  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Deliver to User                │
└─────────────────────────────────────┘
```

## Guardrails 實作建議

於 agent 的工具呼叫層加入下列檢查：

```python
BLOCKED_PATTERNS = [
    # 正式環境禁止 create_order
    (r"ENVIRONMENT\s*=\s*['\"]prod['\"].*create_order", "cannot use create_order in prod"),
    # 歐付寶混淆
    (r"歐付寶|opay\.tw", "should be 歐買尬 / MacroWell OMG, not OPay"),
    # 硬寫金鑰
    (r"HashKey\s*=\s*['\"][A-Za-z0-9]{10,}['\"]", "HashKey must come from .env"),
    (r"HashIV\s*=\s*['\"][A-Za-z0-9]{10,}['\"]", "HashIV must come from .env"),
]

def validate_generated_code(code: str) -> list[str]:
    import re
    errors = []
    for pattern, msg in BLOCKED_PATTERNS:
        if re.search(pattern, code):
            errors.append(msg)
    return errors
```

## 常見用法

### 生成完整整合

```python
response = agent.run(
    "User has a Taiwan-based online course platform. "
    "Generate a complete OMG payment integration including "
    "FastAPI backend, test dashboard, prod health monitor, "
    "Telegram bot, Discord bot, and Taiwan legal templates."
)
```

### 生成單一元件

```python
response = agent.run(
    "Generate only the webhook handler with race-safe idempotency "
    "for OMG. Reference guides/05-webhook-idempotency.md."
)
```

### 故障排除

```python
response = agent.run(
    "User reports CheckMacValue Error when calling create_order. "
    "Debug using references/check-mac-value.md and suggest fixes."
)
```

## 授權與責任

本 skill 採 MIT License。使用本 skill 建置的 agent 若對外提供服務，應於使用者介面明確標示：

- 本服務為社群維護，與 MacroWell OMG 無隸屬關係
- 法規範本需由使用者自行審閱
- 金流整合之最終品質由使用者驗證

詳見 `SECURITY.md` 與 `CONTRIBUTING.md`。
