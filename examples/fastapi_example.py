"""OMG Payment Gateway (歐買尬第三方支付) - Complete FastAPI Integration Example.
OMG 金流完整 FastAPI 串接範例 - 涵蓋所有 API 端點。

Company 公司: 茂為歐買尬數位科技股份有限公司 / MacroWell OMG Digital Entertainment Co., Ltd.
Country 國家: Taiwan 台灣
Official Website 官網: https://www.funpoint.com.tw/
API Document Version: V 1.4.9 (2025-11)

Author 作者: Mitchell Chen
Generated with assistance from Claude (Anthropic)
本文件以 Claude AI 輔助產出，一切以官方文件為主，如有問題請洽 OMG 官網。

Usage 使用方式:
    1. pip install fastapi uvicorn
    2. Change BASE_URL to your public domain / 修改 BASE_URL 為你的公開網域
    3. uvicorn fastapi_example:app --host 0.0.0.0 --port 8000
    4. Visit http://localhost:8000/pay to test / 瀏覽測試付款

Test Credentials 測試環境帳號:
    MerchantID: 1000031
    HashKey: 265fIDjIvesceXWM
    HashIV: pOOvhGd1V2pJbjfX
    Test Card 測試卡號: 4311-9522-2222-2222 (CVV: 222, Expiry: any future date)
"""

import hashlib
import secrets
import time
import json
from datetime import datetime
from urllib.parse import quote
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse

app = FastAPI(title="OMG Payment Complete Example | OMG 金流完整串接範例")

# ══════════════════════════════════════════════
# Configuration (Test Environment) | 設定（測試環境）
# ══════════════════════════════════════════════
MERCHANT_ID = "1000031"
HASH_KEY = "265fIDjIvesceXWM"
HASH_IV = "pOOvhGd1V2pJbjfX"

# URLs - Switch to production when going live / 正式上線時切換
# Test 測試: payment-stage.funpoint.com.tw
# Prod 正式: payment.funpoint.com.tw
PAYMENT_BASE = "https://payment-stage.funpoint.com.tw"
AIO_URL = f"{PAYMENT_BASE}/Cashier/AioCheckOut/V5"
QUERY_TRADE_URL = f"{PAYMENT_BASE}/Cashier/QueryTradeInfo/V5"
QUERY_RECURRING_URL = f"{PAYMENT_BASE}/Cashier/QueryCreditCardPeriodInfo"
RECURRING_ACTION_URL = f"{PAYMENT_BASE}/Cashier/CreditCardPeriodAction"
DO_ACTION_URL = f"{PAYMENT_BASE}/CreditDetail/DoAction"
QUERY_CREDIT_DETAIL_URL = f"{PAYMENT_BASE}/CreditDetail/QueryTrade/V2"

BASE_URL = "https://your-domain.com"  # ← Change to your domain / 換成你的網域

# .NET URL Encode Replacement Table | .NET URL Encode 替換表
DOTNET_REPLACEMENTS = {
    "%2d": "-", "%5f": "_", "%2e": ".",
    "%21": "!", "%2a": "*", "%28": "(", "%29": ")",
}


# ══════════════════════════════════════════════
# CheckMacValue Utilities | CheckMacValue 工具函式
# ══════════════════════════════════════════════

def generate_check_mac_value(params: dict) -> str:
    """Generate OMG CheckMacValue (SHA256).
    產生 OMG 金流 CheckMacValue (SHA256)。

    Algorithm 演算法:
    1. Remove CheckMacValue param / 移除 CheckMacValue
    2. Sort by key A-Z (case-insensitive) / 依參數名 A-Z 排序（不分大小寫）
    3. Join as key=value with & / 組成字串
    4. Prepend HashKey=, append &HashIV= / 前後加上 Hash
    5. URL encode → lowercase / URL encode → 小寫
    6. .NET replacements / .NET 替換
    7. SHA256 → uppercase / SHA256 → 大寫
    """
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue"}
    sorted_keys = sorted(filtered.keys(), key=lambda k: k.lower())
    param_str = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
    raw = f"HashKey={HASH_KEY}&{param_str}&HashIV={HASH_IV}"
    encoded = quote(raw, safe="").lower()
    for old, new in DOTNET_REPLACEMENTS.items():
        encoded = encoded.replace(old, new)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()


