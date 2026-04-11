# Guide 05 — Race-safe Webhook 冪等性

本指南為 OMG Payment Skill 最核心的技術章節。所有金流網關均可能因網路延遲、伺服器重啟、下游服務 timeout 等原因重送 webhook，若接收端未實作冪等性處理，將導致同一筆交易被重複寫入、訂單狀態被多次覆蓋、或退款事件被重複執行。

## 常見錯誤情境

1. **服務重啟延遲**：服務短暫無法回應，網關判定為失敗而重送。若接收端未實作冪等性，同一筆付款會被寫入資料庫多次。
2. **並行 race condition**：兩個 webhook request 並行進入 handler，若採用「SELECT + UPDATE」而未加 row lock，兩個 request 會同時讀到 `pending` 狀態，並同時將其更新為 `paid`，導致 transactions 表產生重複紀錄。
3. **退款重送**：退款 webhook 亦可能重送。若 refund handler 將重送當作新退款處理，將導致同一筆交易被多次退款。

## 核心原則

1. 每個 webhook 必須產生穩定的 `idempotency_key`，由 payload 中的固定欄位組合而成，不得使用隨機值
2. 資料庫 schema 中 `idempotency_key` 欄位必須建立 unique index
3. 所有資料庫寫入操作必須於單一 transaction 內完成，並使用 `SELECT ... FOR UPDATE` 鎖定訂單 row
4. 早期重複檢查：進入 transaction 後立即查詢 `idempotency_key` 是否已存在，若存在則直接回傳成功
5. 晚期重複吸收：鎖定 row 後若發現訂單狀態已為 `paid`、`refunded` 或 `partial_refunded`，應記錄為 absorbed 並回傳成功
6. `rowcount = 0` 吸收：UPDATE 之 `WHERE status = 'pending'` 若回傳 rowcount 為 0，代表該 row 已被其他 request 變更，應記錄為 absorbed 並回傳成功，不得回傳錯誤
7. 所有 INSERT 必須帶 `idempotency_key`
8. 除非為金額不符（amount mismatch）等明確錯誤，否則一律回傳 200 OK，避免網關無限重送

---

## 冪等性鍵（idempotency_key）怎麼算

從 payload 挑**穩定欄位**組合：
- 對 OMG / ECPay：`MerchantTradeNo`、`TradeNo`、`RtnCode`、`TradeAmt`、`PaymentDate`
- 對其他網關：挑「只要是同一次交易，每次重送都會一樣」的欄位

組合後用 `&` 連起來，前面加 provider prefix（例：`omg:MerchantTradeNo=ABC&TradeNo=...`）。

**過長 fallback**：如果組合字串 > 110 chars，用 SHA256 hash 頭 40 碼。
**缺欄位 fallback**：如果關鍵欄位都拿不到，用整個 payload 的 canonical JSON SHA256 前 32 碼 + `hash:` prefix。

### Python 參考實作

```python
import hashlib
import json
from typing import Any

def compute_idempotency_key(provider: str, payload: dict[str, Any]) -> str:
    """
    從 payload 固定欄位組出穩定的 idempotency key。
    
    相同的重送一定會產生相同的 key；不同的交易一定會產生不同的 key。
    """
    key_parts: list[str] = []
    
    if provider in ("omg", "ecpay"):
        fields = ("MerchantTradeNo", "TradeNo", "RtnCode", "TradeAmt", "PaymentDate")
    elif provider == "linepay":
        fields = ("orderId", "transactionId", "amount", "status")
    else:
        fields = ()
    
    for f in fields:
        v = payload.get(f)
        if v is not None and v != "":
            key_parts.append(f"{f}={v}")
    
    # 缺欄位 fallback → hash 整個 payload
    if not key_parts:
        canonical = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
        h = hashlib.sha256(canonical.encode("utf-8", errors="replace")).hexdigest()
        return f"{provider}:hash:{h[:32]}"
    
    body = "&".join(key_parts)
    
    # 過長 fallback → 前綴 + hash
    if len(body) > 110:
        h = hashlib.sha256(body.encode("utf-8")).hexdigest()
        return f"{provider}:long:{h[:40]}"
    
    return f"{provider}:{body}"
```

---

## DB schema（PostgreSQL 範例）

```sql
-- 訂單主表（你的專案應該有類似的表）
CREATE TABLE IF NOT EXISTS orders (
    id              BIGSERIAL PRIMARY KEY,
    order_no        VARCHAR(40) NOT NULL UNIQUE,
    provider        VARCHAR(20) NOT NULL,
    amount          INTEGER NOT NULL,   -- 以最小貨幣單位（元）整數存
    currency        CHAR(3)  NOT NULL DEFAULT 'TWD',
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending | paid | refunded | partial_refunded | failed
    paid_at         TIMESTAMPTZ,
    provider_trade_no VARCHAR(40),
    user_id         BIGINT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 所有 webhook / 呼叫的紀錄表（含冪等 key）
CREATE TABLE IF NOT EXISTS payment_transactions (
    id              BIGSERIAL PRIMARY KEY,
    order_id        BIGINT NOT NULL REFERENCES orders(id),
    trx_type        VARCHAR(20) NOT NULL,   -- callback | query | refund | absorbed | rejected
    provider        VARCHAR(20) NOT NULL,
    amount          INTEGER,
    raw_payload     JSONB,
    idempotency_key VARCHAR(128),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 關鍵：冪等 key + trx_type 的 unique index
-- 這是 race-safe 的最後一道防線
CREATE UNIQUE INDEX IF NOT EXISTS uniq_payment_trx_idem
    ON payment_transactions (idempotency_key, trx_type)
    WHERE idempotency_key IS NOT NULL;
```

