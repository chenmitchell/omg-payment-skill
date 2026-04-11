# test-vectors — CheckMacValue 測試向量

本資料夾存放 CheckMacValue 演算法之測試向量與驗證腳本。任何 CheckMacValue 實作調整（無論 Python、Node.js、PHP、C# 或其他語言）均必須通過本資料夾之向量。

> [!NOTE]
> 本向量為社群維護，不代表官方標準。若與官方文件不一致，請以 <https://github.com/omgtwhub/> 與歐買尬商家後台公告為準。

---

## 檔案清單

| 檔案 | 用途 |
|---|---|
| `check-mac-value.json` | SSOT 測試向量（HashKey、HashIV、params、expected MAC） |
| `verify.py` | Python 驗證腳本（使用 stdlib，無第三方相依） |
| `verify-node.js` | Node.js 驗證腳本（使用 built-in `crypto`） |

---

## 執行方式

### Python

```bash
python3 test-vectors/verify.py
```

預期輸出：

```
[OK]   V1 — 標準信用卡 create_order payload
[OK]   V2 — 最小欄位集
[OK]   V3 — 含 .NET 特殊字元的 ItemName

結果：3/3 通過
```

### Node.js

```bash
node test-vectors/verify-node.js
```

預期輸出與 Python 版本相同。

### CI 建議

於 GitHub Actions 中加入下列 job 以確保演算法穩定性：

```yaml
name: check-mac-value
on: [push, pull_request]
jobs:
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python3 test-vectors/verify.py
  node:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: node test-vectors/verify-node.js
```

---

## 測試向量涵蓋範圍

| ID | 情境 | 重點驗證 |
|---|---|---|
| V1 | 標準信用卡 create_order | 日期時間、URL、一般 ASCII 欄位 |
| V2 | 最小欄位集 | 短字串、最簡組合 |
| V3 | 含 `.NET` 特殊字元 | `( ) * _ . - !` 等需還原之字元 |

日後若需新增向量（例如中文 ItemName、ATM/CVS 特殊欄位、recurring period 參數），請：

1. 於 `check-mac-value.json` 之 `vectors` 陣列增加一筆
2. 使用 `verify.py` 本地執行取得 expected MAC 後寫入
3. 確認 `verify-node.js` 亦能產出相同結果
4. 更新 `references/check-mac-value.md` 中之相關說明

---

## 多語言參考實作

下列為在其他語言中實作 CheckMacValue 時的對應做法：

### PHP

```php
function dotnet_url_encode(string $s): string {
    $encoded = strtolower(urlencode($s));
    $replacements = [
        '%2d' => '-', '%5f' => '_', '%2e' => '.',
        '%21' => '!', '%2a' => '*', '%28' => '(', '%29' => ')',
    ];
    return strtr($encoded, $replacements);
}

function compute_check_mac(array $params, string $hashKey, string $hashIv): string {
    unset($params['CheckMacValue']);
    ksort($params);
    $pairs = [];
    foreach ($params as $k => $v) { $pairs[] = "$k=$v"; }
    $raw = "HashKey=$hashKey&" . implode('&', $pairs) . "&HashIV=$hashIv";
    return strtoupper(hash('sha256', dotnet_url_encode($raw)));
}
```

### C# / .NET

使用 `HttpUtility.UrlEncode`（`System.Web`），這是歐買尬演算法的原生平台，無需字元還原。

```csharp
using System.Security.Cryptography;
using System.Text;
using System.Web;

public static string ComputeCheckMac(
    IDictionary<string, string> parameters,
    string hashKey,
    string hashIv)
{
    var filtered = parameters
        .Where(kv => kv.Key != "CheckMacValue")
        .OrderBy(kv => kv.Key, StringComparer.Ordinal);
    var pairs = string.Join("&", filtered.Select(kv => $"{kv.Key}={kv.Value}"));
    var raw = $"HashKey={hashKey}&{pairs}&HashIV={hashIv}";
    var encoded = HttpUtility.UrlEncode(raw).ToLower();
    using var sha256 = SHA256.Create();
    var bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(encoded));
    return Convert.ToHexString(bytes);
}
```

無論使用何種語言，最終產出之 MAC 均應通過 `check-mac-value.json` 中之所有向量。