def verify_check_mac_value(params: dict) -> bool:
    """Verify CheckMacValue from OMG callback.
    驗證 OMG 回傳的 CheckMacValue。"""
    received = params.get("CheckMacValue", "")
    expected = generate_check_mac_value(params)
    return received.upper() == expected.upper()


def generate_order_no(prefix: str = "T") -> str:
    """Generate unique order number (max 20 chars).
    產生唯一訂單編號（最長 20 碼英數字）。"""
    ts = datetime.now().strftime("%y%m%d%H%M%S")
    rand = secrets.token_hex(3).upper()
    return f"{prefix}{ts}{rand}"[:20]


def build_form_html(params: dict, action_url: str, title: str) -> str:
    """Build auto-submit HTML form. 建立自動提交 HTML 表單。"""
    fields = "\n".join(
        f'            <input type="hidden" name="{k}" value="{v}">'
        for k, v in params.items()
    )
    return f"""
    <html>
    <head><title>{title}</title></head>
    <body style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
        <div style="text-align:center">
            <h2>{title}</h2>
            <p>Click the button if not redirected automatically | 如果沒有自動跳轉請點擊按鈕</p>
            <form id="omg-form" method="POST" action="{action_url}">
{fields}
                <button type="submit" style="padding:10px 30px;font-size:16px;cursor:pointer;">
                    Go to Payment | 前往付款
                </button>
            </form>
        </div>
        <script>document.getElementById('omg-form').submit();</script>
    </body>
    </html>
    """


# ══════════════════════════════════════════════
# API 1: AioCheckOut/V5 - Create Order 產生訂單
# ══════════════════════════════════════════════

@app.get("/pay", response_class=HTMLResponse)
async def create_credit_payment():
    """Create one-time credit card payment. 建立一次性信用卡付款。"""
    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": generate_order_no("C"),
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": "100",
        "TradeDesc": "OMG Payment Test",
        "ItemName": "Test Item 測試商品",
        "ReturnURL": f"{BASE_URL}/notify",
        "OrderResultURL": f"{BASE_URL}/result",
        "ChoosePayment": "Credit",
        "EncryptType": "1",
        "NeedExtraPaidInfo": "Y",
    }
    params["CheckMacValue"] = generate_check_mac_value(params)
    return build_form_html(params, AIO_URL, "Redirecting to OMG Payment... | 正在跳轉至付款頁面...")


@app.get("/pay-installment", response_class=HTMLResponse)
async def create_installment_payment():
    """Create credit card installment payment (6 periods).
    建立信用卡分期付款（6期）。僅支援玉山銀行收單。"""
    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": generate_order_no("I"),
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": "6000",
        "TradeDesc": "Installment Test",
        "ItemName": "Installment Item 分期商品",
        "ReturnURL": f"{BASE_URL}/notify",
        "OrderResultURL": f"{BASE_URL}/result",
        "ChoosePayment": "Credit",
        "EncryptType": "1",
        "CreditInstallment": "3,6,12",  # Let user choose 3/6/12 期
    }
    params["CheckMacValue"] = generate_check_mac_value(params)
    return build_form_html(params, AIO_URL, "Installment Payment | 分期付款")


@app.get("/pay-recurring", response_class=HTMLResponse)
async def create_recurring_payment():
    """Create recurring payment - monthly $299 for 12 periods.
    建立定期定額 - 每月 $299 共 12 期。"""
    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": generate_order_no("R"),
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": "299",
        "TradeDesc": "Recurring Test",
        "ItemName": "Monthly Subscription 月訂閱方案",
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
    return build_form_html(params, AIO_URL, "Recurring Payment | 定期定額付款 NT$299/月 x 12期")


@app.get("/pay-atm", response_class=HTMLResponse)
async def create_atm_payment():
    """Create ATM virtual account payment. 建立 ATM 虛擬帳號付款。"""
    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": generate_order_no("A"),
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": "500",
        "TradeDesc": "ATM Payment Test",
        "ItemName": "ATM Test Item ATM測試商品",
        "ReturnURL": f"{BASE_URL}/notify",
        "OrderResultURL": f"{BASE_URL}/result",
        "ChoosePayment": "ATM",
        "EncryptType": "1",
        "ExpireDate": "3",  # 3 days to pay / 3天內繳費
        "PaymentInfoURL": f"{BASE_URL}/payment-info",
        "ClientRedirectURL": f"{BASE_URL}/payment-info-redirect",
    }
    params["CheckMacValue"] = generate_check_mac_value(params)
    return build_form_html(params, AIO_URL, "ATM Payment | ATM 虛擬帳號付款")


