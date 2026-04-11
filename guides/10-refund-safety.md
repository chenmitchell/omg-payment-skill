# Guide 10 — 退款安全機制

本指南說明退款操作的安全設計原則。核心理念為：**退款屬於合法業務行為，安全機制應以「警示與二次確認」取代「阻擋」**。

## 設計原則

1. **永遠允許執行**：退款不因金額較大、頻率較高或超過建議上限而被阻擋。上限的作用在於讓操作者停下來思考，而非阻止合法退款。
2. **強制二次確認**：所有退款必須經過顯式的二次確認步驟，避免誤觸。
3. **超過上限時強化提醒**：當退款超過任一建議上限時，確認對話框應顯示警示訊息，且確認按鈕文字應變更為「確認退款 NTD X（超過上限）」以提高注意力。
4. **完整稽核紀錄**：所有退款（尤其是超過上限的）必須寫入 audit log。
5. **冪等性保護**：退款 endpoint 本身必須實作冪等性，避免同一筆退款被重複執行（例如網路重試造成）。

## 三項建議上限

建議上限應定義於環境變數，便於不同規模商家調整：

```bash
REFUND_MAX_PER_ORDER=50000       # 單筆退款建議上限（TWD）
REFUND_DAILY_QUOTA=100000        # 每日退款總金額建議上限（TWD）
REFUND_DAILY_COUNT_CAP=20        # 每日退款次數建議上限
```

預設值的推導依據：

| 項目 | 預設值 | 適用規模 |
|---|---|---|
| 單筆上限 | NTD 50,000 | 適合客單價低於 NTD 10,000 的零售與課程類商家 |
| 每日總額上限 | NTD 100,000 | 適合月營收低於 NTD 3,000,000 的小型商家 |
| 每日次數上限 | 20 次 | 適合每日訂單數低於 200 的商家 |

大型商家應依實際營運規模向上調整。

## 雙層實作

退款安全機制應於兩處實作，形成雙重保護：

### 第一層：Bot 層（前端提醒）

Bot 於顯示確認對話框前執行檢查，若超過建議上限則於對話框中顯示警示。此層的目的在於**操作體驗**：讓操作者於點擊確認前看到警示，而非在後端回傳錯誤才知道。

範例實作見 `templates/telegram-bot/bot.py` 的 `_refund_warnings()` 函式。

### 第二層：後端層（稽核與限流）

後端 `POST /api/admin/refund` endpoint 於執行退款時，應：

1. 檢查 `Authorization` header 的 admin token
2. 取得該筆訂單的當前狀態，確認為 `paid`
3. 計算當日已退款累計金額與次數
4. 執行退款操作（呼叫金流網關 refund API）
5. 寫入 `refund_audit_log` 表，包含操作者、金額、是否超過建議上限、執行時間等欄位

後端不得依據「超過上限」而拒絕執行，僅記錄該事實。

## 後端 Schema

```sql
CREATE TABLE IF NOT EXISTS refund_audit_log (
    id              BIGSERIAL PRIMARY KEY,
    order_no        VARCHAR(40) NOT NULL,
    amount          INTEGER NOT NULL,
    exceeded_single BOOLEAN NOT NULL DEFAULT FALSE,
    exceeded_daily  BOOLEAN NOT NULL DEFAULT FALSE,
    exceeded_count  BOOLEAN NOT NULL DEFAULT FALSE,
    operator        VARCHAR(100),       -- 例：tg_chat_id=123456 / admin_panel / api_token
    provider_resp   TEXT,                -- 金流網關回應
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_refund_audit_created ON refund_audit_log (created_at DESC);
CREATE INDEX idx_refund_audit_exceeded ON refund_audit_log (created_at DESC)
    WHERE exceeded_single OR exceeded_daily OR exceeded_count;
```

超過建議上限的退款可透過下列查詢檢視：

```sql
SELECT
    created_at,
    order_no,
    amount,
    operator,
    CASE
        WHEN exceeded_single THEN 'single'
        WHEN exceeded_daily THEN 'daily'
        WHEN exceeded_count THEN 'count'
    END AS reason
FROM refund_audit_log
WHERE (exceeded_single OR exceeded_daily OR exceeded_count)
  AND created_at >= now() - INTERVAL '30 days'
ORDER BY created_at DESC;
```

## 退款 Endpoint 冪等性

退款 endpoint 同樣需實作冪等性，避免重複扣款。建議實作方式：

1. 請求 body 包含 `idempotency_key`（可由呼叫端產生，例如 `refund-{order_no}-{timestamp}`）
2. 若同一 `idempotency_key` 已存在於 `refund_audit_log`，直接回傳先前結果
3. 寫入 `refund_audit_log` 時 `idempotency_key` 欄位加 unique index

此機制可防止網路重試造成同一筆訂單被退款多次。

## 稽核報表

建議每月產出退款報表，內容包含：

- 當月退款總筆數、總金額
- 當月超過建議上限之退款清單（時間、訂單號、金額、操作者、原因）
- 退款金額佔當月收款總額之比例
- 退款率趨勢（對比前三個月）

此報表可自動產出並透過 Email 或 Telegram 推送至商家管理者。

## 定期檢視建議上限

建議商家每 3 個月檢視一次 `REFUND_*` 環境變數，依據實際退款歷史調整。若長期大量退款觸發「超過上限」警示，表示上限設定過低應上調；若長期無警示但偶有異常高額退款，表示上限設定過高應下調。

## 安全提醒

1. 退款 endpoint 必須位於 admin 驗證之下，不得開放未驗證存取
2. Admin token 若外流，應立即輪換並檢視近期退款紀錄
3. 建議於正式環境啟用退款總額即時監控，單日退款超過日營收 10% 時主動告警
4. 退款稽核 log 應保留至少 6 個月，便於爭議處理
