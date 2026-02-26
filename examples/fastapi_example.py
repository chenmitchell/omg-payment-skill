"""OMG Payment Gateway - Complete FastAPI Integration Example.
Test: uvicorn fastapi_example:app --host 0.0.0.0 --port 8000
Visit: http://localhost:8000/pay
Test Card: 4311-9522-2222-2222, CVV: 222
"""
import hashlib, secrets
from datetime import datetime
from urllib.parse import quote
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

app = FastAPI(title="OMG Payment Example")

MERCHANT_ID = "1000031"
HASH_KEY = "265fIDjIvesceXWM"
HASH_IV = "pOOvhGd1V2pJbjfX"
AIO_URL = "https://payment-stage.funpoint.com.tw/Cashier/AioCheckOut/V5"
BASE_URL = "https://your-domain.com"

DOTNET_REPLACEMENTS = {
    "%2d": "-", "%5f": "_", "%2e": ".",
    "%21": "!", "%2a": "*", "%28": "(", "%29": ")",
}

def generate_check_mac_value(params: dict) -> str:
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue"}
    sorted_keys = sorted(filtered.keys(), key=lambda k: k.lower())
    param_str = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
    raw = f"HashKey={HASH_KEY}&{param_str}&HashIV={HASH_IV}"
    encoded = quote(raw, safe="").lower()
    for old, new in DOTNET_REPLACEMENTS.items():
        encoded = encoded.replace(old, new)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()

def verify_check_mac_value(params: dict) -> bool:
    received = params.get("CheckMacValue", "")
    return received.upper() == generate_check_mac_value(params).upper()

@app.get("/pay", response_class=HTMLResponse)
async def create_payment():
    order_no = f"T{datetime.now().strftime('%y%m%d%H%M%S')}{secrets.token_hex(2)}"
    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": "100",
        "TradeDesc": "Test Payment",
        "ItemName": "Test Item",
        "ReturnURL": f"{BASE_URL}/notify",
        "OrderResultURL": f"{BASE_URL}/result",
        "ChoosePayment": "Credit",
        "EncryptType": "1",
    }
    params["CheckMacValue"] = generate_check_mac_value(params)
    fields = "".join(f'<input type="hidden" name="{k}" value="{v}">' for k, v in params.items())
    return f'<html><body><form id="f" method="POST" action="{AIO_URL}">{fields}</form><script>document.getElementById("f").submit();</script></body></html>'

@app.get("/pay-recurring", response_class=HTMLResponse)
async def create_recurring():
    order_no = f"R{datetime.now().strftime('%y%m%d%H%M%S')}{secrets.token_hex(2)}"
    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": "299",
        "TradeDesc": "Recurring Test",
        "ItemName": "Monthly Plan",
        "ReturnURL": f"{BASE_URL}/notify",
        "OrderResultURL": f"{BASE_URL}/result",
        "ChoosePayment": "Credit",
        "EncryptType": "1",
        "PeriodAmount": "299",
        "PeriodType": "M",
        "Frequency": "1",
        "ExecTimes": "12",
        "PeriodReturnURL": f"{BASE_URL}/period-notify",
    }
    params["CheckMacValue"] = generate_check_mac_value(params)
    fields = "".join(f'<input type="hidden" name="{k}" value="{v}">' for k, v in params.items())
    return f'<html><body><form id="f" method="POST" action="{AIO_URL}">{fields}</form><script>document.getElementById("f").submit();</script></body></html>'

@app.post("/notify")
async def payment_notify(request: Request):
    form = await request.form()
    data = dict(form)
    if not verify_check_mac_value(data):
        return PlainTextResponse("0|CheckMacValue Error")
    rtn_code = data.get("RtnCode", "")
    order_no = data.get("MerchantTradeNo", "")
    if rtn_code == "1":
        print(f"[OK] Payment success: {order_no}")
    else:
        print(f"[FAIL] Payment failed: {order_no}, reason: {data.get('RtnMsg', '')}")
    return PlainTextResponse("1|OK")

@app.post("/period-notify")
async def period_notify(request: Request):
    form = await request.form()
    data = dict(form)
    if not verify_check_mac_value(data):
        return PlainTextResponse("0|CheckMacValue Error")
    print(f"[RECURRING] Order: {data.get('MerchantTradeNo')}, Times: {data.get('TotalSuccessTimes')}")
    return PlainTextResponse("1|OK")

@app.post("/result", response_class=HTMLResponse)
async def payment_result(request: Request):
    form = await request.form()
    rtn_code = form.get("RtnCode", "")
    msg = "Payment OK!" if rtn_code == "1" else "Payment incomplete"
    color = "#22c55e" if rtn_code == "1" else "#ef4444"
    return f'<html><body style="display:flex;align-items:center;justify-content:center;height:100vh"><h1 style="color:{color}">{msg}</h1></body></html>'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