@app.get("/pay-cvs", response_class=HTMLResponse)
async def create_cvs_payment():
    """Create CVS (convenience store) code payment. 建立超商代碼繳款。"""
    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": generate_order_no("V"),
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": "300",
        "TradeDesc": "CVS Payment Test",
        "ItemName": "CVS Test Item 超商測試商品",
        "ReturnURL": f"{BASE_URL}/notify",
        "OrderResultURL": f"{BASE_URL}/result",
        "ChoosePayment": "CVS",
        "EncryptType": "1",
        "StoreExpireDate": "10080",  # 7 days in minutes / 7天（分鐘）
        "Desc_1": "OMG Payment",
        "Desc_2": "Test Order",
        "PaymentInfoURL": f"{BASE_URL}/payment-info",
        "ClientRedirectURL": f"{BASE_URL}/payment-info-redirect",
    }
    params["CheckMacValue"] = generate_check_mac_value(params)
    return build_form_html(params, AIO_URL, "CVS Payment | 超商代碼繳款")


@app.get("/pay-barcode", response_class=HTMLResponse)
async def create_barcode_payment():
    """Create BARCODE (convenience store barcode) payment.
    建立超商條碼繳款。回傳 3 段條碼需轉 Code39 格式。"""
    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": generate_order_no("B"),
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": "200",
        "TradeDesc": "Barcode Payment Test",
        "ItemName": "Barcode Test Item 條碼測試商品",
        "ReturnURL": f"{BASE_URL}/notify",
        "OrderResultURL": f"{BASE_URL}/result",
        "ChoosePayment": "BARCODE",
        "EncryptType": "1",
        "StoreExpireDate": "7",  # 7 days / 7天
        "Desc_1": "OMG Payment",
        "PaymentInfoURL": f"{BASE_URL}/payment-info",
        "ClientRedirectURL": f"{BASE_URL}/payment-info-redirect",
    }
    params["CheckMacValue"] = generate_check_mac_value(params)
    return build_form_html(params, AIO_URL, "Barcode Payment | 超商條碼繳款")


@app.get("/pay-all", response_class=HTMLResponse)
async def create_all_payment():
    """Show all available payment methods. 顯示所有可用付款方式。"""
    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": generate_order_no("X"),
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": "100",
        "TradeDesc": "All Methods Test",
        "ItemName": "All Payment Test 全付款方式測試",
        "ReturnURL": f"{BASE_URL}/notify",
        "OrderResultURL": f"{BASE_URL}/result",
        "ChoosePayment": "ALL",
        "EncryptType": "1",
        "PaymentInfoURL": f"{BASE_URL}/payment-info",
        "ClientRedirectURL": f"{BASE_URL}/payment-info-redirect",
    }
    params["CheckMacValue"] = generate_check_mac_value(params)
    return build_form_html(params, AIO_URL, "All Payment Methods | 所有付款方式")


# ══════════════════════════════════════════════
# Notification Endpoints 通知端點
# ══════════════════════════════════════════════

@app.post("/notify")
async def payment_notify(request: Request):
    """ReturnURL - Server POST notification. 伺服器端付款結果通知。
    CRITICAL: Must respond '1|OK' / 必須回應 '1|OK'。"""
    form = await request.form()
    data = dict(form)

    if not verify_check_mac_value(data):
        print(f"[ERROR] CheckMacValue verification failed | 驗證失敗")
        return PlainTextResponse("0|CheckMacValue Error")

    rtn_code = data.get("RtnCode", "")
    order_no = data.get("MerchantTradeNo", "")
    trade_no = data.get("TradeNo", "")
    amount = data.get("TradeAmt", "")
    simulate = data.get("SimulatePaid", "0")

    if rtn_code == "1":
        sim_tag = " [SIMULATED]" if simulate == "1" else ""
        print(f"[SUCCESS{sim_tag}] Payment OK | 付款成功 - Order: {order_no}, TradeNo: {trade_no}, Amount: NT${amount}")
        # TODO: Update database order status / 更新資料庫訂單狀態
        # TODO: Check idempotency (avoid processing duplicate notifications) / 冪等性檢查
    else:
        rtn_msg = data.get("RtnMsg", "")
        print(f"[FAILED] Payment failed | 付款失敗 - Order: {order_no}, Code: {rtn_code}, Msg: {rtn_msg}")

    return PlainTextResponse("1|OK")


