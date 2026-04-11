# Reference R2 — CheckMacValue 演算法

本文件定義歐買尬 CheckMacValue 之計算規則與驗證方式。所有與歐買尬 API 的互動均需依此規則產生或驗證 MAC。

## 演算法

1. **取得 HashKey 與 HashIV**：由歐買尬商家後台「開發者設定」取得，正式與測試環境不同
2. **移除 CheckMacValue 欄位**：計算 MAC 前將 payload 中之 `CheckMacValue` 欄位移除
3. **字典序排序**：將剩餘欄位依 key 的字典序（ASCII）排序
4. **串接字串**：格式為 `HashKey={HashKey}&K1=V1&K2=V2&...&HashIV={HashIV}`
5. **URL encoding**：對整串字串執行 URL encoding（使用 `.NET` 版本之 encoding，對應 Python 之 `urllib.parse.quote_plus` 並將部分字元還原）
6. **小寫化**：將 URL encoded 字串轉為小寫
7. **SHA256 雜湊**：對小寫字串計算 SHA256
8. **轉大寫 hex**：結果為 64 字元之大寫十六進位字串

## .NET 字元還原對照

歐買尬使用的 URL encoding 與 Python 預設不同，需將下列字元還原為原字元：

| URL encoded | 還原為 |
|---|---|
| `%2D` | `-` |
| `%5F` | `_` |
| `%2E` | `.` |
| `%21` | `!` |
| `%2A` | `*` |
| `%28` | `(` |
| `%29` | `)` |

## Python 實作

```python
import hashlib
import urllib.parse


def _dotnet_url_encode(s: str) -> str:
    """仿 .NET URL encoding 規則。"""
    encoded = urllib.parse.quote_plus(s)
    replacements = {
        "%2d": "-",
        "%5f": "_",
        "%2e": ".",
        "%21": "!",
        "%2a": "*",
        "%28": "(",
        "%29": ")",
    }
    lower = encoded.lower()
    for k, v in replacements.items():
        lower = lower.replace(k, v)
    return lower


def compute_check_mac(
    params: dict,
    hash_key: str,
    hash_iv: str,
) -> str:
    """計算歐買尬 CheckMacValue。

    Args:
        params: 交易參數（不含 CheckMacValue）
        hash_key: 商家 HashKey
        hash_iv:  商家 HashIV

    Returns:
        64 字元大寫十六進位字串
    """
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue"}
    sorted_items = sorted(filtered.items(), key=lambda kv: kv[0])

    pairs = [f"{k}={v}" for k, v in sorted_items]
    raw = f"HashKey={hash_key}&" + "&".join(pairs) + f"&HashIV={hash_iv}"

    encoded = _dotnet_url_encode(raw)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return digest.upper()


def verify_check_mac(
    params: dict,
    hash_key: str,
    hash_iv: str,
) -> tuple[bool, str]:
    """驗證 CheckMacValue。

    Returns:
        (是否符合, 期望的 MAC)
    """
    received = params.get("CheckMacValue", "")
    expected = compute_check_mac(params, hash_key, hash_iv)
    return received.upper() == expected, expected
```

## 測試向量

下列為固定之測試向量，可用於驗證實作是否正確。實際數值僅作參考用途，不代表任何真實訂單。

```python
TEST_HASH_KEY = "TESTKEY1234567890"
TEST_HASH_IV  = "TESTIV1234567890"

TEST_PARAMS = {
    "MerchantID":       "1000031",
    "MerchantTradeNo":  "TEST20260412001",
    "MerchantTradeDate":"2026/04/12 10:00:00",
    "PaymentType":      "aio",
    "TotalAmount":      "100",
    "TradeDesc":        "test",
    "ItemName":         "testitem",
    "ReturnURL":        "https://example.com/webhook",
    "ChoosePayment":    "Credit",
}
```

測試向量之期望 MAC 應由實作產出後寫入 `test-vectors/check-mac-value.json`，日後任何實作調整均需通過該檔案之 assertion。

## 常見錯誤

**錯誤 1：未執行字典序排序**

若以 Python dict 插入順序直接串接，會得到不同結果。請確保使用 `sorted()`。

**錯誤 2：使用 Python 預設之 urlencode**

Python `urllib.parse.urlencode` 與 `.NET` encoding 規則不同。必須手動還原上述 7 個字元。

**錯誤 3：未小寫化再雜湊**

雖然字面上只差大小寫，但 SHA256 結果完全不同。切勿省略。

**錯誤 4：金額以浮點數送出**

若 payload 中 `TotalAmount` 送出為 `100.00`，將與歐買尬預期之 `100` 不符，導致 MAC 不相等。所有數值欄位應以字串型態處理。

**錯誤 5：中文未先編碼就放入 payload**

中文商品名稱應於放入 `params` 前以 `urllib.parse.quote` 編碼，避免字元被雜湊前後處理得不一致。

## 效能考量

CheckMacValue 為 SHA256 演算法，於一般伺服器可達每秒百萬次運算，不需快取。然而若 webhook 流量極高，建議：

1. 將 `_dotnet_url_encode` 之替換表建立為 module-level constant
2. 避免在 hot path 中重新 import `hashlib`
3. 若 payload 欄位數固定，可考慮使用 `__slots__` 或 dataclass 減少 dict 開銷

## 單元測試建議

```python
def test_compute_check_mac_stable():
    """同一組 params 計算兩次應得到相同結果。"""
    mac1 = compute_check_mac(TEST_PARAMS, TEST_HASH_KEY, TEST_HASH_IV)
    mac2 = compute_check_mac(TEST_PARAMS, TEST_HASH_KEY, TEST_HASH_IV)
    assert mac1 == mac2
    assert len(mac1) == 64
    assert mac1 == mac1.upper()


def test_compute_check_mac_order_independent():
    """欄位順序不同應得到相同 MAC。"""
    p1 = dict(TEST_PARAMS)
    p2 = dict(reversed(list(TEST_PARAMS.items())))
    assert compute_check_mac(p1, TEST_HASH_KEY, TEST_HASH_IV) == \
           compute_check_mac(p2, TEST_HASH_KEY, TEST_HASH_IV)


def test_verify_check_mac_roundtrip():
    """計算後驗證應通過。"""
    params = dict(TEST_PARAMS)
    params["CheckMacValue"] = compute_check_mac(params, TEST_HASH_KEY, TEST_HASH_IV)
    ok, _ = verify_check_mac(params, TEST_HASH_KEY, TEST_HASH_IV)
    assert ok


def test_verify_check_mac_rejects_tampered():
    """修改任一欄位後驗證應失敗。"""
    params = dict(TEST_PARAMS)
    params["CheckMacValue"] = compute_check_mac(params, TEST_HASH_KEY, TEST_HASH_IV)
    params["TotalAmount"] = "999"
    ok, _ = verify_check_mac(params, TEST_HASH_KEY, TEST_HASH_IV)
    assert not ok
```

這四項測試應納入 CI 以確保 MAC 計算之穩定性。