---

## Race-safe handler 完整流程（8 個 step）

```python
from fastapi import APIRouter, Request, HTTPException
import psycopg2
import psycopg2.extras

router = APIRouter()

def get_conn():
    # 回傳你的 DB 連線，略
    ...

@router.post("/webhook/{provider}")
async def handle_webhook(provider: str, request: Request):
    # 1. Parse payload（純 parse，不碰 DB）
    form = await request.form()
    payload = dict(form)
    
    # 2. 算冪等 key（純函式，不碰 DB）
    idem_key = compute_idempotency_key(provider, payload)
    
    # 3. 驗 MAC（純函式，不碰 DB）
    if not verify_mac(provider, payload):
        # MAC 錯不要寫 DB，直接回 400 — 這是明確的攻擊 / 錯送
        raise HTTPException(400, "invalid mac")
    
    order_no = payload.get("MerchantTradeNo")
    amount = int(payload.get("TradeAmt", 0))
    rtn_code = str(payload.get("RtnCode", ""))
    trade_no = payload.get("TradeNo")
    new_status = "paid" if rtn_code == "1" else "failed"
    
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # 3a. 早期重複檢查（hit unique index 直接結束）
            cur.execute(
                """SELECT id FROM payment_transactions
                   WHERE idempotency_key = %s AND trx_type = 'callback'
                   LIMIT 1""",
                (idem_key,),
            )
            if cur.fetchone():
                conn.rollback()
                return {"ok": True, "note": "early-dup"}
            
            # 3b. 鎖住 order row（這一步是整個 pattern 的核心）
            cur.execute(
                """SELECT id, status, amount FROM orders
                   WHERE order_no = %s
                   FOR UPDATE""",
                (order_no,),
            )
            row = cur.fetchone()
            if not row:
                conn.rollback()
                # 找不到訂單 —— 不要回 404，回 200 避免對方無限重送
                # 但寫一筆 rejected transaction 供事後稽核
                return {"ok": True, "note": "order-not-found"}
            
            order_id = row["id"]
            current_status = row["status"]
            expected_amount = row["amount"]
            
            # 3c. 金額對不上 → 記錄 + 回 rejected
            if amount != expected_amount:
                cur.execute(
                    """INSERT INTO payment_transactions
                       (order_id, trx_type, provider, amount, raw_payload, idempotency_key)
                       VALUES (%s, 'rejected', %s, %s, %s, %s)""",
                    (order_id, provider, amount, psycopg2.extras.Json(payload), idem_key),
                )
                conn.commit()
                raise HTTPException(400, "amount mismatch")
            
            # 3d. 晚期重複吸收（已經 paid / refunded 了）
            if current_status in ("paid", "refunded", "partial_refunded"):
                cur.execute(
                    """INSERT INTO payment_transactions
                       (order_id, trx_type, provider, amount, raw_payload, idempotency_key)
                       VALUES (%s, 'absorbed', %s, %s, %s, %s)""",
                    (order_id, provider, amount, psycopg2.extras.Json(payload), idem_key),
                )
                conn.commit()
                return {"ok": True, "note": "late-dup"}
            
            # 3e. UPDATE with optimistic concurrency
            if new_status == "paid":
                cur.execute(
                    """UPDATE orders
                       SET status = 'paid', paid_at = now(),
                           provider_trade_no = %s, updated_at = now()
                       WHERE id = %s AND status = 'pending'""",
                    (trade_no, order_id),
                )
            else:
                cur.execute(
                    """UPDATE orders
                       SET status = %s, updated_at = now()
                       WHERE id = %s AND status = 'pending'""",
                    (new_status, order_id),
                )
            
            # 3f. rowcount = 0 吸收（race 被別的 request 搶先改掉）
            if cur.rowcount == 0:
                cur.execute(
                    """INSERT INTO payment_transactions
                       (order_id, trx_type, provider, amount, raw_payload, idempotency_key)
                       VALUES (%s, 'absorbed', %s, %s, %s, %s)""",
                    (order_id, provider, amount, psycopg2.extras.Json(payload), idem_key),
                )
                conn.commit()
                return {"ok": True, "note": "rowcount-zero-absorbed"}
            
            # 3g. 成功 INSERT callback transaction
            cur.execute(
                """INSERT INTO payment_transactions
                   (order_id, trx_type, provider, amount, raw_payload, idempotency_key)
                   VALUES (%s, 'callback', %s, %s, %s, %s)""",
                (order_id, provider, amount, psycopg2.extras.Json(payload), idem_key),
            )
            
            # 3h. commit
            conn.commit()
        
        return {"ok": True, "note": "new"}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

---

## 為什麼每一步都不能省

| Step | 不做會怎樣 |
|---|---|
| 3a 早期重複檢查 | 重送會走到 3b–3g 白白鎖 row，高併發下會壓垮 DB |
| 3b `FOR UPDATE` | 兩個並行 request 都會讀到 pending，兩邊都 update 成 paid，transactions 多寫一筆 |
| 3c amount mismatch 記錄 | 事後對帳對不起來，稽核找不到蛛絲馬跡 |
| 3d 晚期吸收 | 第 9 秒重送時會走 3e 的 `WHERE status='pending'` 吃 rowcount=0，走到 3f，重複次數++ |
| 3e `WHERE status='pending'` | 沒有這條 optimistic concurrency，重送會把 paid 訂單再改一次 paid（看起來沒事，但 `paid_at` 會跳） |
| 3f rowcount = 0 吸收 | 如果回 400，對方會無限重送到服務掛掉 |
| 3g INSERT with idem_key | 下次重送就走不到 3a 了，會變成永遠重新處理 |
| 3h commit 統一 | 3b–3g 分散在多個 transaction 會破壞 row lock，等於沒鎖 |

---

## 11 組 unit test（一定要跑過才算串完）

把下面這 11 個 test case 寫成 Python unittest 或 pytest，用 mock cursor + mock connection：

```python
import unittest
from unittest.mock import MagicMock, patch