@app.post("/payment-info")
async def payment_info_notify(request: Request):
    """PaymentInfoURL - ATM/CVS/BARCODE payment info notification.
    ATM/超商 取號結果通知。"""
    form = await request.form()
    data = dict(form)

    if not verify_check_mac_value(data):
        return PlainTextResponse("0|CheckMacValue Error")

    rtn_code = data.get("RtnCode", "")
    payment_type = data.get("PaymentType", "")
    order_no = data.get("MerchantTradeNo", "")

    if rtn_code == "2":
        # ATM virtual account generated / ATM 取號成功
        bank_code = data.get("BankCode", "")
        v_account = data.get("vAccount", "")
        expire = data.get("ExpireDate", "")
        print(f"[ATM] 取號成功 - Order: {order_no}, Bank: {bank_code}, Account: {v_account}, Expire: {expire}")

    elif rtn_code == "10100073":
        # CVS/BARCODE code generated / 超商取號成功
        if "Barcode1" in data:
            barcode1 = data.get("Barcode1", "")
            barcode2 = data.get("Barcode2", "")
            barcode3 = data.get("Barcode3", "")
            print(f"[BARCODE] 取號成功 - Order: {order_no}, Codes: {barcode1} | {barcode2} | {barcode3}")
        else:
            payment_no = data.get("PaymentNo", "")
            expire = data.get("ExpireDate", "")
            print(f"[CVS] 取號成功 - Order: {order_no}, PaymentNo: {payment_no}, Expire: {expire}")

    return PlainTextResponse("1|OK")


@app.post("/payment-info-redirect", response_class=HTMLResponse)
async def payment_info_redirect(request: Request):
    """ClientRedirectURL - Redirect user after getting ATM/CVS/BARCODE info.
    使用者取號後跳轉頁面。"""
    form = await request.form()
    data = dict(form)
    payment_type = data.get("PaymentType", "")
    order_no = data.get("MerchantTradeNo", "")

    info_html = ""
    if "BankCode" in data:
        info_html = f"<p>銀行代碼 Bank Code: <strong>{data.get('BankCode')}</strong></p>"
        info_html += f"<p>虛擬帳號 Virtual Account: <strong>{data.get('vAccount')}</strong></p>"
        info_html += f"<p>繳費期限 Deadline: <strong>{data.get('ExpireDate')}</strong></p>"
    elif "Barcode1" in data:
        info_html = f"<p>條碼1: <strong>{data.get('Barcode1')}</strong></p>"
        info_html += f"<p>條碼2: <strong>{data.get('Barcode2')}</strong></p>"
        info_html += f"<p>條碼3: <strong>{data.get('Barcode3')}</strong></p>"
    elif "PaymentNo" in data:
        info_html = f"<p>繳費代碼 Payment Code: <strong>{data.get('PaymentNo')}</strong></p>"
        info_html += f"<p>繳費期限 Deadline: <strong>{data.get('ExpireDate')}</strong></p>"

    return f"""
    <html><body style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;background:#f5f5f5;">
    <div style="text-align:center;padding:40px;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <h2>Payment Info | 繳費資訊</h2>
        <p>Order 訂單: {order_no}</p>
        <p>Type 方式: {payment_type}</p>
        {info_html}
        <p style="color:#666;margin-top:20px">請於期限內完成繳費 / Please complete payment before deadline</p>
    </div></body></html>
    """


@app.post("/period-notify")
async def period_notify(request: Request):
    """PeriodReturnURL - Recurring payment notification (2nd period onwards).
    定期定額後續扣款通知（第 2 期起）。"""
    form = await request.form()
    data = dict(form)

    if not verify_check_mac_value(data):
        return PlainTextResponse("0|CheckMacValue Error")

    rtn_code = data.get("RtnCode", "")
    order_no = data.get("MerchantTradeNo", "")
    total_times = data.get("TotalSuccessTimes", "")
    total_amount = data.get("TotalSuccessAmount", "")

    if rtn_code == "1":
        print(f"[RECURRING OK] 扣款成功 - Order: {order_no}, Total times: {total_times}, Total: NT${total_amount}")
    else:
        rtn_msg = data.get("RtnMsg", "")
        print(f"[RECURRING FAIL] 扣款失敗 - Order: {order_no}, Msg: {rtn_msg}")

    return PlainTextResponse("1|OK")


