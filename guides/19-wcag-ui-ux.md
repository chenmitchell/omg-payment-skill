# Guide 19 — 商家 UI/UX 無障礙規範（WCAG AAA）

> **免責聲明**：本指南依 WCAG 2.2 Level AAA、台灣《身心障礙者權益保障法》及「網站無障礙規範 2.0」整理。本 Skill 不構成法律意見；通過本指南之檢查不等於通過 NCC、國發會「無障礙網頁標章」或 VPAT 等正式認證。商家若需正式審驗，應委由第三方無障礙測試機構實施。

本指南是 `guides/11-merchant-homepage.md`（法規揭露）與 `guides/18-merchant-ai-optimization.md`（AI 最佳化）的**第三層補強**：確保商家整合歐買尬金流後，整個購物流程對身心障礙者、低視力者、色盲者、行動不便者、高齡使用者同樣可用。

本 repo 自身的圖表配色遵循 `docs/accessibility.md`，本指南則把同一套原則外推至**商家網站**。

## 為什麼金流串接必須談無障礙

1. **法律面向**：台灣《身心障礙者權益保障法》§52-2 要求政府機關網站符合無障礙規範，雖未強制民間電商，但消費爭議走到法院時，未提供無障礙購物流程可能被認定為「通訊交易管理未盡善良注意」
2. **實務面向**：台灣 65 歲以上人口已逾 17%，弱視與色盲族群合計約佔人口 7–8%，無障礙不是小眾需求而是主流需求
3. **金流關鍵路徑**：從商品頁 → 加入購物車 → 結帳頁 → 導回 OMG → 銀行 3D 驗證 → 回跳成功頁，任何一步不可用，整個交易直接斷裂。AI 助手若只幫商家接好 API 卻讓結帳頁無法用鍵盤操作，等於沒接好
4. **OMG 本身之限制**：OMG 金流頁面（歐買尬託管的結帳頁）由 OMG 控制，商家無法修改。商家的義務僅限「自家網站從商品頁到付款按鈕」與「付款完成的回跳頁」之無障礙品質

## AI 助手的執行規則

當使用者完成金流串接後，AI 助手應主動執行本指南之檢查清單，並於交付訊息中明確告知：

1. 哪些項目已自動產出符合規範
2. 哪些項目需要使用者自行驗證（因涉及視覺 rendering 或實機操作）
3. 哪些項目超出本 Skill 能力範圍（例如實機用 screen reader 測試）

> [!IMPORTANT]
> 本指南列出「合理努力」級別的無障礙要求。若使用者經營醫療、金融、政府標案等高敏感產業，須另聘無障礙顧問做更嚴格的 VPAT / WCAG 2.2 AAA 正式審驗。

## 一、色彩與對比

### 1.1 對比度最低標準

| 元素 | 最小對比度 | WCAG 等級 |
|---|---|---|
| 正文文字（< 18pt） | 7:1 | AAA |
| 大型文字（≥ 18pt 或 ≥ 14pt bold） | 4.5:1 | AAA |
| UI 控制項邊界（按鈕、input 邊框） | 3:1 | AA |
| 狀態訊息（錯誤、成功、警示） | 7:1 | AAA |

**AI 助手產出 CSS 時的義務**：

- 不得使用淺灰底配淺灰字（`#F9FAFB` 底配 `#9CA3AF` 字）等常見的「設計感但不可讀」組合
- 不得使用純紅（`#EF4444`）或純綠（`#22C55E`）作為唯一狀態訊號
- 預設的 button primary 色必須提供 ≥ 7:1 對比於白底，或提供反色版本讓使用者自行切換

### 1.2 建議色盤（與 `docs/accessibility.md` 相同 Okabe-Ito 變體）

