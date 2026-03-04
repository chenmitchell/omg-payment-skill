"""OMG Payment Gateway (歐買尬第三方支付) - Complete FastAPI Integration Example.
OMG 金流完整 FastAPI 串接範例 - 涵蓋所有 API 端點。

Company 公司: 茂為歐買尬數位科技股份有限公司 / MacroWell OMG Digital Entertainment Co., Ltd.
Country 國家: Taiwan 台灣
Official Website 官網: https://www.funpoint.com.tw/
API Document Version: V 1.4.9 (2025-11)

Author 作者: Mitchell Chen
Generated with assistance from Claude (Anthropic)
本文件以 Claude AI 輔助產出，一切以官方文件為主，如有問題請洽 OMG 官網。

Features 功能:
    - 6 OMG API endpoints (AioCheckOut, QueryTradeInfo, QueryCreditCardPeriodInfo, etc.)
    - Environment variable configuration (.env support) / 環境變數設定
    - Health check endpoint with API connectivity test / 健康檢查端點
    - Admin dashboard with transaction list and metrics / 管理員儀表板
    - In-memory transaction store for monitoring / 交易記錄存儲
    - Real-time metrics and monitoring endpoint / 實時監控指標
    - Comprehensive logging throughout / 全面日誌記錄

Usage 使用方式:
    1. pip install fastapi uvicorn python-dotenv
    2. Create .env file with OMG credentials / 建立 .env 檔案
    3. uvicorn fastapi_example:app --host 0.0.0.0 --port 8000
    4. Visit http://localhost:8000/ for home page / 瀏覽首頁
    5. Visit http://localhost:8000/admin for dashboard / 瀏覽管理儀表板
    6. Visit http://localhost:8000/health for health check / 檢查健康狀態

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
import os
import logging
from datetime import datetime, timedelta
from urllib.parse import quote
from collections import defaultdict
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse

# ══════════════════════════════════════════════
# Logging Configuration | 日誌設定
# ══════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════
# Environment Configuration | 環境變數設定
# ══════════════════════════════════════════════
# Load from environment variables with fallback to test credentials / 從環境變數讀取，默認為測試帳號
MERCHANT_ID = os.getenv("OMG_MERCHANT_ID", "1000031")
HASH_KEY = os.getenv("OMG_HASH_KEY", "265fIDjIvesceXWM")
HASH_IV = os.getenv("OMG_HASH_IV", "pOOvhGd1V2pJbjfX")
IS_PRODUCTION = os.getenv("OMG_PRODUCTION", "false").lower() == "true"
PAYMENT_BASE = "https://payment.funpoint.com.tw" if IS_PRODUCTION else "https://payment-stage.funpoint.com.tw"

logger.info(f"OMG Payment Configuration | 金流設定")
logger.info(f"  Environment 環境: {'PRODUCTION 正式' if IS_PRODUCTION else 'STAGING 測試'}")
logger.info(f"  Merchant ID: {MERCHANT_ID}")
logger.info(f"  Payment Base URL: {PAYMENT_BASE}")

app = FastAPI(title="OMG Payment Complete Example | OMG 金流完整串接範例")

# ══════════════════════════════════════════════
# In-Memory Transaction Store | 交易記錄存儲
# ══════════════════════════════════════════════
# Simple dict-based store for demo tracking / 簡單的交易記錄存儲
transactions = {}
transaction_lock_time = {}  # Track request times for idempotency / 冪等性檢查
request_count = defaultdict(int)
success_count = 0
failed_count = 0
start_time = time.time()
AIO_URL = f"{PAYMENT_BASE}/Cashier/AioCheckOut/V5"
QUERY_TRADE_URL = f"{PAYMENT_BASE}/Cashier/QueryTradeInfo/V5"
QUERY_RECURRING_URL = f"{PAYMENT_BASE}/Cashier/QueryCreditCardPeriodInfo"
RECURRING_ACTION_URL = f"{PAYMENT_BASE}/Cashier/CreditCardPeriodAction"
DO_ACTION_URL = f"{PAYMENT_BASE}/CreditDetail/DoAction"
QUERY_CREDIT_DETAIL_URL = f"{PAYMENT_BASE}/CreditDetail/QueryTrade/V2"

BASE_URL = os.getenv("BASE_URL", "https://your-domain.com")  # ← Change to your domain / 換成你的網域

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
    request_count["/pay"] += 1
    order_no = generate_order_no("C")
    logger.info(f"Creating credit card payment | 建立信用卡付款 - Order: {order_no}")

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
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
    request_count["/pay-installment"] += 1
    order_no = generate_order_no("I")
    logger.info(f"Creating installment payment | 建立分期付款 - Order: {order_no}")

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
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
    request_count["/pay-recurring"] += 1
    order_no = generate_order_no("R")
    logger.info(f"Creating recurring payment | 建立定期定額 - Order: {order_no}")

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
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
    request_count["/pay-atm"] += 1
    order_no = generate_order_no("A")
    logger.info(f"Creating ATM payment | 建立 ATM 付款 - Order: {order_no}")

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
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
    request_count["/pay-cvs"] += 1
    order_no = generate_order_no("V")
    logger.info(f"Creating CVS payment | 建立超商付款 - Order: {order_no}")

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
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
    request_count["/pay-barcode"] += 1
    order_no = generate_order_no("B")
    logger.info(f"Creating barcode payment | 建立條碼付款 - Order: {order_no}")

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
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
    request_count["/pay-all"] += 1
    order_no = generate_order_no("X")
    logger.info(f"Creating all-methods payment | 建立所有方式付款 - Order: {order_no}")

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
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
    global success_count, failed_count

    form = await request.form()
    data = dict(form)

    request_count["/notify"] += 1

    if not verify_check_mac_value(data):
        logger.error(f"CheckMacValue verification failed | 驗證失敗")
        failed_count += 1
        return PlainTextResponse("0|CheckMacValue Error")

    rtn_code = data.get("RtnCode", "")
    order_no = data.get("MerchantTradeNo", "")
    trade_no = data.get("TradeNo", "")
    amount = data.get("TradeAmt", "")
    simulate = data.get("SimulatePaid", "0")
    payment_type = data.get("PaymentType", "Credit")

    # Idempotency check - avoid processing duplicate notifications / 冪等性檢查
    if order_no in transaction_lock_time:
        last_request = transaction_lock_time[order_no]
        if time.time() - last_request < 5:  # Within 5 seconds = duplicate / 5 秒內視為重複
            logger.warning(f"Duplicate notification detected | 檢測到重複通知 - Order: {order_no}")
            return PlainTextResponse("1|OK")

    transaction_lock_time[order_no] = time.time()

    if rtn_code == "1":
        sim_tag = " [SIMULATED]" if simulate == "1" else ""
        logger.info(f"[SUCCESS{sim_tag}] Payment OK | 付款成功 - Order: {order_no}, TradeNo: {trade_no}, Amount: NT${amount}")
        success_count += 1

        # Store in transaction store / 存儲到交易記錄
        transactions[order_no] = {
            "status": "success",
            "order_no": order_no,
            "trade_no": trade_no,
            "amount": amount,
            "payment_type": payment_type,
            "timestamp": datetime.now().isoformat(),
            "simulated": simulate == "1"
        }
    else:
        rtn_msg = data.get("RtnMsg", "")
        logger.error(f"[FAILED] Payment failed | 付款失敗 - Order: {order_no}, Code: {rtn_code}, Msg: {rtn_msg}")
        failed_count += 1

        # Store failed transaction / 存儲失敗的交易
        transactions[order_no] = {
            "status": "failed",
            "order_no": order_no,
            "amount": amount,
            "payment_type": payment_type,
            "error_code": rtn_code,
            "error_message": rtn_msg,
            "timestamp": datetime.now().isoformat()
        }

    return PlainTextResponse("1|OK")


@app.post("/payment-info")
async def payment_info_notify(request: Request):
    """PaymentInfoURL - ATM/CVS/BARCODE payment info notification.
    ATM/超商 取號結果通知。"""
    form = await request.form()
    data = dict(form)

    request_count["/payment-info"] += 1

    if not verify_check_mac_value(data):
        logger.error("CheckMacValue verification failed for payment-info")
        return PlainTextResponse("0|CheckMacValue Error")

    rtn_code = data.get("RtnCode", "")
    payment_type = data.get("PaymentType", "")
    order_no = data.get("MerchantTradeNo", "")
    amount = data.get("TradeAmt", "")

    if rtn_code == "2":
        # ATM virtual account generated / ATM 取號成功
        bank_code = data.get("BankCode", "")
        v_account = data.get("vAccount", "")
        expire = data.get("ExpireDate", "")
        logger.info(f"[ATM] 取號成功 - Order: {order_no}, Bank: {bank_code}, Account: {v_account}, Expire: {expire}")

        # Store ATM payment info / 存儲 ATM 取號資訊
        if order_no not in transactions:
            transactions[order_no] = {
                "status": "waiting_payment",
                "order_no": order_no,
                "payment_type": payment_type,
                "amount": amount,
                "timestamp": datetime.now().isoformat(),
                "bank_code": bank_code,
                "v_account": v_account,
                "expire_date": expire
            }

    elif rtn_code == "10100073":
        # CVS/BARCODE code generated / 超商取號成功
        if "Barcode1" in data:
            barcode1 = data.get("Barcode1", "")
            barcode2 = data.get("Barcode2", "")
            barcode3 = data.get("Barcode3", "")
            logger.info(f"[BARCODE] 取號成功 - Order: {order_no}, Codes: {barcode1} | {barcode2} | {barcode3}")

            # Store barcode payment info / 存儲超商條碼資訊
            if order_no not in transactions:
                transactions[order_no] = {
                    "status": "waiting_payment",
                    "order_no": order_no,
                    "payment_type": "BARCODE",
                    "amount": amount,
                    "timestamp": datetime.now().isoformat(),
                    "barcode1": barcode1,
                    "barcode2": barcode2,
                    "barcode3": barcode3
                }
        else:
            payment_no = data.get("PaymentNo", "")
            expire = data.get("ExpireDate", "")
            logger.info(f"[CVS] 取號成功 - Order: {order_no}, PaymentNo: {payment_no}, Expire: {expire}")

            # Store CVS payment info / 存儲超商代碼資訊
            if order_no not in transactions:
                transactions[order_no] = {
                    "status": "waiting_payment",
                    "order_no": order_no,
                    "payment_type": "CVS",
                    "amount": amount,
                    "timestamp": datetime.now().isoformat(),
                    "payment_no": payment_no,
                    "expire_date": expire
                }

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
    global success_count, failed_count

    form = await request.form()
    data = dict(form)

    request_count["/period-notify"] += 1

    if not verify_check_mac_value(data):
        logger.error("CheckMacValue verification failed for period-notify")
        return PlainTextResponse("0|CheckMacValue Error")

    rtn_code = data.get("RtnCode", "")
    order_no = data.get("MerchantTradeNo", "")
    total_times = data.get("TotalSuccessTimes", "")
    total_amount = data.get("TotalSuccessAmount", "")
    period_no = data.get("PeriodNo", "")

    if rtn_code == "1":
        logger.info(f"[RECURRING OK] 扣款成功 - Order: {order_no}, Period: {period_no}, Total times: {total_times}, Total: NT${total_amount}")
        success_count += 1
    else:
        rtn_msg = data.get("RtnMsg", "")
        logger.error(f"[RECURRING FAIL] 扣款失敗 - Order: {order_no}, Period: {period_no}, Msg: {rtn_msg}")
        failed_count += 1

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
    request_count["/query"] += 1
    logger.info(f"Querying trade info | 查詢交易 - Order: {order_no}")

    import httpx

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "TimeStamp": str(int(time.time())),
    }
    params["CheckMacValue"] = generate_check_mac_value(params)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(QUERY_TRADE_URL, data=params)
            return PlainTextResponse(resp.text)
    except Exception as e:
        logger.error(f"Query trade failed | 查詢失敗: {str(e)}")
        return PlainTextResponse(f"Error: {str(e)}")


# ══════════════════════════════════════════════
# API 3: QueryCreditCardPeriodInfo 查詢定期定額
# ══════════════════════════════════════════════

@app.get("/query-recurring/{order_no}")
async def query_recurring(order_no: str):
    """Query recurring payment info. 查詢定期定額訂單資訊。
    Returns ExecStatus: 0=已停用, 1=執行中, 2=已完成"""
    request_count["/query-recurring"] += 1
    logger.info(f"Querying recurring payment | 查詢定期定額 - Order: {order_no}")

    import httpx

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "TimeStamp": str(int(time.time())),
    }
    params["CheckMacValue"] = generate_check_mac_value(params)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(QUERY_RECURRING_URL, data=params)
            return PlainTextResponse(resp.text)
    except Exception as e:
        logger.error(f"Query recurring failed | 查詢定期定額失敗: {str(e)}")
        return PlainTextResponse(f"Error: {str(e)}")


# ══════════════════════════════════════════════
# API 4: CreditCardPeriodAction 定期定額停用
# ══════════════════════════════════════════════

@app.post("/cancel-recurring/{order_no}")
async def cancel_recurring(order_no: str):
    """Cancel recurring payment. WARNING: Irreversible!
    停用定期定額。警告：停用後無法重新啟用！"""
    request_count["/cancel-recurring"] += 1
    logger.warning(f"Cancelling recurring payment | 停用定期定額 - Order: {order_no}")

    import httpx

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "Action": "Cancel",
    }
    params["CheckMacValue"] = generate_check_mac_value(params)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(RECURRING_ACTION_URL, data=params)
            return PlainTextResponse(resp.text)
    except Exception as e:
        logger.error(f"Cancel recurring failed | 停用定期定額失敗: {str(e)}")
        return PlainTextResponse(f"Error: {str(e)}")


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
    request_count["/do-action"] += 1
    action_name = {"C": "Capture/關帳", "R": "Refund/退刷", "E": "Cancel/取消", "N": "Abandon/放棄"}.get(action, action)
    logger.info(f"Executing do-action | 執行信用卡操作 - Order: {order_no}, Action: {action_name}, Amount: {amount}")

    import httpx

    params = {
        "MerchantID": MERCHANT_ID,
        "MerchantTradeNo": order_no,
        "TradeNo": trade_no,
        "Action": action,
        "TotalAmount": str(amount),
    }
    params["CheckMacValue"] = generate_check_mac_value(params)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(DO_ACTION_URL, data=params)
            return PlainTextResponse(resp.text)
    except Exception as e:
        logger.error(f"DoAction failed | 信用卡操作失敗: {str(e)}")
        return PlainTextResponse(f"Error: {str(e)}")


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
    request_count["/query-credit-detail"] += 1
    logger.info(f"Querying credit detail | 查詢信用卡明細 - RefundID: {credit_refund_id}, Amount: {credit_amount}")

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

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(QUERY_CREDIT_DETAIL_URL, data=params)
            return PlainTextResponse(resp.text)
    except Exception as e:
        logger.error(f"Query credit detail failed | 查詢信用卡明細失敗: {str(e)}")
        return PlainTextResponse(f"Error: {str(e)}")


# ══════════════════════════════════════════════
# Health Check & Monitoring 健康檢查與監控
# ══════════════════════════════════════════════

@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Health check with OMG API connectivity test.
    健康檢查 - 驗證 OMG API 連線狀態。"""
    import httpx

    try:
        logger.info("Health check initiated | 開始健康檢查")

        # Quick connectivity test - try to resolve the payment domain / 快速連線測試
        async with httpx.AsyncClient(timeout=5.0) as client:
            # We don't send a real request, just check if the host is reachable / 測試域名可達性
            # This is a simple connectivity check / 簡單的連線檢查
            try:
                resp = await client.get(f"{PAYMENT_BASE}/", follow_redirects=False)
                api_status = "connected"
            except Exception as e:
                api_status = "unreachable"
                logger.warning(f"API connectivity test failed: {str(e)}")

        uptime_seconds = int(time.time() - start_time)
        uptime_formatted = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"

        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": "production" if IS_PRODUCTION else "staging",
            "merchant_id": MERCHANT_ID,
            "api_status": api_status,
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": uptime_formatted,
            "transactions_processed": success_count + failed_count,
            "success_rate": f"{(success_count / max(success_count + failed_count, 1) * 100):.1f}%"
        }

        logger.info(f"Health check passed | 健康檢查通過 - {health_data}")
        return health_data

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/metrics", response_class=JSONResponse)
async def metrics():
    """Basic transaction metrics. 基本交易指標。"""
    total_transactions = success_count + failed_count
    success_rate = (success_count / max(total_transactions, 1)) * 100
    uptime_seconds = int(time.time() - start_time)

    # Calculate daily metrics / 計算每日指標
    today = datetime.now().date()
    today_transactions = {k: v for k, v in transactions.items()
                         if datetime.fromisoformat(v.get('timestamp', '')).date() == today}
    today_amount = sum(int(v.get('amount', 0)) for v in today_transactions.values())

    metrics_data = {
        "timestamp": datetime.now().isoformat(),
        "total_transactions": total_transactions,
        "successful": success_count,
        "failed": failed_count,
        "success_rate_percent": round(success_rate, 2),
        "uptime_seconds": uptime_seconds,
        "daily_transactions": len(today_transactions),
        "daily_amount_ntd": today_amount,
        "endpoint_requests": dict(request_count)
    }

    logger.info(f"Metrics requested | 指標請求 - Total: {total_transactions}, Success Rate: {success_rate:.1f}%")
    return metrics_data


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Admin dashboard with transaction list and metrics.
    管理員儀表板 - 交易清單與統計。"""
    logger.info("Admin dashboard accessed | 管理員儀表板被存取")

    total = success_count + failed_count
    success_rate = (success_count / max(total, 1)) * 100
    uptime_seconds = int(time.time() - start_time)
    uptime_hours = uptime_seconds // 3600
    uptime_mins = (uptime_seconds % 3600) // 60

    # Build transaction table rows / 建立交易列表
    transaction_rows = ""
    if transactions:
        # Sort by timestamp descending / 按時間戳降序排列
        sorted_txns = sorted(
            transactions.items(),
            key=lambda x: x[1].get('timestamp', ''),
            reverse=True
        )[:50]  # Show last 50 transactions / 顯示最近 50 筆

        for order_no, txn in sorted_txns:
            status_color = "#10b981" if txn.get('status') == 'success' else "#ef4444"
            status_text = "✓ Success" if txn.get('status') == 'success' else "✗ Failed"
            timestamp = txn.get('timestamp', 'N/A')
            amount = txn.get('amount', 'N/A')
            payment_type = txn.get('payment_type', 'N/A')

            transaction_rows += f"""
            <tr>
                <td style="font-size:12px;">{order_no}</td>
                <td>{payment_type}</td>
                <td style="text-align:right;">NT${amount}</td>
                <td style="color:{status_color};font-weight:bold;">{status_text}</td>
                <td style="font-size:11px;color:#666;">{timestamp}</td>
            </tr>
            """
    else:
        transaction_rows = '<tr><td colspan="5" style="text-align:center;color:#999;">No transactions yet | 尚無交易記錄</td></tr>'

    # Calculate daily total / 計算每日總額
    today = datetime.now().date()
    today_transactions = {k: v for k, v in transactions.items()
                         if datetime.fromisoformat(v.get('timestamp', '')).date() == today}
    today_amount = sum(int(v.get('amount', 0)) for v in today_transactions.values())

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OMG Payment Admin | 管理員儀表板</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                background: white;
                padding: 20px 30px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                color: #333;
                margin-bottom: 10px;
            }}
            .header p {{
                color: #666;
                font-size: 14px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .stat-card h3 {{
                color: #999;
                font-size: 12px;
                text-transform: uppercase;
                margin-bottom: 10px;
                font-weight: 500;
            }}
            .stat-value {{
                font-size: 28px;
                font-weight: bold;
                color: #333;
            }}
            .stat-sub {{
                color: #999;
                font-size: 12px;
                margin-top: 5px;
            }}
            .transactions-panel {{
                background: white;
                padding: 20px 30px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .transactions-panel h2 {{
                color: #333;
                margin-bottom: 15px;
                font-size: 18px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
            }}
            th {{
                background: #f8f9fa;
                padding: 12px;
                text-align: left;
                color: #666;
                font-weight: 600;
                border-bottom: 1px solid #e9ecef;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #e9ecef;
            }}
            tr:hover {{
                background: #f8f9fa;
            }}
            .action-buttons {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 20px;
            }}
            button {{
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                transition: background 0.3s;
            }}
            button:hover {{
                background: #764ba2;
            }}
            button.secondary {{
                background: #6c757d;
            }}
            button.secondary:hover {{
                background: #5a6268;
            }}
            button.danger {{
                background: #ef4444;
            }}
            button.danger:hover {{
                background: #dc2626;
            }}
            .footer {{
                text-align: center;
                color: white;
                font-size: 12px;
                margin-top: 20px;
            }}
            .badge {{
                display: inline-block;
                padding: 3px 8px;
                background: #e9ecef;
                border-radius: 4px;
                font-size: 11px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>OMG Payment Admin Dashboard</h1>
                <p>管理員儀表板 | Real-time transaction monitoring | 實時交易監控</p>
                <p style="margin-top:10px;"><span class="badge">{{'PRODUCTION' if IS_PRODUCTION else 'STAGING'}}</span> Merchant ID: {MERCHANT_ID}</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Transactions | 總交易</h3>
                    <div class="stat-value">{total}</div>
                    <div class="stat-sub">Since: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                <div class="stat-card">
                    <h3>Successful | 成功</h3>
                    <div class="stat-value" style="color:#10b981;">{success_count}</div>
                    <div class="stat-sub">Success Rate: {success_rate:.1f}%</div>
                </div>
                <div class="stat-card">
                    <h3>Failed | 失敗</h3>
                    <div class="stat-value" style="color:#ef4444;">{failed_count}</div>
                    <div class="stat-sub">Failure Rate: {100-success_rate:.1f}%</div>
                </div>
                <div class="stat-card">
                    <h3>Today's Total | 今日總額</h3>
                    <div class="stat-value" style="color:#667eea;">NT${today_amount}</div>
                    <div class="stat-sub">{len(today_transactions)} transactions | 筆交易</div>
                </div>
                <div class="stat-card">
                    <h3>Uptime | 運行時間</h3>
                    <div class="stat-value">{uptime_hours}h {uptime_mins}m</div>
                    <div class="stat-sub">Since: {datetime.fromtimestamp(start_time).strftime('%H:%M:%S')}</div>
                </div>
                <div class="stat-card">
                    <h3>Environment | 環境</h3>
                    <div class="stat-value" style="font-size:14px;">{'🟢 PRODUCTION' if IS_PRODUCTION else '🟡 STAGING'}</div>
                    <div class="stat-sub">{PAYMENT_BASE.split('/')[-1]}</div>
                </div>
            </div>

            <div class="transactions-panel">
                <h2>Recent Transactions | 最近交易 (最新 50 筆)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Order No | 訂單號</th>
                            <th>Payment Type | 付款方式</th>
                            <th style="text-align:right;">Amount | 金額</th>
                            <th>Status | 狀態</th>
                            <th>Timestamp | 時間</th>
                        </tr>
                    </thead>
                    <tbody>
                        {transaction_rows}
                    </tbody>
                </table>

                <div class="action-buttons">
                    <button onclick="location.href='/health'">Health Check | 健康檢查</button>
                    <button class="secondary" onclick="location.href='/metrics'">View Metrics | 檢視指標</button>
                    <button class="secondary" onclick="location.href='/'">Back to Home | 返回首頁</button>
                    <button class="secondary" onclick="location.reload()">Refresh | 刷新</button>
                </div>
            </div>

            <div class="footer">
                <p>OMG Payment Gateway Admin Dashboard | 歐買尬第三方支付管理員儀表板</p>
                <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 最後更新時間</p>
            </div>
        </div>
    </body>
    </html>
    """