@app.post("/result", response_class=HTMLResponse)
async def payment_result(request: Request):
    """OrderResultURL - User redirect after payment. 使用者付款完成跳轉頁。
    Note: Actual result should be based on ReturnURL, not this page.
    注意：實際付款結果以 ReturnURL 通知為準，此頁面僅供參考。"""
    form = await request.form()
    data = dict(form)
    rtn_code = data.get("RtnCode", "")
    order_no = data.get("MerchantTradeNo", "")

    if rtn_code == "1":
        msg = f"Payment Successful! | 付款成功！"
        color = "#22c55e"
    else:
        msg = f"Payment Incomplete | 付款未完成"
        color = "#ef4444"

    return f"""
    <html><body style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;background:#f5f5f5;">
    <div style="text-align:center;padding:40px;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <h1 style="color:{color}">{msg}</h1>
        <p>Order 訂單: {order_no}</p>
        <p style="color:#666">此頁面僅供參考，實際付款結果以系統通知為準。</p>
        <p style="color:#666">This page is for reference only. Actual result is based on server notification.</p>
        <a href="/" style="color:#3b82f6">Back to Home | 返回首頁</a>
    </div></body></html>
    """


# ══════════════════════════════════════════════
# API 2: QueryTradeInfo/V5 - Query Trade 查詢訂單
# ══════════════════════════════════════════════

@app.get("/query/{order_no}")
async def query_trade(order_no: str):
    """Query trade info by order number. 以訂單編號查詢交易狀態。
    TimeStamp must be within 3 min of current time / 時間戳需在 3 分鐘內。"""
    import httpx

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "TimeStamp": str(int(time.time())),
    }
    params["CheckMacValue"] = generate_check_mac_value(params)

    async with httpx.AsyncClient() as client:
        resp = await client.post(QUERY_TRADE_URL, data=params)
        return PlainTextResponse(resp.text)


# ══════════════════════════════════════════════
# API 3: QueryCreditCardPeriodInfo 查詢定期定額
# ══════════════════════════════════════════════

@app.get("/query-recurring/{order_no}")
async def query_recurring(order_no: str):
    """Query recurring payment info. 查詢定期定額訂單資訊。
    Returns ExecStatus: 0=已停用, 1=執行中, 2=已完成"""
    import httpx

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "TimeStamp": str(int(time.time())),
    }
    params["CheckMacValue"] = generate_check_mac_value(params)

    async with httpx.AsyncClient() as client:
        resp = await client.post(QUERY_RECURRING_URL, data=params)
        return PlainTextResponse(resp.text)


# ══════════════════════════════════════════════
# API 4: CreditCardPeriodAction 定期定額停用
# ══════════════════════════════════════════════

@app.post("/cancel-recurring/{order_no}")
async def cancel_recurring(order_no: str):
    """Cancel recurring payment. WARNING: Irreversible!
    停用定期定額。警告：停用後無法重新啟用！"""
    import httpx

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "Action": "Cancel",
    }
    params["CheckMacValue"] = generate_check_mac_value(params)

    async with httpx.AsyncClient() as client:
        resp = await client.post(RECURRING_ACTION_URL, data=params)
        return PlainTextResponse(resp.text)


# ══════════════════════════════════════════════
# API 5: DoAction - Credit Card Capture/Refund 信用卡請退款
# ══════════════════════════════════════════════

@app.post("/do-action")
async def do_action(
    order_no: str = Form(...),
    trade_no: str = Form(...),
    action: str = Form(...),  # C=Capture/關帳, R=Refund/退刷, E=Cancel/取消, N=Abandon/放棄
    amount: int = Form(...),
):
    """Credit card post-authorization action. 信用卡請退款操作。
    Actions: C=關帳(Capture), R=退刷(Refund), E=取消(Cancel), N=放棄(Abandon)
    Rules 規則:
    - Authorization → C (Capture) → R (Refund)
    - Authorization → E (Cancel, before capture)
    - Authorization → N (Abandon)
    """
    import httpx

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "TradeNo": trade_no,
        "Action": action,
        "TotalAmount": str(amount),
    }
    params["CheckMacValue"] = generate_check_mac_value(params)

    async with httpx.AsyncClient() as client:
        resp = await client.post(DO_ACTION_URL, data=params)
        return PlainTextResponse(resp.text)