```css
:root {
  /* 主要語意 */
  --color-primary:       #1E3A8A; /* Navy — 主按鈕、導覽 */
  --color-secondary:     #3730A3; /* Indigo — 次按鈕 */
  --color-emphasis:      #581C87; /* Purple — 關鍵連結 */

  /* 狀態 */
  --color-success:       #14532D; /* 搭配 ✅ */
  --color-warning:       #78350F; /* 搭配 ⚠️ */
  --color-error:         #7F1D1D; /* 搭配 ❌ */

  /* 資訊層級 */
  --color-info:          #134E4A; /* Teal */
  --color-data:          #164E63; /* Dark Cyan */
  --color-neutral:       #1F2937; /* Slate */

  /* 底色 */
  --color-bg-primary:    #FFFFFF;
  --color-bg-secondary:  #F3F4F6;
  --color-text-primary:  #1F2937;
  --color-text-inverse:  #FFFFFF;
}
```

### 1.3 雙編碼規則

任何傳達「狀態」的 UI 元件必須同時具備以下任兩者：

- 顏色（僅為其中一項）
- 圖示（✅ / ❌ / ⚠️ / ℹ️）
- 文字標籤（「付款成功」「付款失敗」「金額超過上限」）
- 形狀或線型差異（實線 vs 虛線 vs 圓角 vs 直角）

範例（付款結果頁）：

```html
<!-- ✅ 好：顏色 + 圖示 + 文字三重編碼 -->
<div class="result result--success" role="status">
  <span aria-hidden="true">✅</span>
  <strong>付款成功</strong>
  <p>訂單編號 OMG20260412001，我們已寄出確認信至您的信箱。</p>
</div>

<!-- ❌ 壞：僅以顏色表達狀態 -->
<div style="background:#22C55E;color:#fff">付款完成</div>
```

## 二、鍵盤可操作性

整個從「商品頁 → 結帳 → 金流導向」流程**必須可以只用鍵盤完成**。

### 2.1 必要行為

1. **Tab 順序合理**：從上到下、從左到右，與視覺順序一致
2. **Focus indicator 明顯**：每個 focusable 元素於 `:focus-visible` 時必須顯示 ≥ 3px 的外框，顏色對比 ≥ 3:1，不可以 `outline: none` 移除
3. **不得有 keyboard trap**：使用者進入 modal 或下拉後必須能用 `Esc` 或 `Shift+Tab` 離開
4. **跳至主內容連結**：於 `<body>` 最頂端提供 `Skip to main content`，讓使用者跳過導覽列
5. **Enter 與 Space 可觸發按鈕**：若使用 `<div>` 或 `<a>` 偽裝按鈕，必須補上 `role="button"` + `tabindex="0"` + `keydown` 監聽

範例（skip link）：

```html
<body>
  <a class="skip-link" href="#main">跳至主內容</a>
  <header>...</header>
  <main id="main">...</main>
</body>

<style>
.skip-link {
  position: absolute;
  top: -100px;
  left: 0;
  background: #1E3A8A;
  color: #FFFFFF;
  padding: 1rem;
  z-index: 9999;
}
.skip-link:focus {
  top: 0;
}
</style>
```

### 2.2 付款按鈕的鍵盤行為

付款按鈕必須是原生 `<button type="submit">` 或 `<form>` 的 submit 元素，避免使用 `<a onclick>` 或 `<div onclick>`。原因：

- 螢幕閱讀器會把原生按鈕唸為「按鈕」，自訂元素只會唸為「連結」或無描述
- 使用者按 Enter 時原生按鈕會自動 submit，自訂元素需額外 JS 處理
- 若 JS 載入失敗，原生按鈕仍可運作，自訂元素直接壞掉

```html
<!-- ✅ 好 -->
<form action="/api/create-order" method="post">
  <button type="submit" class="btn-pay">
    確認付款 NTD 1,200
  </button>
</form>

<!-- ❌ 壞 -->
<div class="btn-pay" onclick="createOrder()">確認付款</div>
```

## 三、語義化 HTML 與 ARIA

### 3.1 地標元素（Landmark）

每一頁至少包含：

- `<header>` — 導覽列
- `<nav aria-label="主選單">`
- `<main>` — 主內容
- `<footer>`

螢幕閱讀器可快速跳轉地標，不必逐段閱讀。

### 3.2 表單元素