# ══════════════════════════════════════════════
# Home Page with Test Links 首頁測試連結
# ══════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with all test links. 首頁：所有測試連結。"""
    request_count["/"] += 1
    logger.info("Home page accessed | 首頁被存取")

    return """
    <html>
    <head>
        <title>OMG Payment Test | OMG 金流測試</title>
        <style>
            body {
                max-width: 900px;
                margin: 40px auto;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 0 20px;
                color: #333;
            }
            h1 {
                color: #667eea;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }
            h2 {
                color: #555;
                margin-top: 30px;
                border-left: 4px solid #667eea;
                padding-left: 15px;
            }
            a {
                color: #667eea;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            .badge {
                display: inline-block;
                padding: 3px 10px;
                background: #667eea;
                color: white;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin-left: 10px;
            }
            .admin-link {
                background: #667eea;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                text-decoration: none;
                display: inline-block;
                margin: 20px 0;
                font-weight: bold;
            }
            .admin-link:hover {
                background: #764ba2;
                text-decoration: none;
            }
            table {
                border-collapse: collapse;
                margin: 20px 0;
            }
            td {
                border: 1px solid #ddd;
                padding: 8px 12px;
            }
            code {
                background: #f5f5f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #999;
                font-size: 12px;
            }
            ul {
                line-height: 1.8;
            }
            .env-note {
                background: #f0f7ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <h1>OMG Payment Gateway Test | OMG 金流測試</h1>
        <p>Company 公司: 茂為歐買尬數位科技股份有限公司 / MacroWell OMG Digital Entertainment Co., Ltd.</p>
        <p>Country 國家: Taiwan 台灣 | Official 官網: <a href="https://www.funpoint.com.tw/">funpoint.com.tw</a></p>

        <div class="admin-link" onclick="location.href='/admin'" style="cursor: pointer;">
            📊 Admin Dashboard | 管理員儀表板
        </div>

        <div class="env-note">
            <strong>Environment Configuration 環境設定:</strong><br>
            This integration supports .env configuration files | 支援 .env 環境變數配置<br>
            Available variables: OMG_MERCHANT_ID, OMG_HASH_KEY, OMG_HASH_IV, OMG_PRODUCTION, BASE_URL
        </div>

        <hr>

        <h2>Create Order 產生訂單 (AioCheckOut/V5)</h2>
        <ul>
            <li><a href="/pay">💳 Credit Card 信用卡一次付款 (NT$100)</a></li>
            <li><a href="/pay-installment">📅 Credit Card Installment 信用卡分期 (NT$6,000, 3/6/12期)</a></li>
            <li><a href="/pay-recurring">🔄 Recurring 定期定額 (NT$299/月 x 12期)</a></li>
            <li><a href="/pay-atm">🏧 ATM 虛擬帳號 (NT$500)</a></li>
            <li><a href="/pay-cvs">🛒 CVS 超商代碼 (NT$300)</a></li>
            <li><a href="/pay-barcode">📱 BARCODE 超商條碼 (NT$200)</a></li>
            <li><a href="/pay-all">🎯 ALL 所有付款方式 (NT$100)</a></li>
        </ul>

        <h2>Monitoring & Health 監控與狀態</h2>
        <ul>
            <li><a href="/health">🟢 Health Check 健康檢查</a> - API connectivity and system status | API 連線與系統狀態</li>
            <li><a href="/metrics">📈 Metrics 指標</a> - Transaction statistics and performance | 交易統計與效能指標</li>
            <li><a href="/admin">📊 Admin Dashboard 管理員儀表板</a> - Real-time transaction monitoring | 實時交易監控</li>
        </ul>

        <h2>Query APIs 查詢 API</h2>
        <ul>
            <li><a href="/query/TEST_ORDER_NO">QueryTradeInfo/V5 查詢訂單</a> (replace TEST_ORDER_NO with actual order)</li>
            <li><a href="/query-recurring/TEST_ORDER_NO">QueryCreditCardPeriodInfo 查詢定期定額</a></li>
            <li>POST /cancel-recurring/{order_no} - CreditCardPeriodAction 定期定額停用 (WARNING: Irreversible!)</li>
            <li>POST /do-action - DoAction 信用卡請退款 (C=Capture, R=Refund, E=Cancel, N=Abandon)</li>
            <li><a href="/query-credit-detail?credit_refund_id=TEST&credit_amount=100">QueryTrade/V2 查詢信用卡明細</a></li>
        </ul>

        <h2>Test Credentials 測試帳號</h2>
        <table>
            <tr><td><strong>MerchantID</strong></td><td><code>1000031</code></td></tr>
            <tr><td><strong>HashKey</strong></td><td><code>265fIDjIvesceXWM</code></td></tr>
            <tr><td><strong>HashIV</strong></td><td><code>pOOvhGd1V2pJbjfX</code></td></tr>
            <tr><td><strong>Test Card 測試卡</strong></td><td><code>4311-9522-2222-2222</code> (CVV: 222, any future date)</td></tr>
        </table>

        <h2>Environment Variables 環境變數</h2>
        <p>Create a <code>.env</code> file in the same directory as this script | 在相同目錄建立 .env 檔案:</p>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto;">
OMG_MERCHANT_ID=1000031
OMG_HASH_KEY=265fIDjIvesceXWM
OMG_HASH_IV=pOOvhGd1V2pJbjfX
OMG_PRODUCTION=false
BASE_URL=https://your-domain.com
        </pre>

        <div class="footer">
            <p><strong>Author 作者:</strong> Mitchell Chen | <strong>Generated with:</strong> Claude (Anthropic) AI assistance</p>
            <p>一切以官方文件為主，如有問題請洽 <a href="https://www.funpoint.com.tw/">OMG 官網</a></p>
            <p>Features 功能: All 6 API endpoints + Health check + Metrics + Admin dashboard + .env support + Logging | 全 6 個 API + 健康檢查 + 指標 + 管理員儀表板 + 環境變數 + 日誌</p>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
