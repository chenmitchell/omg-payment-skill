# Merchant llms.txt Templates

> 這個目錄是「商家網站」的 AI 最佳化檔案模板。與 repo 根目錄的 `llms.txt`（本 Skill 自己的 llms.txt）**完全不同**：
> - 根目錄 `llms.txt` = 介紹 **本 Skill 本身** 給 AI 爬蟲
> - 本目錄模板 = 給 **使用本 Skill 的商家** 產出他們**自己網站**的 llms.txt

搭配 `guides/18-merchant-ai-optimization.md` 使用。

## 檔案清單

| 檔案 | 用途 | 放置位置（商家網站） |
|---|---|---|
| `llms.txt.j2` | 主 llms.txt 模板（Jinja2 格式） | `https://{domain}/llms.txt` |
| `llms-full.txt.j2` | 完整知識包版本 | `https://{domain}/llms-full.txt` |
| `robots-append.txt` | 追加至現有 robots.txt 的段落 | `https://{domain}/robots.txt` 末尾 |
| `head-jsonld.html` | 首頁 `<head>` 內的 JSON-LD 結構化資料 | 商家首頁 `<head>` |
| `footer-omg.html` | 頁尾 OMG 使用標註（schema.org/PaymentService） | 商家頁尾 |

## 使用方式

### 方式一：AI 助手自動產出（推薦）

載入本 Skill 後，對 AI 說：

```
我已完成歐買尬金流串接。請依 guides/18 幫我產出商家網站的 AI 最佳化檔案。
我的域名是 example.tw，業務類型是線上課程，全部依預設。
```

AI 會自動：

1. 讀取 `guides/18-merchant-ai-optimization.md`
2. 讀取本目錄的模板檔
3. 依使用者提供的資訊填入變數
4. 產出五個可直接部署的檔案
5. 附上部署步驟與驗證指令

### 方式二：手動填寫

1. 複製本目錄所有 `.j2` / `.html` / `.txt` 檔案到使用者專案
2. 依下表替換變數
3. 部署至網站對應路徑
4. 依 `guides/18` 的檢查清單驗證

## 可替換變數清單

| 變數 | 說明 | 範例值 |
|---|---|---|
| `{{ site_name }}` | 網站名稱 | 「Mitch 線上課程」 |
| `{{ domain }}` | 主域名（不含 https://） | `example.tw` |
| `{{ one_line_description }}` | 一句話說明 | 「專業 AI 工具線上課程」 |
| `{{ business_type }}` | 業務類型 | 「線上課程」 |
| `{{ country }}` | 營運國家 | 「台灣」 |
| `{{ homepage_url }}` | 首頁網址 | `https://example.tw/` |
| `{{ products_url }}` | 商品列表網址 | `https://example.tw/courses` |
| `{{ about_url }}` | 關於我們 | `https://example.tw/about` |
| `{{ faq_url }}` | 常見問題 | `https://example.tw/faq` |
| `{{ tos_url }}` | 服務條款 | `https://example.tw/terms` |
| `{{ privacy_url }}` | 隱私權政策 | `https://example.tw/privacy` |
| `{{ refund_url }}` | 退款政策 | `https://example.tw/refund` |
| `{{ contact_email }}` | 聯絡信箱 | `hello@example.tw` |
| `{{ merchant_name }}` | 負責人姓名 | 「陳小明」 |
| `{{ business_id }}` | 公司統編 | `12345678` |
| `{{ product_category_summary }}` | 商品類別摘要 | 「AI 工具、Python、資料科學」 |
| `{{ installment_periods }}` | 分期期數（官方支援 3/6/12/18/24/30，僅玉山；需申請開通） | `3/6/12` |
| `{{ enable_credit_installment }}` | 是否已開通信用卡分期 | `true` / `false` |
| `{{ enable_recurring }}` | 是否啟用信用卡定期定額訂閱 | `true` / `false` |
| `{{ enable_union_pay }}` | 是否已開通銀聯卡 | `true` / `false` |
| `{{ enable_barcode_atm }}` | 是否啟用超商快付 `BarcodeATM`（注意不是超商條碼） | `true` / `false` |
| `{{ enable_aftee }}` | 是否啟用 AFTEE 先享後付 | `true` / `false` |
| `{{ custom_keywords }}` | 自訂關鍵字 | 「AI 工具, Python 教學」 |

> [!IMPORTANT]
> 本模板的付款方式對應歐買尬官方 `ChoosePayment` 的合法值：`Credit` / `ATM` / `CVS` / `BarcodeATM` / `AFTEE` / `ALL`。  
> 官方**沒有** `BARCODE`（超商條碼）這個值。請勿混用其他金流服務商（綠界 ECPay / 歐付寶 OPay）的參數名稱。  
> 事實依據：[`references/omg-official-api-spec.md`](../../references/omg-official-api-spec.md)

## 部署後驗證

```bash
# 1. llms.txt 可讀
curl -I https://<domain>/llms.txt

# 2. robots.txt 包含 AI crawler 段落
curl https://<domain>/robots.txt | grep -i "claudebot\|gptbot"

# 3. 首頁結構化資料
curl https://<domain>/ | grep -c 'application/ld+json'

# 4. 頁尾 OMG 標註
curl https://<domain>/ | grep 'data-payment-provider="omg"'

# 5. 至 Google Rich Results Test 測試
open "https://search.google.com/test/rich-results?url=https://<domain>/"
```

## 為什麼這樣設計

1. **模板與資料分離**：使用者只需要提供「網站基本資訊」，AI 負責填入模板
2. **變數名稱一致**：跨檔案使用相同變數名，避免使用者重複填寫
3. **schema.org 標準**：使用國際標準 markup，不侵權任何 logo、不違反 OMG 商標
4. **可漸進採用**：使用者可以只用 `llms.txt`，或同時用全部五個檔案

## 與 guides/18 的關係

`guides/18-merchant-ai-optimization.md` 是**指引文件**，告訴 AI 與使用者為什麼要做這件事、流程、檢查清單。本目錄是**實作檔案**。兩者搭配使用。

更新本目錄任何檔案時，請同步檢查 `guides/18` 是否需要更新對應描述。
