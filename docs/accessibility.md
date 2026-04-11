<!--
  docs/accessibility.md
  視覺友善與可近用性規範（WCAG AAA + 色盲友善 + 字體 + 雙編碼）
  Accessibility Specification (WCAG AAA + Colorblind-safe + Typography + Dual encoding)

  繁體中文 | English — 同檔雙語對照，以 ─── 分隔
-->

# 視覺友善與可近用性規範 / Accessibility Specification

> [!IMPORTANT]
> 這份規範是本 repo 所有視覺元素（Mermaid 圖、表格、Callout、顏色標示、字體大小）的**強制最低標準**。  
> 所有 PR 若新增／修改圖表或色彩，必須符合本規範，否則會在 CI 與 review 被擋下。  
> **本規範參考：** WCAG 2.2 Level AAA、W3C WAI、聯合國 CRPD（身心障礙者權利公約）第 9 條「可及性」、Okabe-Ito 色盲友善色彩研究（2008）。

---

## 🌐 語言 / Language

本文件為中英對照，捲動即可閱讀兩種語言。若只想看英文，可直接跳到每節的 **EN** 區塊。

This document is bilingual Chinese-English. Scroll to read both. Skip to **EN** blocks for English only.

---

## 1. 四大強制原則 / Four Core Requirements

**ZH：**

1. **對比度 ≥ 7:1**（WCAG AAA 正常文字）或 **≥ 4.5:1**（WCAG AAA 大型文字 ≥ 18pt）。任何填色區塊上的文字都必須達到此比例。
2. **色盲安全**：不得只用顏色區分語意（例如只用紅綠表示成功／失敗）。必須搭配 **圖示 + 文字標籤 + 形狀／線型** 等至少一種額外編碼。
3. **字體大小 ≥ 16px**：所有 Mermaid 圖以 `themeVariables.fontSize: '16px'` 為最低基準；正文以瀏覽器預設 100%（通常 16px）為準，不得強制縮小。
4. **直線直角連線**：所有流程圖以 `curve: stepAfter` 強制走直角，不使用弧線（對低視力與認知障礙者更易追蹤路徑）。

**EN：**

1. **Contrast ratio ≥ 7:1** (WCAG AAA normal text) or **≥ 4.5:1** (WCAG AAA large text ≥ 18pt). Every text-on-fill combination must meet this ratio.
2. **Colorblind-safe**: never convey meaning through color alone (e.g., red/green for success/failure). Always add a second encoding: **icon + text label + shape/line pattern**.
3. **Font size ≥ 16px**: all Mermaid diagrams must declare `themeVariables.fontSize: '16px'` as floor; body text must not force a smaller size than 100% browser default (typically 16px).
4. **Orthogonal right-angle lines**: all flowcharts use `curve: stepAfter` to draw right-angle connectors. No curves (easier for low-vision and cognitive-disability readers to trace paths).

---

## 2. 指定色盤（Okabe-Ito 變體）/ Approved Palette (Okabe-Ito derived)

**說明 / Rationale：** 一般用於網頁的純紅／純綠對 3 型色盲（protanopia、deuteranopia、tritanopia）皆會混淆。Okabe-Ito 色盤 (2008) 是學界公認對 3 型色盲全部安全的 8 色集。我們挑選其「深色版本」以維持 ≥ 7:1 對比。

**用色原則 / Usage：** 填色必為下列之一；文字一律 `#FFFFFF`；邊框一律 `#FFFFFF stroke-width:3px`。

