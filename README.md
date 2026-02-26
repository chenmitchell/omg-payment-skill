# OMG 金流串接 Skill | OMG Payment Gateway Skill

> **繁體中文** | [English](#english)

---

## 繁體中文

### 這是什麼？

這是一個 **Claude Skill 檔案**，讓 AI 助手（如 Claude Code、Cowork）能夠理解 OMG 金流（歐買尬第三方支付）的 API 規格，並協助開發者快速產生正確的串接程式碼。

### 支援功能

- 信用卡一次性付款
- 信用卡定期定額（訂閱制）
- CheckMacValue SHA256 驗證
- 付款結果通知處理
- 取消定期定額
- ATM / 超商代碼 / 超商條碼付款

### 如何使用

#### 方法一：放入專案 .skills 資料夾

在你的專案根目錄執行:
mkdir -p .skills/skills/omg-payment
cp SKILL.md .skills/skills/omg-payment/SKILL.md

Claude Code 或 Cowork 會自動讀取此 Skill 來協助你串接金流。

#### 方法二：直接告訴 AI

將 SKILL.md 的內容貼給 AI，或上傳檔案後說「請根據這份金流文件幫我串接」。

### 測試帳號

MerchantID: 1000031
HashKey: 265fIDjIvesceXWM
HashIV: pOOvhGd1V2pJbjfX
測試卡號: 4311-9522-2222-2222
CVV: 222
有效期限: 任意未過期月/年

---

## English

### What is this?

This is a Claude Skill file that enables AI assistants (such as Claude Code, Cowork) to understand the OMG Payment Gateway API specification and help developers quickly generate correct integration code.

### Test Credentials

MerchantID: 1000031
HashKey: 265fIDjIvesceXWM
HashIV: pOOvhGd1V2pJbjfX
Test Card: 4311-9522-2222-2222
CVV: 222

## License

MIT License

## Author

Mitch Chen
