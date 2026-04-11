# Guide 07 — 正式環境儀表板（唯讀探測模式）

本指南說明正式環境儀表板的建置方式。與測試環境儀表板（`guides/06-test-dashboard.md`）不同，正式環境儀表板**嚴禁**執行任何會產生實際訂單資料的操作。

## 為何不可使用 create_order

`create_order` 執行成功後，會於歐買尬商家後台產生一筆實際的未付款訂單。若將此方法作為定期健康檢查，將持續累積無效訂單資料，造成下列問題：

1. **對帳污染**：後台訂單列表充斥大量未付款探測訂單，人工對帳時難以區分
2. **統計失真**：訂單總數、轉換率、棄單率等指標均受影響
3. **商家關係**：大量未付款訂單可能觸發歐買尬的風險警示
4. **無效清理**：無法批次刪除已建立的訂單，僅能由商家客服協助

因此正式環境健康檢查必須採用唯讀方法。

## 唯讀探測方法

以下四項方法可於不產生任何訂單資料的前提下，驗證金流網關與整合服務的健康狀態。

### 1. TCP Handshake

對 `{{OMG_API_HOST_PROD}}` 的 443 port 建立 TCP 連線並立即關閉，驗證網路層可達性與 TLS 憑證有效性。

```python
import socket
import ssl

def probe_tcp(host: str, port: int = 443, timeout: float = 3.0) -> tuple[bool, int]:
    """
    回傳 (是否成功, 延遲毫秒)。
    """
    import time
    t0 = time.time()
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                _ = ssock.version()
        return True, int((time.time() - t0) * 1000)
    except Exception:
        return False, int((time.time() - t0) * 1000)
```

### 2. query_order 以假交易號查詢

發送 `query_order` 請求，但使用一組隨機產生的假交易號（例如 `PROBE{uuid}`）。預期網關回應「查無此筆交易」，此回應代表網關服務正常運作且金鑰有效。

```python
import uuid
import time

async def probe_query_order(http_client, host: str, merchant_id: str, hash_key: str, hash_iv: str):
    fake_no = f"PROBE{uuid.uuid4().hex[:10].upper()}"
    params = {
        "MerchantID": merchant_id,
        "MerchantTradeNo": fake_no,
        "TimeStamp": str(int(time.time())),
        "PlatformID": "",
    }
    params["CheckMacValue"] = compute_check_mac(params, hash_key, hash_iv)
    url = f"{host.rstrip('/')}/Cashier/QueryTradeInfo/V5"
    t0 = time.time()
    try:
        resp = await http_client.post(url, data=params, timeout=10.0)
        latency_ms = int((time.time() - t0) * 1000)
        # 查無此筆回應通常為 "10200047 Trade not found" 或類似訊息
        body = resp.text
        is_expected = ("查無" in body) or ("not found" in body.lower()) or ("10200047" in body)
        return is_expected, latency_ms, body[:200]
    except Exception as e:
        return False, int((time.time() - t0) * 1000), str(e)
```

### 3. Refund 簽名自我驗證

使用假訂單號建立退款 payload 並計算 CheckMacValue，但**不發送 HTTP 請求**。此方法驗證退款簽名路徑使用的金鑰與演算法是否可正常運作。

```python
def probe_refund_sign(merchant_id: str, hash_key: str, hash_iv: str) -> tuple[bool, str]:
    params = {
        "MerchantID": merchant_id,
        "MerchantTradeNo": "FAKEPROBE",
        "TradeNo": "",
        "Action": "R",
        "TotalAmount": "1",
    }
    try:
        mac = compute_check_mac(params, hash_key, hash_iv)
        return True, mac
    except Exception as e:
        return False, str(e)
```

### 4. Webhook MAC 自我驗證

建構一組已知的假 callback payload，計算其 CheckMacValue，再使用 webhook 接收器的 MAC 驗證函式進行驗證，確認驗證路徑可正常運作。

```python
def probe_webhook_mac(merchant_id: str, hash_key: str, hash_iv: str) -> bool:
    payload = {
        "MerchantID": merchant_id,
        "MerchantTradeNo": "SELFPROBE",
        "TradeNo": "SELFPROBE",
        "RtnCode": "1",
        "TradeAmt": "1",
        "PaymentDate": "2026/01/01 00:00:00",
    }
    payload["CheckMacValue"] = compute_check_mac(payload, hash_key, hash_iv)
    # 使用實際的 webhook verify 函式
    return verify_check_mac(payload, hash_key, hash_iv)[0]
```

## 儀表板呈現

正式環境儀表板應針對每一個啟用中的金流供應商顯示：

- **整體狀態燈**：綠（4 項探測全部成功）、黃（1-2 項失敗）、紅（3 項以上失敗）
- **24 小時 uptime 百分比**：以整體成功率計算
- **24 小時探測次數**：成功數 / 總數
- **24 小時 by_method 拆解**：TCP / query_order / refund_sign / webhook_mac 四項各自的成功率
- **最新探測時間**：相對時間顯示（例：「3 分鐘前」）
- **最後錯誤訊息**：若最新探測失敗，顯示錯誤內容

## 建議執行頻率

- **每小時**：一次完整探測（四項全部執行）
- **每 5 分鐘**（選用）：僅執行 TCP handshake，用以快速偵測網路中斷

建議以 cron 或背景 worker 執行，並將結果寫入 `health_log` 表供儀表板查詢。

## Database Schema 建議

```sql
CREATE TABLE IF NOT EXISTS health_log (
    id           BIGSERIAL PRIMARY KEY,
    provider     VARCHAR(20) NOT NULL,
    probe_method VARCHAR(30) NOT NULL,   -- tcp | query_order | refund_sign | webhook_mac | overall
    is_healthy   BOOLEAN NOT NULL,
    latency_ms   INTEGER,
    error_text   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_health_log_provider_created
    ON health_log (provider, created_at DESC);
```

查詢 24 小時整體 uptime：

```sql
SELECT
    provider,
    ROUND(100.0 * SUM(CASE WHEN is_healthy THEN 1 ELSE 0 END) / COUNT(*), 2) AS uptime_24h,
    COUNT(*) AS total_probes,
    AVG(latency_ms) AS avg_latency_ms,
    MAX(latency_ms) AS max_latency_ms
FROM health_log
WHERE probe_method = 'overall'
  AND created_at >= now() - INTERVAL '24 hours'
GROUP BY provider;
```

## 告警機制

當整體 24 小時 uptime 低於 95%、或連續 3 次探測失敗時，應透過 Telegram / Discord bot 推送告警訊息。告警訊息應包含：

- 觸發條件（uptime 低於閾值 / 連續失敗次數）
- 最新探測時間與錯誤訊息
- 受影響的探測方法（哪些是 TCP 失敗、哪些是 query_order 失敗）

告警推送程式碼範例：

```python
async def alert_if_degraded(bot, provider: str, uptime: float, recent_errors: list[str]):
    if uptime < 95.0 or len(recent_errors) >= 3:
        text = (
            f"⚠️ 金流健康告警\n"
            f"供應商：{provider}\n"
            f"24h uptime：{uptime}%\n"
            f"最近錯誤：{recent_errors[-1] if recent_errors else '無'}"
        )
        await bot.broadcast(text)
```

## 安全提醒

1. 正式環境探測使用之 HashKey 與 HashIV 僅可寫入 `.env`，不得寫入 repo
2. 探測函式必須通過單元測試驗證，確保不會意外呼叫到 `create_order` endpoint
3. 儀表板 URL 應加上 admin 認證保護，不得公開存取
4. health_log 表建議每 30 天清理一次舊資料，避免無限成長
