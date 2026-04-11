#!/usr/bin/env python3
"""test-vectors/verify.py — CheckMacValue 實作驗證腳本（Python 版）

本腳本讀取 test-vectors/check-mac-value.json 並驗證 references/check-mac-value.md
所述之演算法實作是否能產出與 JSON 中相同之 MAC。

用法：
    python3 test-vectors/verify.py

退出碼：
    0 — 全部通過
    1 — 至少一項失敗

本腳本不依賴任何第三方套件。
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.parse
from pathlib import Path


def _dotnet_url_encode(s: str) -> str:
    """仿 .NET URL encoding 規則。

    Python `urllib.parse.quote_plus` 會將 `-`, `_`, `.`, `!`, `*`, `(`, `)`
    等字元保留或轉為 %XX，.NET 之行為有所不同。必須手動還原。
    """
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


def compute_check_mac(params: dict, hash_key: str, hash_iv: str) -> str:
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue"}
    sorted_items = sorted(filtered.items(), key=lambda kv: kv[0])
    pairs = [f"{k}={v}" for k, v in sorted_items]
    raw = f"HashKey={hash_key}&" + "&".join(pairs) + f"&HashIV={hash_iv}"
    encoded = _dotnet_url_encode(raw)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()


def main() -> int:
    vectors_path = Path(__file__).parent / "check-mac-value.json"
    if not vectors_path.exists():
        print(f"找不到測試向量檔：{vectors_path}", file=sys.stderr)
        return 1

    data = json.loads(vectors_path.read_text(encoding="utf-8"))
    hash_key = data["hash_key"]
    hash_iv = data["hash_iv"]
    vectors = data["vectors"]

    total = len(vectors)
    passed = 0
    failed = []

    for vec in vectors:
        name = vec["name"]
        expected = vec["expected_mac"].upper()
        actual = compute_check_mac(vec["params"], hash_key, hash_iv)
        if actual == expected:
            print(f"[OK]   {name}")
            passed += 1
        else:
            print(f"[FAIL] {name}")
            print(f"       expected: {expected}")
            print(f"       actual:   {actual}")
            failed.append(name)

    print()
    print(f"結果：{passed}/{total} 通過")

    if failed:
        print("失敗項目：")
        for name in failed:
            print(f"  - {name}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