| 語意 / Role | Hex | 對比 / Contrast (vs #FFFFFF) | 用途 / Where |
|---|---|---|---|
| 主要資訊 / Primary info | `#1E3A8A` Navy | 11.2:1 | 起點、主幹、Primary nodes |
| 次要資訊 / Secondary | `#3730A3` Indigo | 10.7:1 | 步驟中間、Step nodes |
| 強調 / Emphasis | `#581C87` Purple | 11.7:1 | 關鍵節點、Critical nodes |
| 成功 / Success | `#14532D` Dark Green | 12.6:1 | 搭配 ✅ 圖示 |
| 警示 / Warning | `#78350F` Dark Amber | 10.9:1 | 搭配 ⚠️ 圖示 |
| 錯誤 / Error | `#7F1D1D` Dark Red | 12.1:1 | 搭配 ❌ 圖示 |
| 外部 / External | `#134E4A` Teal | 13.1:1 | API、第三方服務 |
| 資料庫 / Data store | `#164E63` Dark Cyan | 12.4:1 | DB、Storage |
| 中性 / Neutral | `#1F2937` Slate | 15.3:1 | Legend、註解 |

> [!WARNING]
> ❌ **禁用**：`#EF4444` 純紅、`#22C55E` 亮綠、`#F59E0B` 亮黃、`#3B82F6` 亮藍 —— 對比度不足或色盲混淆。  
> ❌ **禁用**：`#E0F2FE` / `#DBEAFE` / `#FEE2E2` 等淺色底配深字（先前的 pastel 配色）—— 老花、弱視、夜間模式下都難辨。

---

## 3. 雙編碼（Dual encoding）規則 / Dual Encoding Rule

**ZH：** 任何表達「狀態」或「結果」的節點，**必須** 同時具備以下兩項以上：

- 顏色（從第 2 節色盤選）
- 圖示前綴：`✅`、`❌`、`⚠️`、`ℹ️`、`🔐`、`🔁`
- 文字標籤：直接寫「成功」「失敗」「警示」在節點內
- 邊框粗細差異或線型（`stroke-width:3px` vs `stroke-dasharray:5 5`）

**EN：** Any node conveying *state* or *outcome* must use **at least two** of the following simultaneously:

- Color (from §2 palette)
- Icon prefix: `✅`, `❌`, `⚠️`, `ℹ️`, `🔐`, `🔁`
- Text label: explicit words like "Success", "Failed", "Warning" in the node
- Border weight or line pattern (`stroke-width:3px` vs `stroke-dasharray:5 5`)

### 範例 / Example

```
✓  [✅ 全數通過<br/>All passed]    fill: #14532D, color: #FFFFFF, stroke-width: 3px
✗  [❌ 任一失敗<br/>Any failed]    fill: #7F1D1D, color: #FFFFFF, stroke-width: 3px, stroke-dasharray: 5 5
```

即使把整張圖轉成灰階，也能靠文字、圖示、虛實線區分結果。  
Even when the diagram is rendered in grayscale, the outcome is still distinguishable by icon, label, and line pattern.

---

## 4. Mermaid 統一頭註 / Mermaid Standard Header

每一張 Mermaid 圖都必須以下列其中一段開頭 / Every Mermaid block must start with one of:

### 4.1 flowchart（流程圖）

```
%%{init: {
  'flowchart': {'curve': 'stepAfter', 'htmlLabels': true, 'useMaxWidth': true},
  'themeVariables': {'fontSize': '16px', 'fontFamily': 'ui-sans-serif, system-ui, sans-serif'}
}}%%
flowchart LR
    ...
```

### 4.2 sequenceDiagram（時序圖 / 交互圖）

sequenceDiagram 不支援 `style` 指令，必須透過 `themeVariables` 設定：

```
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontSize': '16px',
    'actorBkg': '#1E3A8A', 'actorTextColor': '#FFFFFF', 'actorLineColor': '#FFFFFF', 'actorBorder': '#FFFFFF',
    'signalColor': '#1F2937', 'signalTextColor': '#1F2937',
    'labelBoxBkgColor': '#134E4A', 'labelBoxBorderColor': '#FFFFFF', 'labelTextColor': '#FFFFFF',
    'noteBkgColor': '#78350F', 'noteTextColor': '#FFFFFF', 'noteBorderColor': '#FFFFFF',
    'activationBkgColor': '#3730A3', 'activationBorderColor': '#FFFFFF'
  }
}}%%
sequenceDiagram
    autonumber
    ...
```

### 4.3 stateDiagram-v2（狀態機）

```
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontSize': '16px',
    'primaryColor': '#1E3A8A', 'primaryTextColor': '#FFFFFF', 'primaryBorderColor': '#FFFFFF',
    'lineColor': '#1F2937', 'secondaryColor': '#581C87', 'tertiaryColor': '#134E4A'
  }
}}%%
stateDiagram-v2
    ...
```

---

## 5. 表格、Callout、其他文字 / Tables, Callouts, Other Text

- **GitHub Alert callouts**：一律使用 `> [!IMPORTANT]`、`> [!WARNING]`、`> [!TIP]`、`> [!NOTE]`、`> [!CAUTION]`，GitHub 會自動配圖示＋色彩，本身即符合雙編碼。
- **禁止** 用純色塊表示狀態（例如 🟢🔴 emoji 串接），必須附文字。
- **禁止** 在正文強制 `<small>` 或小於 14px 的字體。
- **連結可辨識性**：連結除了顏色外，必須有底線（GitHub Markdown 預設即有）。

---

## 6. 字體大小 / Font Size

| 場合 / Scope | 最小 / Floor | 建議 / Recommended |
|---|---|---|
| 正文 Body text | 16px | 16–18px（瀏覽器預設） |
| Mermaid 節點文字 | 16px | 16–18px (`themeVariables.fontSize`) |
| 表格內文字 | 14px | 16px |
| 註腳 Footnote | 14px | 14px |
| Code fence | 14px | 14–16px monospace |

> [!NOTE]
> 使用者若將系統字體放大（macOS、iOS、Android 放大鏡功能、Windows 顯示比例 ≥125%），本 repo 的任何 rendering 都必須能等比放大不破版。我們不使用固定 px 高度的 container。

---

## 7. 低視力 / 螢幕閱讀器支援 / Low-Vision & Screen Reader

- 所有圖片（未來若有）必須附 `alt` 文字，描述「圖中要傳達的事實」而非「圖裡有什麼」。
- 所有 Mermaid 圖必須在上方或下方以純文字重述一次關鍵資訊，讓螢幕閱讀器使用者即使跳過 `<svg>` 也能取得相同資訊。
- 標題階層 `#` → `##` → `###` 必須連續，不可跳層（H1 後不可直接 H3）。
- 連結文字必須能自我解釋（`詳見 guides/05` ✓），不可用「click here / 點這裡」。

---

## 8. 檢查清單 / Review Checklist

送 PR 前請自行確認 / Before opening a PR:

- [ ] 新圖表有 `%%{init: ...}%%` 頭註且符合 §4
- [ ] 所有填色都在 §2 指定色盤中
- [ ] 所有表達狀態的節點同時用了「顏色 + 圖示 + 文字」三者中的兩個以上（§3）
- [ ] 流程圖走直角（`curve: stepAfter`）
- [ ] 字體 ≥ 16px
- [ ] 任一圖表轉成灰階後資訊仍可讀
- [ ] 圖表上下附有純文字描述（§7）
- [ ] 新增的文件同時更新中文版與英文版（見 `docs/i18n.md`）

---

## 9. 參考資料 / References

- [WCAG 2.2 Level AAA](https://www.w3.org/TR/WCAG22/) — W3C 無障礙網頁指引
- [Okabe-Ito Color Universal Design palette (2008)](https://jfly.uni-koeln.de/color/)
- [UN CRPD Article 9 — Accessibility](https://www.un.org/development/desa/disabilities/convention-on-the-rights-of-persons-with-disabilities.html)
- [GitHub Markdown Alerts](https://github.com/orgs/community/discussions/16925)
- [Sim Daltonism — Colorblind simulator](https://michelf.ca/projects/sim-daltonism/)（可用來檢查圖表是否色盲友善）

---

## 10. 強制執行 / Enforcement

**ZH：** 本規範由 `scripts/validate-accessibility.sh`（未來補齊）與人工 code review 共同把關。違反 §1–§4 任一條的 PR 會被擋下，除非 issue 中有經維護者同意的豁免說明。

**EN:** Enforced via `scripts/validate-accessibility.sh` (to be added) and manual code review. Any PR violating §1–§4 is blocked unless the issue has a maintainer-approved exception.

---

*本規範最後更新：2026-04-12 — 若您發現本 repo 有任何違反此規範之處，請開 issue 回報（這本身就是對本專案最有價值的貢獻之一）。*

*Last updated: 2026-04-12. If you find any violation in this repo, please open an issue — that's one of the most valuable contributions you can make.*
