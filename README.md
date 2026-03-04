![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![API Version](https://img.shields.io/badge/API-AioCheckOut%20V5-blue)
![Platform](https://img.shields.io/badge/Platform-Taiwan-green)
![AI Skill](https://img.shields.io/badge/AI%20Skill-Claude%20%7C%20OpenAI-purple)

# OMG 金流串接 Skill | OMG Payment Gateway Skill

> **繁體中文** | [English](#english)

---

## 繁體中文

### 這是什麼？

這是 **AI Skill 檔案**，讓 AI 助手（如 Claude Code、Cowork、ChatGPT）能夠理解 **OMG 金流**（歐買尬第三方支付）的完整 API 規格，並協助開發者快速產生正確的串接程式碼。

這個專案提供了一個完整的 Taiwan 第三方支付網關整合方案，支援多種電子商務付款方式，包括信用卡、ATM 轉帳、超商代碼繳款等。無論你是在建置新的支付系統或整合現有的電商平台，本 Skill 透過 AI 驅動的代碼生成功能，讓付款 API 整合變得簡單快速。我們提供完整的 API 文件、定期定額/訂閱制計費支援、以及生產環境遷移指南。

### 包含內容 / What's Included

- **Complete API documentation** — 6 核心端點的完整規格
- **SDK wrapper class** — Python、Node.js、PHP、C# 多語言支援
- **Admin dashboard generation guide** — 廠商後台整合指南
- **Health check & monitoring** — 系統健康檢查與監控方案
- **Automated error diagnosis** — 自動化錯誤診斷工具
- **Debug tools & checklist** — 除錯工具與檢查清單
- **FastAPI complete example** — 完整的 FastAPI 實作範例
- **Production migration guide** — 從測試環境到正式環境的遷移指南

### 公司資訊

- **公司名稱**：茂為歐買尬數位科技股份有限公司
- **英文名稱**：MacroWell OMG Digital Entertainment Co., Ltd.
- **服務地區**：台灣 (Taiwan)
- **API 文件版本**：V 1.4.9 (2025-11)

### 支援功能（完整 API 涵蓋）

#### 核心 API

- **AioCheckOut/V5** — 產生訂單（一次性付款、分期付款、定期定額）
- **QueryTradeInfo/V5** — 查詢訂單狀態
- **QueryCreditCardPeriodInfo** — 查詢定期定額訂單資訊
- **CreditCardPeriodAction** — 定期定額訂單作業（停用）
- **DoAction (CreditDetail/DoAction)** — 信用卡請退款（關帳/退刷/取消/放棄）
- **QueryTrade/V2 (CreditDetail/QueryTrade/V2)** — 查詢信用卡單筆明細

#### 支援付款方式

- 信用卡一次性付款（Credit）
- 信用卡分期付款（CreditInstallment: 3/6/12/18/24/30 期）
- 信用卡定期定額/訂閱制（Recurring: PeriodType D/M/Y）
- ATM 虛擬帳號轉帳（ATM: 第一銀行/中國信託/聯邦/凱基）
- 超商代碼繳款（CVS: 超商代碼/全家/7-11）
- 超商條碼繳款（BARCODE: 三段式條碼 Code39）
- AFTEE 先享後付

#### 技術功能

- CheckMacValue SHA256 驗證（含 .NET URL Encode 替換）
- 付款結果通知處理（ReturnURL / OrderResultURL）
- ATM/CVS/BARCODE 取號結果通知（PaymentInfoURL）
- 定期定額後續扣款通知（PeriodReturnURL）
- 額外付款資訊回傳（NeedExtraPaidInfo=Y）
- 完整錯誤碼參考與除錯指南
- 正式環境遷移指南
- 冪等性處理與最佳實踐

#### 程式碼範例

- Python (FastAPI) 完整範例
- Node.js (Express.js) 範例
- PHP 範例
- .NET/C# 範例
- CheckMacValue 計算（Python / Node.js / PHP / .NET）

### 如何使用

#### 方法一：放入專案 `.skills` 資料夾（Claude Code / Cowork）

```bash
# 在你的專案根目錄
mkdir -p .skills/skills/omg-payment
cp SKILL.md .skills/skills/omg-payment/SKILL.md
```

Claude Code 或 Cowork 會自動讀取此 Skill 來協助你串接金流。

#### 方法二：OpenAI / ChatGPT 使用

```bash
# 使用 OpenAI 格式的 Skill 檔案
cp SKILL_OPENAI.md your-project/
```

將 `SKILL_OPENAI.md` 的內容貼入 ChatGPT 的 Custom Instructions，或上傳檔案後說「請根據這份金流文件幫我串接」。

#### 方法三：直接告訴 AI

將 Skill 檔案的內容貼給 AI，或上傳檔案後說「請根據這份金流文件幫我串接 OMG 金流」。

### 支援的 AI 平台 / Supported AI Platforms

| AI 平台 | 檔案 | 使用方式 |
|---------|------|---------|
| Claude Code | SKILL.md | 放入 `.skills/skills/omg-payment/` |
| Claude Cowork | SKILL.md | 上傳或引用 |
| ChatGPT | SKILL_OPENAI.md | 自訂指令或上傳檔案 |
| 任何 AI | 任一檔案 | 上傳並請求整合協助 |

### 測試帳號

| 項目 | 值 |
|------|------|
| MerchantID | `1000031` |
| HashKey | `265fIDjIvesceXWM` |
| HashIV | `pOOvhGd1V2pJbjfX` |
| 測試卡號 | `4311-9522-2222-2222` |
| CVV | `222` |
| 有效期限 | 任意未過期月/年 |
| 廠商後台 | `https://vendor-stage.funpoint.com.tw` |
| 後台帳密 | `funstage001` / `test1234` |

### 檔案結構

```
omg-payment-skill/
├── README.md                   # 本說明文件 (中英雙語)
├── SKILL.md                    # Claude Skill 主體（Claude Code / Cowork 用）
├── SKILL_OPENAI.md             # OpenAI Skill 主體（ChatGPT / OpenAI 用）
├── LICENSE                     # MIT License
├── .gitignore                  # Git 忽略規則
└── examples/
    └── fastapi_example.py      # FastAPI 完整串接範例（涵蓋所有 API）
```

---

<a id="english"></a>

## English

### What is this?

This is an **AI Skill file** that enables AI assistants (such as Claude Code, Cowork, ChatGPT) to understand the complete API specification of the **OMG Payment Gateway** (歐買尬 third-party payment) and help developers quickly generate correct integration code.

This project delivers a comprehensive Taiwan-based payment gateway integration solution for e-commerce platforms, supporting multiple payment methods including credit cards, ATM transfers, and convenience store payment codes. Whether you're building a new payment system or integrating payment processing into an existing e-commerce application, this Skill uses AI-powered code generation to make payment API integration straightforward and efficient. We provide complete API documentation, support for recurring subscription billing, credit card payments, and a detailed production migration guide to help you move from testing to live environments seamlessly.

### What's Included

- **Complete API documentation** — Full specifications for 6 core endpoints
- **SDK wrapper class** — Support for Python, Node.js, PHP, and C#
- **Admin dashboard generation guide** — Vendor backend integration instructions
- **Health check & monitoring** — System health verification and monitoring solutions
- **Automated error diagnosis** — Intelligent error detection and resolution
- **Debug tools & checklist** — Debugging utilities and troubleshooting checklist
- **FastAPI complete example** — Full-featured FastAPI implementation reference
- **Production migration guide** — Step-by-step guide from testing to production environment

### Company Information

- **Company (Chinese)**: 茂為歐買尬數位科技股份有限公司
- **Company (English)**: MacroWell OMG Digital Entertainment Co., Ltd.
- **Service Region**: Taiwan (台灣)
- **API Document Version**: V 1.4.9 (2025-11)

### Supported Features (Complete API Coverage)

#### Core APIs

- **AioCheckOut/V5** — Create Order (one-time, installment, recurring)
- **QueryTradeInfo/V5** — Query Trade Info
- **QueryCreditCardPeriodInfo** — Query Recurring Payment Info
- **CreditCardPeriodAction** — Recurring Payment Action (Cancel)
- **DoAction (CreditDetail/DoAction)** — Credit Card Capture/Refund/Cancel/Abandon
- **QueryTrade/V2 (CreditDetail/QueryTrade/V2)** — Query Credit Card Transaction Detail

#### Supported Payment Methods

- Credit Card one-time payment
- Credit Card installment (3/6/12/18/24/30 periods, E.SUN Bank only)
- Credit Card recurring/subscription (Daily/Monthly/Yearly)
- ATM virtual account (First Bank, CTBC, Union Bank, KGI)
- CVS payment code (CVS code, FamilyMart, 7-11 ibon)
- CVS barcode (3-segment Code39 barcode)
- AFTEE buy now pay later

#### Technical Features

- CheckMacValue SHA256 verification (with .NET URL Encode replacements)
- Payment result notification handling (ReturnURL / OrderResultURL)
- ATM/CVS/BARCODE payment info notification (PaymentInfoURL)
- Recurring payment notification (PeriodReturnURL)
- Extra payment info return (NeedExtraPaidInfo=Y)
- Complete error code reference and debug guide
- Production migration guide
- Idempotency handling and best practices

#### Code Examples

- Python (FastAPI) complete example
- Node.js (Express.js) example
- PHP example
- .NET/C# example
- CheckMacValue calculation (Python / Node.js / PHP / .NET)

### How to Use

#### Method 1: Place in project `.skills` folder (Claude Code / Cowork)

```bash
# In your project root
mkdir -p .skills/skills/omg-payment
cp SKILL.md .skills/skills/omg-payment/SKILL.md
```

Claude Code or Cowork will automatically read this Skill to assist you with payment integration.

#### Method 2: OpenAI / ChatGPT Usage

```bash
# Use the OpenAI format Skill file
cp SKILL_OPENAI.md your-project/
```

Paste the contents of `SKILL_OPENAI.md` into ChatGPT's Custom Instructions, or upload the file and say "Please help me integrate the payment gateway based on this document."

#### Method 3: Tell AI directly

Paste the Skill file contents to the AI, or upload the file and ask for integration help.

### Supported AI Platforms

| AI Platform | File | Method |
|-------------|------|--------|
| Claude Code | SKILL.md | Place in `.skills/skills/omg-payment/` |
| Claude Cowork | SKILL.md | Upload or reference |
| ChatGPT | SKILL_OPENAI.md | Custom Instructions or upload |
| Any AI | Either file | Upload and ask for integration help |

### Test Credentials

| Item | Value |
|------|-------|
| MerchantID | `1000031` |
| HashKey | `265fIDjIvesceXWM` |
| HashIV | `pOOvhGd1V2pJbjfX` |
| Test Card | `4311-9522-2222-2222` |
| CVV | `222` |
| Expiry | Any future date |
| Vendor Backend | `https://vendor-stage.funpoint.com.tw` |
| Backend Login | `funstage001` / `test1234` |

### File Structure

```
omg-payment-skill/
├── README.md                   # This file (bilingual)
├── SKILL.md                    # Claude Skill body (for Claude Code / Cowork)
├── SKILL_OPENAI.md             # OpenAI Skill body (for ChatGPT / OpenAI)
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore rules
└── examples/
    └── fastapi_example.py      # Complete FastAPI integration example (all APIs)
```

---

## 相關主題 | Related Topics

台灣金流串接、歐買尬金流、第三方支付、OMG Payment、線上付款、信用卡付款、ATM 轉帳付款、超商代碼繳費、超商條碼繳費、定期定額扣款、訂閱制付款、電商金流整合、金流 API、Payment Gateway Taiwan、Credit Card Payment、Recurring Payment、E-commerce Payment Integration、AI Skill、Claude Code Skill、ChatGPT Custom Instructions、FastAPI Payment、Python 金流串接、Node.js 金流串接、PHP 金流串接、CheckMacValue、SHA256 驗證、付款結果通知、Webhook 回調、付款閘道、線上刷卡、分期付款、AFTEE 先享後付

## 授權 | License

MIT License - 自由使用、修改、分享。Free to use, modify, and share.

## 作者 | Author

Mitchell Chen

> 本專案由 Mitchell Chen 編寫，透過 [Claude](https://claude.ai/) (Anthropic) AI 輔助完成。
> This project was written by Mitchell Chen, with assistance from [Claude](https://claude.ai/) (Anthropic) AI.