# ══════════════════════════════════════════════
# API 6: QueryTrade/V2 - Query Credit Card Detail 查詢信用卡單筆明細
# ══════════════════════════════════════════════

@app.get("/query-credit-detail")
async def query_credit_detail(
    credit_refund_id: str,
    credit_amount: int,
):
    """Query credit card transaction detail. 查詢信用卡單筆明細記錄。
    Returns: TradeID, amount, clsamt, authtime, status, close_data"""
    import httpx

    # CreditCheckCode = SHA256(MerchantID + CreditRefundId + CreditAmount + HashKey + HashIV)
    raw_str = f"{MERCHANT_ID}{credit_refund_id}{credit_amount}{HASH_KEY}{HASH_IV}"
    credit_check_code = hashlib.sha256(raw_str.encode("utf-8")).hexdigest().upper()

    params = {
        "MerchantID": MERCHANT_ID,
        "CreditRefundId": credit_refund_id,
        "CreditAmount": str(credit_amount),
        "CreditCheckCode": credit_check_code,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(QUERY_CREDIT_DETAIL_URL, data=params)
        return PlainTextResponse(resp.text)


# ══════════════════════════════════════════════
# Home Page with Test Links 首頁測試連結
# ══════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with all test links. 首頁：所有測試連結。"""
    return """
    <html>
    <head><title>OMG Payment Test | OMG 金流測試</title></head>
    <body style="max-width:800px;margin:40px auto;font-family:sans-serif;padding:0 20px;">
        <h1>OMG Payment Gateway Test | OMG 金流測試</h1>
        <p>Company 公司: 茂為歐買尬數位科技股份有限公司 / MacroWell OMG Digital Entertainment Co., Ltd.</p>
        <p>Country 國家: Taiwan 台灣 | Official 官網: <a href="https://www.funpoint.com.tw/">funpoint.com.tw</a></p>
        <hr>

        <h2>Create Order 產生訂單 (AioCheckOut/V5)</h2>
        <ul>
            <li><a href="/pay">Credit Card 信用卡一次付款 (NT$100)</a></li>
            <li><a href="/pay-installment">Credit Card Installment 信用卡分期 (NT$6,000, 3/6/12期)</a></li>
            <li><a href="/pay-recurring">Recurring 定期定額 (NT$299/月 x 12期)</a></li>
            <li><a href="/pay-atm">ATM 虛擬帳號 (NT$500)</a></li>
            <li><a href="/pay-cvs">CVS 超商代碼 (NT$300)</a></li>
            <li><a href="/pay-barcode">BARCODE 超商條碼 (NT$200)</a></li>
            <li><a href="/pay-all">ALL 所有付款方式 (NT$100)</a></li>
        </ul>

        <h2>Query APIs 查詢 API</h2>
        <ul>
            <li><a href="/query/TEST_ORDER_NO">QueryTradeInfo/V5 查詢訂單</a> (replace TEST_ORDER_NO)</li>
            <li><a href="/query-recurring/TEST_ORDER_NO">QueryCreditCardPeriodInfo 查詢定期定額</a></li>
            <li>POST /cancel-recurring/{order_no} - CreditCardPeriodAction 定期定額停用</li>
            <li>POST /do-action - DoAction 信用卡請退款 (C/R/E/N)</li>
            <li><a href="/query-credit-detail?credit_refund_id=TEST&credit_amount=100">QueryTrade/V2 查詢信用卡明細</a></li>
        </ul>

        <h2>Test Credentials 測試帳號</h2>
        <table border="1" cellpadding="8" style="border-collapse:collapse;">
            <tr><td>MerchantID</td><td><code>1000031</code></td></tr>
            <tr><td>HashKey</td><td><code>265fIDjIvesceXWM</code></td></tr>
            <tr><td>HashIV</td><td><code>pOOvhGd1V2pJbjfX</code></td></tr>
            <tr><td>Test Card 測試卡</td><td><code>4311-9522-2222-2222</code> (CVV: 222)</td></tr>
        </table>

        <p style="margin-top:20px;color:#999;font-size:12px;">
            Author 作者: Mitchell Chen | Generated with Claude (Anthropic) AI assistance<br>
            一切以官方文件為主，如有問題請洽 <a href="https://www.funpoint.com.tw/">OMG 官網</a>
        </p>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