```html
<!-- ✅ label 與 input 正確綁定 -->
<label for="email">電子郵件</label>
<input type="email" id="email" name="email" required
       aria-describedby="email-hint"
       autocomplete="email">
<p id="email-hint" class="form-hint">
  付款完成後將寄送收據至此信箱
</p>
```

**禁用做法**：

- 只用 `placeholder` 代替 `label`（placeholder 於輸入後消失，認知障礙使用者無法回頭確認）
- 於 `<input>` 外包 `<label>` 但缺 `for` 屬性（部分 screen reader 無法正確綁定）
- 在 `required` input 上只用紅色 `*` 表示必填（色盲看不見）

### 3.3 錯誤訊息

```html
<label for="card-number">信用卡號</label>
<input type="text" id="card-number"
       aria-invalid="true"
       aria-describedby="card-error">
<p id="card-error" role="alert" class="form-error">
  <span aria-hidden="true">⚠️</span>
  卡號格式錯誤，請輸入 16 位數字
</p>
```

`role="alert"` 會讓 screen reader 立即朗讀錯誤訊息，無須使用者額外互動。

> [!WARNING]
> 信用卡號不得由商家自家前端收集後送至 OMG。信用卡資料的鍵入必須於 OMG 金流頁面完成，以符合 PCI-DSS 要求。上面的範例僅為結帳**前**其他表單欄位（如 email、配送地址）的錯誤處理示意。

## 四、動態內容與通知

### 4.1 Live region

付款流程中常見「輪詢訂單狀態」或「倒數計時」之類的動態更新，必須讓 screen reader 使用者也能接收到：

```html
<div aria-live="polite" aria-atomic="true">
  <p id="order-status">訂單處理中...</p>
</div>
```

- `aria-live="polite"`：下次 screen reader 空閒時朗讀（適合狀態更新）
- `aria-live="assertive"`：立即中斷朗讀（僅用於錯誤、超時等關鍵訊息）

### 4.2 Session timeout

若商家結帳頁有 session timeout（例如 15 分鐘未完成付款則清除購物車），必須：

1. 於 timeout 前 2 分鐘主動告知使用者，並提供「延長」按鈕
2. timeout 後清楚告知原因，並保留使用者已填資料不清空
3. 不得無預警直接跳轉或登出

## 五、行動裝置

### 5.1 觸控目標大小

所有可點擊元素必須 ≥ 44 × 44 CSS 像素（WCAG 2.5.5 AAA）。按鈕之間必須保留至少 8px 間距，避免誤觸。

```css
.btn, a.btn, input[type="button"] {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px;
}

.btn + .btn {
  margin-left: 8px;
}
```

### 5.2 縮放

不得於 `<meta viewport>` 中停用縮放：

```html
<!-- ✅ 好 -->
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- ❌ 壞：user-scalable=no 已被 WCAG 2.2 明令禁止 -->
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
```

### 5.3 橫向與直向

結帳頁必須同時支援 portrait 與 landscape。部分行動障礙者會把手機固定於輪椅支架上無法旋轉，若只支援直向等於把這部分使用者排除在外。

## 六、金流特有的無障礙議題

### 6.1 3D Secure 驗證頁

當 OMG 將使用者導向發卡銀行的 3D Secure 驗證頁時，商家無法修改該頁面。但商家的前後流程必須：

1. **導向前**：告知使用者「接下來將跳轉至發卡銀行驗證頁，請依銀行 App / 簡訊完成驗證」
2. **驗證失敗回跳**：清楚顯示失敗原因與重試選項，不得只顯示「付款失敗」四個字
3. **驗證超時**：提供「重新發起付款」按鈕，避免使用者困在中繼頁

### 6.2 超商代碼與 ATM 虛擬帳號

若使用者選擇超商代碼或 ATM 虛擬帳號，商家的「待繳費頁」必須：

1. 以大字體（≥ 24px）顯示繳費代碼 / 虛擬帳號
2. 提供「複製」按鈕（含 `aria-label="複製繳費代碼"`）
3. 複製成功後以 `aria-live="polite"` 告知「已複製」
4. 同步寄送含繳費資訊的 email，避免使用者離開頁面後資訊遺失

### 6.3 退款確認頁

