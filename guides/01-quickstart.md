# Guide 01 — Quickstart

依下列步驟操作，即可於 30 分鐘內完成歐買尬金流整合、測試儀表板與通知機器人的啟動。全部指令可直接複製執行。

> 本 Skill 為社群維護之非官方資源，與 MacroWell OMG Digital Entertainment Co., Ltd. 無隸屬關係。

## 事前準備

請於開始前備妥下列資訊：

1. 歐買尬商家後台帳號（測試環境之 MerchantID 可使用官方公告之 `1000031`）
2. 具備 Python 3.10 以上之電腦（macOS、Windows、Linux 皆可）
3. 具備 Git（若不熟悉，可直接下載 repo zip 檔）
4. Telegram 帳號（若需付款通知機器人）
5. Discord 帳號（若需 Discord 通知機器人）

Python 安裝方式請參考官方網站 https://www.python.org/downloads/。安裝時請勾選「Add Python to PATH」。

## 步驟 1：取得程式碼

```bash
git clone https://github.com/<your-fork>/omg-payment-skill.git
cd omg-payment-skill
```

若不熟悉 Git，亦可於 GitHub 網頁點選 Code → Download ZIP，解壓後以檔案總管進入該資料夾。

## 步驟 2：安裝相依套件

於專案資料夾中執行下列指令：

```bash
pip install -r templates/omg-test-console/requirements.txt
```

若您使用 macOS 且系統內建 Python 版本為 3.9 以下，請改用 `python3 -m pip install -r ...`。

## 步驟 3：填寫環境變數

複製 `.env.example` 為 `.env`，並以任何文字編輯器開啟：

```bash
cp templates/omg-test-console/.env.example templates/omg-test-console/.env
```

填寫下列欄位（其餘欄位可暫時保留預設值）：

```
OMG_MERCHANT_ID=1000031
OMG_HASH_KEY=<從歐買尬後台取得之 HashKey>
OMG_HASH_IV=<從歐買尬後台取得之 HashIV>
OMG_API_HOST_STAGE=<歐買尬測試環境 API host>
```

測試環境金鑰應於歐買尬商家後台「開發者設定」取得。若僅需體驗本 Skill，可先使用官方公告之測試參數。

## 步驟 4：啟動測試儀表板

```bash
cd templates/omg-test-console
python backend.py
```

啟動成功後，終端機將顯示：

```
Uvicorn running on http://127.0.0.1:8787
```

開啟瀏覽器進入 `http://127.0.0.1:8787/`，即可看到測試儀表板介面。

## 步驟 5：執行一鍵全鏈路測試

於儀表板點擊「一鍵全鏈路測試」按鈕，系統將依序執行：

1. 建立訂單（`create_order`）
2. CheckMacValue 簽名驗證
3. HTTP POST 至測試環境
4. 查詢訂單（`query_order`）
5. Refund 簽名計算
6. Webhook 接收器自我驗證

若五項步驟全部顯示綠燈，表示整合成功。詳細流程可參考 `guides/06-test-dashboard.md`。

## 常見問題

**Q1：點擊「一鍵全鏈路測試」後顯示紅燈，錯誤訊息為「CheckMacValue Error」**

A：請確認 `.env` 中的 `OMG_HASH_KEY` 與 `OMG_HASH_IV` 是否與歐買尬後台設定完全一致。常見錯誤：

- 複製時誤加空白或換行
- 大小寫錯誤
- 使用了歐付寶（OPay）的金鑰（兩者為不同公司）

**Q2：無法連線至測試環境 API**

A：請確認 `OMG_API_HOST_STAGE` 是否為歐買尬測試環境之完整 URL。若公司或學校網路有擋外連，可嘗試切換行動網路或其他網路環境。

**Q3：瀏覽器打不開 `http://127.0.0.1:8787/`**

A：確認步驟 4 執行之終端機是否仍顯示 `Uvicorn running` 訊息。若無，代表服務未啟動或已被中斷，請重新執行 `python backend.py`。

**Q4：想要讓測試儀表板收到付款通知**

A：測試儀表板內建 webhook 接收器，URL 為 `http://127.0.0.1:8787/webhook`。若需歐買尬真實測試環境呼叫回此 URL，需要搭配 ngrok 或類似工具將本機服務暴露為公開 URL。詳細步驟見 `guides/17-troubleshooting.md`。

## 下一步

測試儀表板驗證通過後，可依需求繼續：

- **啟動 Telegram 通知機器人**：見 `guides/08-telegram-bot.md`
- **啟動 Discord 通知機器人**：見 `guides/09-discord-bot.md`
- **建置正式環境健康監控儀表板**：見 `guides/07-prod-dashboard.md`
- **套用法規揭露範本**：見 `guides/11-merchant-homepage.md` 至 `guides/15-legal-refund.md`

## 一句話啟動指令（進階）

若您已熟悉本 Skill 的結構，可使用單一 AI 指令完成全流程：

```
請依 omg-payment skill 幫我整合歐買尬金流，全部依預設，我經營 {{商品類型}}
```

AI 助手將依 `guides/00-onboarding.md` 定義之流程自動執行 15 步整合作業，並於結束時統一請您補齊商家資訊。
