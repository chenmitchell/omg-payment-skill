# vscode_copilot — VS Code + GitHub Copilot Chat 使用指引

本文件說明如何將 OMG Payment Skill 整合至 VS Code 中的 GitHub Copilot Chat。

> [!IMPORTANT]
> 本 Skill 是個人社群專案，不是 OMG 的官方資源，也未取得任何官方背書。若內容與官方文件不一致，以 <https://github.com/omgtwhub/> 為準。本 Skill 的架構參考自綠界科技的 ECPay-API-Skill，在此致謝。
>
> 申請 OMG 會員、取得正式環境金鑰請至官方註冊頁：<https://www.funpoint.com.tw/member/register>

---

## 一、前置條件

- VS Code（最新版）
- GitHub Copilot 訂閱（Individual 或 Business）
- GitHub Copilot Chat 擴充套件

---

## 二、安裝方式

Copilot Chat 會於工作區內自動讀取 `.github/copilot-instructions.md`。將本 Skill 的關鍵內容寫入該檔案即可。

### 步驟 1：建立 copilot-instructions.md

於您的專案根目錄：

```bash
mkdir -p .github
cp SKILL.md .github/copilot-instructions.md
```

或手動建立，內容包含下列區塊：

```markdown
# Project Instructions (OMG Payment Integration)

本專案使用歐買尬（OMG）金流。請依下列規則協助開發：

## 非官方聲明
社群維護之 Skill，非歐買尬官方。官方資源：https://github.com/omgtwhub/

## 公司區辨
歐買尬（OMG）≠ 歐付寶（OPay）。本專案串接歐買尬。

## 執行規則
1. 新增 webhook 路由時，必須使用 SELECT ... FOR UPDATE 搭配 idempotency_key 處理重送
2. 新增 admin endpoint 時，必須同步更新 Telegram/Discord bot 選單
3. HashKey/HashIV 只寫入 .env
4. 退款採警示不阻擋原則
5. 正式環境禁用 create_order 作為健康檢查

## 主要檔案
- backend/webhook.py — webhook 路由
- backend/idempotency.py — 冪等性處理
- backend/admin.py — 管理 API
- bots/telegram_bot.py — Telegram 通知
- bots/discord_bot.py — Discord 通知

## 參考文件
docs 完整於 omg-payment-skill/ 資料夾或請求 Copilot 引用 SKILL.md。
```

### 步驟 2：引用本 Skill 之文件

於 Copilot Chat 對話中，使用 `#file` 指令引用 guide：

```
#file:SKILL.md 幫我實作歐買尬 webhook 冪等性處理
#file:guides/05-webhook-idempotency.md 請依此參考實作改寫我的 handler
#file:references/check-mac-value.md 幫我驗證我的 MAC 計算
```

---

## 三、工作區設定

建議於 `.vscode/settings.json` 中加入下列設定：

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "本專案使用歐買尬（OMG, 非歐付寶）金流。冪等性必須 race-safe。HashKey/HashIV 只寫 .env。正式環境禁用 create_order 作為健康檢查。退款採警示不阻擋原則。"
    },
    {
      "file": ".github/copilot-instructions.md"
    }
  ],
  "github.copilot.chat.testGeneration.instructions": [
    {
      "text": "測試必須涵蓋 webhook 重送情境與 CheckMacValue 驗證。參考 test-vectors/check-mac-value.json。"
    }
  ]
}
```

---

## 四、常用 Prompt

### 新增 webhook handler

```
@workspace 依本專案之 copilot-instructions 幫我新增一個歐買尬 webhook handler，
要 race-safe，使用 SELECT ... FOR UPDATE 與 idempotency_key unique index。
```

### 新增退款 endpoint

```
@workspace 幫我新增退款 endpoint /api/admin/refund，要符合警示不阻擋原則：
單筆超過 50000、當日超過 100000、當日超過 20 筆時只警示不拒絕。
同時幫我更新 bots/telegram_bot.py 與 bots/discord_bot.py 的選單。
```

### 檢查 CheckMacValue 實作

```
#file:references/check-mac-value.md #file:backend/mac_value.py
檢查我的 MAC 計算是否符合本 Skill 的規範，特別是 .NET 字元還原部分。
```

---

## 五、Pull Request Copilot

若您的專案啟用 GitHub Pull Request Copilot，可於 PR description 中要求 Copilot 檢查：

```
/copilot review

重點檢查：
1. 是否有任何 admin endpoint 新增但未同步更新 bot 選單
2. 是否有 HashKey/HashIV 洩漏至程式碼或 commit
3. webhook handler 是否 race-safe
4. 是否使用 create_order 作為正式環境健康檢查
```

---

## 六、官方資源優先

Copilot 於回應 API 精確規格問題時，請使用者交叉驗證：

- 官方 AI 金流 Skill：<https://github.com/omgtwhub/>
- 歐買尬商家後台「開發者設定」

本 Skill 不取代官方文件。