若退款流程由使用者自行於前台操作（非僅透過 admin bot），退款確認頁必須：

1. 清楚顯示「退款金額」與「退回來源（原付款卡 / 原帳戶）」
2. 提供「確認」與「取消」兩個按鈕，間距 ≥ 8px
3. 按鈕必須能鍵盤操作，且 `Esc` 可關閉
4. 退款為不可逆操作，按鈕文字必須清楚（「確認退款 NTD X」而非「OK」）

## 七、自動化檢查工具

AI 助手可主動執行下列工具，對商家網站做初步掃描：

| 工具 | 用途 | 執行方式 |
|---|---|---|
| axe-core | WCAG 2.2 違規掃描 | `npm install -D @axe-core/cli && axe https://your-site.tw` |
| Lighthouse | 綜合性能與無障礙評分 | `npx lighthouse https://your-site.tw --only-categories=accessibility` |
| pa11y | Command-line 無障礙測試 | `npm install -g pa11y && pa11y https://your-site.tw` |
| WAVE | 視覺化標註違規 | <https://wave.webaim.org/> 貼網址 |
| Color Contrast Analyzer | 對比度檢查 | TPG 出品的 Mac/Windows 桌面工具 |

> [!NOTE]
> 自動化工具僅能檢出約 30–40% 的無障礙問題，其餘需靠手動測試（鍵盤、screen reader、放大鏡模擬）與使用者研究。AI 助手不得因自動化工具通過就宣告「已達 WCAG AAA」。

## 八、AI 助手的交付檢查清單

AI 助手產出商家前台程式碼後，必須於交付訊息中逐項回報：

- [ ] 全站色彩符合 §1.1 對比度標準
- [ ] 狀態訊息採用 §1.3 雙編碼（顏色 + 圖示 + 文字）
- [ ] 所有 focusable 元素有明顯 `:focus-visible` 外框
- [ ] 有 `Skip to main content` 連結
- [ ] 付款按鈕使用原生 `<button type="submit">`
- [ ] 所有表單 `<label>` 正確綁定 `<input>`
- [ ] 必填欄位不僅以顏色標示
- [ ] 錯誤訊息使用 `role="alert"`
- [ ] 動態狀態更新使用 `aria-live`
- [ ] 觸控目標 ≥ 44 × 44 px
- [ ] `<meta viewport>` 未停用 `user-scalable`
- [ ] Session timeout 於前 2 分鐘主動警示
- [ ] 3D Secure 導向前有明確告知
- [ ] 超商代碼 / ATM 虛擬帳號頁提供複製按鈕與 email 備份

若任一項無法確認，AI 助手必須於交付訊息中明確標示「此項需您自行驗證」或「此項超出本 Skill 能力範圍」，**不得隱瞞或代為宣稱已通過**。

## 九、與其他 guide 的關係

| Guide | 主題 | 19 的角色 |
|---|---|---|
| `guides/11-merchant-homepage.md` | 法規揭露 | 19 補充：揭露必須對身障者可讀 |
| `guides/12-product-page.md` | 商品頁法規 | 19 補充：商品頁必須可鍵盤操作 |
| `guides/18-merchant-ai-optimization.md` | AI 最佳化 | 19 與 18 並列：18 談被 AI 看見，19 談被人類看見 |
| `docs/accessibility.md` | 本 repo 自身規範 | 19 是其外推版本 |

## 十、參考資料

- [WCAG 2.2 Level AAA](https://www.w3.org/TR/WCAG22/)
- [WebAIM — Web Accessibility Checklist](https://webaim.org/standards/wcag/checklist)
- [MDN — ARIA](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)
- 台灣 [國家通訊傳播委員會 — 無障礙網頁開發規範 2.0](https://accessibility.ncc.gov.tw/)
- [A11y Project — Checklist](https://www.a11yproject.com/checklist/)

---

> [!IMPORTANT]
> 本 Skill 的無障礙建議係最低合理努力。正式申請「無障礙網頁標章」或對外宣稱通過 WCAG 2.2 AAA 前，必須委由具資格之第三方測試機構進行實機審驗。AI 助手不得代替使用者做此宣告。
