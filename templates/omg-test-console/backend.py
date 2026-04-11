"""
OMG 測試後台 — 獨立 FastAPI backend
=====================================

這支檔案是專門給你「單獨跑起來玩」的測試後台，不依賴任何其他專案。

跑法：
    pip install fastapi uvicorn httpx python-dotenv
    cp .env.example .env      # 填入你的 OMG 測試金鑰
    python backend.py

然後開 http://localhost:8787/ 就會載入 console.html。

提供的 endpoint：
    POST /api/test/full-chain      一鍵跑 create→MAC→POST→query→refund_sign
    POST /api/test/create-order    單測 create_order
    POST /api/test/query-order     單測 query_order
    POST /api/test/refund-sign     單測 refund 簽名（不真的打網關）
    POST /api/test/mac-calculate   貼參數算 CheckMacValue
    POST /api/test/mac-verify      貼 payload + MAC 驗證
    POST /api/test/webhook-simulate 對自己的 /webhook 接收器模擬 N 次重送
    POST /webhook                   收 OMG callback（示範用，完整版見 guides/05）
    GET  /api/test/logs             取得所有 log（JSON）
    GET  /                          載入 console.html

本檔刻意寫得「一支 .py 跑完」，方便 AI 幫使用者複製貼上就能跑。
正式專案應該把各 module 拆分，不要學這份檔案的「全塞一支」風格。
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
import urllib.parse
import uuid
from collections import deque
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse

# ---------- Config ----------

OMG_MERCHANT_ID = os.getenv("OMG_MERCHANT_ID", "1000031")
OMG_HASH_KEY = os.getenv("OMG_HASH_KEY", "")   # 請填入測試 HashKey
OMG_HASH_IV = os.getenv("OMG_HASH_IV", "")     # 請填入測試 HashIV
OMG_API_HOST_STAGE = os.getenv("OMG_API_HOST_STAGE", "")  # 請填入測試 API host
OMG_API_HOST_PROD = os.getenv("OMG_API_HOST_PROD", "")    # 正式環境 host（本檔案不會主動打）

# ---------- In-memory log ring buffer ----------

LOGS: deque[dict[str, Any]] = deque(maxlen=500)

def log(level: str, step: str, data: dict[str, Any] | None = None) -> None:
    entry = {
        "ts": time.time(),
        "level": level,
        "step": step,
        "data": data or {},
    }
    LOGS.append(entry)

# ---------- CheckMacValue (SHA256) ----------

def _url_encode(s: str) -> str:
    # OMG / ECPay 的 URL encode 規則：大寫轉義、部分符號不轉義
    return urllib.parse.quote_plus(str(s), safe="").lower()

def compute_check_mac(params: dict[str, Any], hash_key: str, hash_iv: str) -> str:
    """
    SHA256 版 CheckMacValue。
    流程：
      1. 把 params（去掉 CheckMacValue 本身）按 key 字母排序
      2. 組成 key1=val1&key2=val2&...
      3. 前後加上 HashKey / HashIV → HashKey=xxx&...&HashIV=xxx
      4. URL encode（小寫）
      5. 轉小寫後 .NET style encode 調整（實務上各家細節略有差異，請以官方為準）
      6. SHA256 取 hex 並全轉大寫

    這份實作是「通用示範」，實際要用請對照 OMG 官方的 SHA256 流程檢查一次。
    """
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue" and v not in (None, "")}
    sorted_items = sorted(filtered.items(), key=lambda x: x[0].lower())
    body = "&".join(f"{k}={v}" for k, v in sorted_items)
    raw = f"HashKey={hash_key}&{body}&HashIV={hash_iv}"
    encoded = urllib.parse.quote_plus(raw, safe="").lower()
    # 部分 gateway 會做 .NET encode 對齊（"(" ")" "*" "!" 不轉義）
    for ch_from, ch_to in (("%21", "!"), ("%2a", "*"), ("%28", "("), ("%29", ")")):
        encoded = encoded.replace(ch_from, ch_to)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()

def verify_check_mac(params: dict[str, Any], hash_key: str, hash_iv: str) -> tuple[bool, str, str]:
    """回傳 (是否正確, 使用者提供的 MAC, 我們算出來的 MAC)"""
    received = str(params.get("CheckMacValue", ""))
    expected = compute_check_mac(params, hash_key, hash_iv)
    return received.upper() == expected.upper(), received, expected

# ---------- Idempotency key ----------

def compute_idempotency_key(provider: str, payload: dict[str, Any]) -> str:
    key_parts: list[str] = []
    if provider == "omg":
        for f in ("MerchantTradeNo", "TradeNo", "RtnCode", "TradeAmt", "PaymentDate"):
            v = payload.get(f)
            if v not in (None, ""):
                key_parts.append(f"{f}={v}")
    if not key_parts:
        canonical = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
        h = hashlib.sha256(canonical.encode("utf-8", errors="replace")).hexdigest()
        return f"{provider}:hash:{h[:32]}"
    body = "&".join(key_parts)
    if len(body) > 110:
        h = hashlib.sha256(body.encode("utf-8")).hexdigest()
        return f"{provider}:long:{h[:40]}"
    return f"{provider}:{body}"

# ---------- OMG helpers ----------

def _build_create_order_params(
    merchant_trade_no: str,
    amount: int,
    item_name: str,
    payment_method: str = "ALL",
) -> dict[str, str]:
    return {
        "MerchantID": OMG_MERCHANT_ID,
        "MerchantTradeNo": merchant_trade_no,
        "MerchantTradeDate": time.strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": str(amount),
        "TradeDesc": "OMG test console",
        "ItemName": item_name,
        "ReturnURL": "http://localhost:8787/webhook",
        "ChoosePayment": payment_method,
        "EncryptType": "1",
    }

# ---------- FastAPI ----------

app = FastAPI(title="OMG Test Console")

@app.get("/")
def root():
    console_path = Path(__file__).parent / "console.html"
    return FileResponse(console_path)

@app.get("/api/test/logs")
def get_logs():
    return {"logs": list(LOGS)}

@app.post("/api/test/mac-calculate")
async def test_mac_calculate(req: Request):
    body = await req.json()
    params = body.get("params", {})
    mac = compute_check_mac(params, OMG_HASH_KEY, OMG_HASH_IV)
    log("OK", "mac-calculate", {"input_keys": list(params.keys()), "mac": mac})
    return {"ok": True, "mac": mac}

@app.post("/api/test/mac-verify")
async def test_mac_verify(req: Request):
    body = await req.json()
    params = body.get("params", {})
    is_ok, received, expected = verify_check_mac(params, OMG_HASH_KEY, OMG_HASH_IV)
    log("OK" if is_ok else "ERROR", "mac-verify", {
        "received": received, "expected": expected, "match": is_ok,
    })
    return {"ok": is_ok, "received": received, "expected": expected}

@app.post("/api/test/create-order")
async def test_create_order(req: Request):
    body = await req.json()
    amount = int(body.get("amount", 100))
    method = body.get("method", "ALL")
    trade_no = f"TEST{int(time.time())}{uuid.uuid4().hex[:6].upper()}"[:20]
    params = _build_create_order_params(trade_no, amount, "OMG Test", method)
    params["CheckMacValue"] = compute_check_mac(params, OMG_HASH_KEY, OMG_HASH_IV)

    if not OMG_API_HOST_STAGE:
        log("WARN", "create-order", {"note": "OMG_API_HOST_STAGE 未設定，跳過 HTTP POST", "params": params})
        return {"ok": True, "mode": "sign-only", "params": params}

    url = f"{OMG_API_HOST_STAGE.rstrip('/')}/Cashier/AioCheckOut/V5"
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, data=params)
        latency_ms = int((time.time() - t0) * 1000)
        log("OK", "create-order", {
            "url": url, "status": resp.status_code,
            "latency_ms": latency_ms, "body_len": len(resp.text),
        })
        return {"ok": True, "mode": "http", "status": resp.status_code,
                "latency_ms": latency_ms, "trade_no": trade_no}
    except Exception as e:
        log("ERROR", "create-order", {"url": url, "error": str(e)})
        raise HTTPException(500, str(e))

@app.post("/api/test/query-order")
async def test_query_order(req: Request):
    body = await req.json()
    trade_no = body.get("trade_no") or f"PROBE{uuid.uuid4().hex[:10].upper()}"
    params = {
        "MerchantID": OMG_MERCHANT_ID,
        "MerchantTradeNo": trade_no,
        "TimeStamp": str(int(time.time())),
        "PlatformID": "",
    }
    params["CheckMacValue"] = compute_check_mac(params, OMG_HASH_KEY, OMG_HASH_IV)

    if not OMG_API_HOST_STAGE:
        log("WARN", "query-order", {"note": "OMG_API_HOST_STAGE 未設定"})
        return {"ok": True, "mode": "sign-only", "params": params}

    url = f"{OMG_API_HOST_STAGE.rstrip('/')}/Cashier/QueryTradeInfo/V5"
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, data=params)
        latency_ms = int((time.time() - t0) * 1000)
        log("OK", "query-order", {
            "trade_no": trade_no, "status": resp.status_code,
            "latency_ms": latency_ms, "body_preview": resp.text[:200],
        })
        return {"ok": True, "status": resp.status_code, "latency_ms": latency_ms, "body": resp.text}
    except Exception as e:
        log("ERROR", "query-order", {"error": str(e)})
        raise HTTPException(500, str(e))

@app.post("/api/test/refund-sign")
async def test_refund_sign(req: Request):
    body = await req.json()
    trade_no = body.get("trade_no", "FAKETRADE")
    amount = int(body.get("amount", 1))
    params = {
        "MerchantID": OMG_MERCHANT_ID,
        "MerchantTradeNo": trade_no,
        "TradeNo": body.get("provider_trade_no", ""),
        "Action": "R",
        "TotalAmount": str(amount),
    }
    params["CheckMacValue"] = compute_check_mac(params, OMG_HASH_KEY, OMG_HASH_IV)
    log("OK", "refund-sign", {"trade_no": trade_no, "mac": params["CheckMacValue"]})
    return {"ok": True, "params": params, "note": "sign only, no HTTP POST"}

@app.post("/api/test/full-chain")
async def test_full_chain():
    """一鍵全鏈路測試"""
    chain = []
    start = time.time()

    # Step 1: create_order (sign + POST)
    try:
        r = await test_create_order(_FakeReq({"amount": 100, "method": "Credit"}))
        chain.append({"step": "create_order", "ok": True, "detail": r})
    except Exception as e:
        chain.append({"step": "create_order", "ok": False, "error": str(e)})

    # Step 2: query_order (fake trade_no — expect "查無此筆")
    try:
        r = await test_query_order(_FakeReq({"trade_no": f"PROBE{uuid.uuid4().hex[:8]}"}))
        chain.append({"step": "query_order", "ok": True, "detail": r})
    except Exception as e:
        chain.append({"step": "query_order", "ok": False, "error": str(e)})

    # Step 3: refund sign
    try:
        r = await test_refund_sign(_FakeReq({"trade_no": "FAKETRADE", "amount": 1}))
        chain.append({"step": "refund_sign", "ok": True, "detail": r})
    except Exception as e:
        chain.append({"step": "refund_sign", "ok": False, "error": str(e)})

    # Step 4: self-ping webhook
    try:
        fake_payload = {
            "MerchantID": OMG_MERCHANT_ID,
            "MerchantTradeNo": f"SELFPING{int(time.time())}",
            "TradeNo": "SELFPING",
            "RtnCode": "1",
            "TradeAmt": "100",
            "PaymentDate": time.strftime("%Y/%m/%d %H:%M:%S"),
        }
        fake_payload["CheckMacValue"] = compute_check_mac(fake_payload, OMG_HASH_KEY, OMG_HASH_IV)
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post("http://localhost:8787/webhook", data=fake_payload)
        chain.append({"step": "webhook_self_ping", "ok": resp.status_code == 200, "status": resp.status_code})
    except Exception as e:
        chain.append({"step": "webhook_self_ping", "ok": False, "error": str(e)})

    total_ms = int((time.time() - start) * 1000)
    all_ok = all(s["ok"] for s in chain)
    log("OK" if all_ok else "WARN", "full-chain", {"chain": chain, "total_ms": total_ms})
    return {"ok": all_ok, "total_ms": total_ms, "chain": chain}

@app.post("/api/test/webhook-simulate")
async def test_webhook_simulate(req: Request):
    """模擬 N 次重送打自己的 webhook，驗冪等性"""
    body = await req.json()
    n = int(body.get("n", 10))
    payload = {
        "MerchantID": OMG_MERCHANT_ID,
        "MerchantTradeNo": body.get("trade_no", f"SIM{int(time.time())}"),
        "TradeNo": body.get("provider_trade_no", "SIMTRADE"),
        "RtnCode": "1",
        "TradeAmt": str(body.get("amount", 100)),
        "PaymentDate": time.strftime("%Y/%m/%d %H:%M:%S"),
    }
    payload["CheckMacValue"] = compute_check_mac(payload, OMG_HASH_KEY, OMG_HASH_IV)

    async def _one_shot():
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.post("http://localhost:8787/webhook", data=payload)
            return r.status_code

    results = await asyncio.gather(*[_one_shot() for _ in range(n)], return_exceptions=True)
    status_200 = sum(1 for r in results if r == 200)
    log("OK", "webhook-simulate", {"n": n, "200_count": status_200, "idem_key": compute_idempotency_key("omg", payload)})
    return {"ok": True, "n": n, "200_count": status_200,
            "idempotency_key": compute_idempotency_key("omg", payload)}

# ---------- Webhook receiver (示範版，真的實作請看 guides/05) ----------

_seen_idem_keys: set[str] = set()
_seen_lock = asyncio.Lock()

@app.post("/webhook")
async def webhook(req: Request):
    form = await req.form()
    payload = dict(form)
    is_ok, received, expected = verify_check_mac(payload, OMG_HASH_KEY, OMG_HASH_IV)
    if not is_ok:
        log("ERROR", "webhook-recv", {"mac": "INVALID", "received": received, "expected": expected})
        raise HTTPException(400, "invalid mac")

    idem_key = compute_idempotency_key("omg", payload)
    async with _seen_lock:
        if idem_key in _seen_idem_keys:
            log("WARN", "webhook-recv", {"note": "early-dup", "idem_key": idem_key})
            return {"ok": True, "note": "early-dup"}
        _seen_idem_keys.add(idem_key)

    log("OK", "webhook-recv", {"trade_no": payload.get("MerchantTradeNo"), "idem_key": idem_key})
    return {"ok": True, "note": "new"}

# ---------- helper ----------

class _FakeReq:
    def __init__(self, body: dict[str, Any]):
        self._body = body
    async def json(self):
        return self._body

# ---------- Main ----------

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("OMG Test Console starting on http://localhost:8787/")
    print("=" * 60)
    if not OMG_HASH_KEY or not OMG_HASH_IV:
        print("⚠️  OMG_HASH_KEY / OMG_HASH_IV 未設定 — 所有 API 只會做簽名，不會真的打網關")
        print("    請複製 .env.example 成 .env 並填入測試金鑰")
    if not OMG_API_HOST_STAGE:
        print("⚠️  OMG_API_HOST_STAGE 未設定 — create_order / query_order 都只會 sign-only")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8787)
