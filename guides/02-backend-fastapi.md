# Guide 02 — FastAPI 後端骨架

本指南說明以 FastAPI 建置歐買尬金流後端的標準結構。所有指令均可直接複製執行。

## 為何預設使用 FastAPI

- **上手快**：單檔即可啟動服務，無需額外設定
- **依賴少**：`fastapi` 與 `uvicorn` 兩個套件即可運作
- **文件自動生成**：啟動後可於 `/docs` 自動取得互動式 API 文件
- **跨平台**：macOS、Windows、Linux 均可使用相同指令

若您偏好 Node.js 或 PHP，請參考 `guides/03-backend-nodejs.md` 或 `guides/04-backend-php.md`。

## 專案結構

```
backend/
├── main.py              FastAPI 應用程式入口
├── omg_client.py        歐買尬 API 客戶端（create_order / query_order / refund）
├── mac_value.py         SHA256 CheckMacValue 計算與驗證
├── idempotency.py       Race-safe webhook 冪等性處理
├── admin.py             admin endpoint（訂單查詢、退款、健康摘要）
├── models.py            資料庫 schema 與 ORM（SQLAlchemy + SQLite 預設）
├── settings.py          環境變數讀取
├── .env.example         環境變數範本
└── requirements.txt
```

完整檔案已提供於 `templates/backend-fastapi/`，可直接複製使用。

## 啟動方式

```bash
cd templates/backend-fastapi
pip install -r requirements.txt
cp .env.example .env
# 編輯 .env 填入金鑰
python -m uvicorn main:app --reload --port 8000
```

啟動後開啟瀏覽器進入 `http://127.0.0.1:8000/docs`，即可看到所有 API 之互動式文件。

## 核心 endpoint 列表

| Method | Path | 用途 | 認證 |
|---|---|---|---|
| `GET` | `/health` | 服務健康檢查 | 無 |
| `POST` | `/webhook` | 接收歐買尬 callback | MAC 驗證 |
| `POST` | `/api/checkout/create-order` | 建立訂單 | 可選擇加上 app token |
| `GET` | `/api/admin/orders` | 訂單列表 | admin token |
| `GET` | `/api/admin/orders/{order_no}` | 單筆訂單明細 | admin token |
| `GET` | `/api/admin/orders/today` | 今日訂單摘要 | admin token |
| `POST` | `/api/admin/refund` | 發起退款 | admin token |
| `GET` | `/api/admin/payment/health-summary` | 金流健康狀態 | admin token |

## settings.py 範例

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OMG_MERCHANT_ID: str
    OMG_HASH_KEY: str
    OMG_HASH_IV: str
    OMG_API_HOST_STAGE: str
    OMG_API_HOST_PROD: str = ""
    DATABASE_URL: str = "sqlite:///./omg.db"
    ADMIN_TOKEN: str
    ENVIRONMENT: str = "stage"  # stage | prod

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

此類別負責讀取 `.env` 並提供型別安全之存取。任何寫入敏感金鑰之行為應集中於此檔案，其他模組僅從 `settings` 讀取。

## models.py 範例

預設採用 SQLite，無需額外安裝。若需切換至 PostgreSQL，只需修改 `.env` 中之 `DATABASE_URL`。

```python
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True)
    order_no = Column(String(40), unique=True, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    payment_method = Column(String(20))
    provider = Column(String(20), nullable=False, default="omg")
    trade_no = Column(String(40))
    idempotency_key = Column(String(128), unique=True, index=True)
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_status_created", "status", "created_at"),
    )

class CallbackLog(Base):
    __tablename__ = "callback_logs"

    id = Column(Integer, primary_key=True)
    order_no = Column(String(40), nullable=False, index=True)
    payload = Column(String)                # JSON text
    mac_valid = Column(Boolean, nullable=False)
    processed = Column(String(20), nullable=False)  # absorbed | applied | early-dup
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

## main.py 範例

```python
from fastapi import FastAPI
from .settings import settings
from .models import Base
from sqlalchemy import create_engine
from . import webhook, admin, checkout

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OMG Payment Backend",
    version="1.0.0",
    description="歐買尬金流整合後端（社群版）",
)

app.include_router(webhook.router)
app.include_router(checkout.router, prefix="/api/checkout")
app.include_router(admin.router, prefix="/api/admin")

@app.get("/health")
async def health():
    return {"ok": True, "env": settings.ENVIRONMENT}
```

## 模組切分原則

1. **業務邏輯與 API endpoint 分離**：`omg_client.py` 負責與歐買尬 API 對話，不含 HTTP 框架相依；`webhook.py`、`admin.py` 僅負責 HTTP 路由
2. **敏感操作集中於 admin.py**：退款、訂單修改等操作必須透過 admin token 驗證
3. **冪等性單獨模組化**：`idempotency.py` 提供 `compute_idempotency_key()` 與 `handle_callback()`，由 webhook 路由呼叫
4. **金鑰僅從 settings 讀取**：任何模組都不得直接存取 `os.environ`

## 本機測試

專案啟動後，可透過下列方式進行本機測試：

1. 開啟 `http://127.0.0.1:8000/docs` 使用 Swagger UI 手動測試各 endpoint
2. 使用 `curl` 呼叫：
   ```bash
   curl http://127.0.0.1:8000/health
   ```
3. 使用 `templates/omg-test-console/` 之測試儀表板進行完整鏈路驗證（詳見 `guides/06-test-dashboard.md`）

## 生產環境部署建議

若需部署至正式環境，建議：

1. **進程管理**：使用 `uvicorn` 搭配 `gunicorn` 或容器化（Docker）
2. **反向代理**：於前端加上 nginx / Caddy 以處理 HTTPS 與靜態檔案
3. **環境變數管理**：正式環境之 `.env` 不得納入版本控制
4. **資料庫**：正式環境建議切換至 PostgreSQL 或 MySQL，不使用 SQLite
5. **監控**：啟用 `guides/07-prod-dashboard.md` 定義之唯讀探測儀表板

## 安全提醒

1. `ADMIN_TOKEN` 應使用加密隨機字串產生，並僅寫入 `.env`
2. 所有 admin endpoint 必須透過 `Authorization: Bearer {token}` 驗證
3. Webhook endpoint 必須驗證 CheckMacValue，未通過者不得寫入資料庫
4. 日誌不得記錄 HashKey、HashIV 或完整信用卡號
