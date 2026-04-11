# /omg-legal

產出台灣合規揭露與法規公版範例。

## 用法

```
/omg-legal                     產出全部（服務條款 / 隱私權 / 退貨退款 / 首頁 / 商品頁）
/omg-legal tos                 僅服務條款
/omg-legal privacy             僅隱私權政策
/omg-legal refund              僅退貨退款政策
/omg-legal homepage            僅首頁與頁尾必要揭露
/omg-legal product             僅商品頁必要揭露
```

## AI 執行流程

1. 讀取對應之 `guides/13-legal-tos.md`、`guides/14-legal-privacy.md`、`guides/15-legal-refund.md`、`guides/11-merchant-homepage.md`、`guides/12-product-page.md`
2. 替換所有 `{{變數}}` 佔位符
3. 若使用者之商品類型為「數位下載」或「線上課程」，應於退貨退款政策中保留七日猶豫期例外條款
4. 產出檔案後於交付訊息中強調免責聲明與律師審閱建議

## 強制免責聲明

所有法規檔案之開頭必須包含：

> 本範例僅為參考，不構成法律意見。上線前請委請法務顧問或律師審閱，並依實際營運狀況調整。

AI 不得於交付訊息中宣稱產出之範本「已符合法規」或「可直接使用」，應使用「已提供公版範本供參考」等保留性語句。

## 變數

| 變數 | 來源 |
|---|---|
| `{{商家名}}` | onboarding 收集 |
| `{{統一編號}}` | onboarding 收集 |
| `{{負責人}}` | onboarding 收集 |
| `{{客服Email}}` | onboarding 收集 |
| `{{客服電話}}` | onboarding 收集 |
| `{{營業地址}}` | onboarding 收集 |
| `{{網站網址}}` | onboarding 收集 |
| `{{管轄法院}}` | onboarding 收集 |
| `{{出貨天數}}` | onboarding 收集 |
| `{{年份}}` / `{{月}}` / `{{日}}` | 自動填入當前日期 |