class IdempotencyKeyTests(unittest.TestCase):
    def test_same_payload_same_key(self):
        """相同 payload 必然產生相同 key"""
        p = {"MerchantTradeNo": "A1", "TradeNo": "T1", "RtnCode": "1", "TradeAmt": "500"}
        self.assertEqual(compute_idempotency_key("omg", p), compute_idempotency_key("omg", p))
    
    def test_extra_noise_doesnt_affect_key(self):
        """多一個無關欄位不影響 key"""
        p1 = {"MerchantTradeNo": "A1", "TradeNo": "T1", "RtnCode": "1", "TradeAmt": "500"}
        p2 = {**p1, "ExtraField": "noise"}
        self.assertEqual(compute_idempotency_key("omg", p1), compute_idempotency_key("omg", p2))
    
    def test_different_trade_no_different_key(self):
        p1 = {"MerchantTradeNo": "A1", "TradeNo": "T1", "RtnCode": "1", "TradeAmt": "500"}
        p2 = {"MerchantTradeNo": "A1", "TradeNo": "T2", "RtnCode": "1", "TradeAmt": "500"}
        self.assertNotEqual(compute_idempotency_key("omg", p1), compute_idempotency_key("omg", p2))
    
    def test_provider_prefix(self):
        p = {"MerchantTradeNo": "A1"}
        self.assertTrue(compute_idempotency_key("omg", p).startswith("omg:"))
        self.assertTrue(compute_idempotency_key("ecpay", p).startswith("ecpay:"))
    
    def test_key_length_cap(self):
        p = {"MerchantTradeNo": "X" * 200, "TradeNo": "Y" * 200}
        self.assertLessEqual(len(compute_idempotency_key("omg", p)), 128)
    
    def test_fallback_hash_when_no_fields(self):
        p = {"random_field": "value"}
        k = compute_idempotency_key("unknown", p)
        self.assertIn(":hash:", k)

class HandlerTests(unittest.TestCase):
    def test_first_delivery_happy_path(self):
        """第一次送達 → new"""
        ...
    
    def test_duplicate_early_dup(self):
        """第二次送達，DB 已有 idem_key → early-dup"""
        ...
    
    def test_late_duplicate_absorbed(self):
        """第二次送達，order 已經 paid → late-dup absorbed"""
        ...
    
    def test_amount_mismatch_rejected(self):
        """金額對不上 → 400 + rejected transaction written"""
        ...
    
    def test_rowcount_zero_absorbed(self):
        """race 導致 rowcount=0 → 吸收成 200，不 REJECT"""
        ...
```

---

## 實戰 checklist（部署前）

- [ ] `payment_transactions.idempotency_key` 欄位存在
- [ ] `(idempotency_key, trx_type)` 的 unique index 存在
- [ ] Webhook handler 用單一 DB transaction
- [ ] `SELECT ... FOR UPDATE` 有鎖住 order row
- [ ] 有早期重複檢查（3a）
- [ ] 有晚期重複吸收（3d）
- [ ] 有 rowcount=0 吸收（3f）
- [ ] 所有 INSERT 都帶 idempotency_key
- [ ] MAC 驗證失敗回 400，其他幾乎所有情況回 200
- [ ] 跑過上方 11 組 unit test 全綠
- [ ] 壓測：同一筆 payload 並行送 50 次，結果 DB 只有 1 筆 callback + 49 筆 absorbed/early-dup
