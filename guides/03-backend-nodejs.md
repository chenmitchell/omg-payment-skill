# Guide 03 — Node.js (Express) 後端骨架

本指南說明以 Node.js + Express 建置歐買尬金流後端的標準結構。若您偏好 Python，請參考 `guides/02-backend-fastapi.md`。

> [!NOTE]
> 本 Skill 預設使用 FastAPI。Node.js 版本與 FastAPI 版本之架構、API endpoint、冪等性規則完全相同，使用者可依團隊技術棧擇一採用。

---

## 為何提供 Node.js 版本

Express 於前端團隊、JavaScript 生態系中使用率高。若您的網站使用 Next.js、Nuxt、Remix 等框架，整合 Express 後端可共用相同語言與開發工具鏈。

---

## 專案結構

```
backend/
├── package.json
├── .env.example
├── src/
│   ├── index.ts              Express 應用程式入口
│   ├── omgClient.ts          歐買尬 API 客戶端
│   ├── macValue.ts           SHA256 CheckMacValue 計算
│   ├── idempotency.ts        Race-safe webhook 冪等性
│   ├── admin.ts              admin endpoints
│   ├── webhook.ts            webhook 路由
│   ├── models.ts             資料庫 schema（Prisma 或 TypeORM）
│   └── config.ts             環境變數讀取
└── prisma/                   （若採用 Prisma）
    └── schema.prisma
```

---

## 啟動方式

```bash
cd templates/backend-nodejs
npm install
cp .env.example .env
# 編輯 .env 填入 OMG 金鑰
npm run dev
```

預設於 `http://127.0.0.1:8000` 啟動。

---

## 核心 endpoint 列表

與 FastAPI 版本完全相同：

| Method | Path | 用途 |
|---|---|---|
| `GET` | `/health` | 服務健康檢查 |
| `POST` | `/webhook` | 接收歐買尬 callback |
| `POST` | `/api/checkout/create-order` | 建立訂單 |
| `GET` | `/api/admin/orders` | 訂單列表 |
| `GET` | `/api/admin/orders/{order_no}` | 單筆訂單明細 |
| `GET` | `/api/admin/orders/today` | 今日訂單摘要 |
| `POST` | `/api/admin/refund` | 發起退款 |
| `GET` | `/api/admin/payment/health-summary` | 金流健康狀態 |

---

## CheckMacValue 參考實作（TypeScript）

```typescript
import crypto from 'crypto';

function dotnetUrlEncode(s: string): string {
  let encoded = encodeURIComponent(s).replace(/%20/g, '+').toLowerCase();
  const replacements: Record<string, string> = {
    '%2d': '-', '%5f': '_', '%2e': '.',
    '%21': '!', '%2a': '*', '%28': '(', '%29': ')',
  };
  for (const [k, v] of Object.entries(replacements)) {
    encoded = encoded.split(k).join(v);
  }
  return encoded;
}

export function computeCheckMac(
  params: Record<string, string>,
  hashKey: string,
  hashIv: string,
): string {
  const filtered = Object.fromEntries(
    Object.entries(params).filter(([k]) => k !== 'CheckMacValue'),
  );
  const sortedKeys = Object.keys(filtered).sort();
  const pairs = sortedKeys.map((k) => `${k}=${filtered[k]}`);
  const raw = `HashKey=${hashKey}&${pairs.join('&')}&HashIV=${hashIv}`;
  return crypto
    .createHash('sha256')
    .update(dotnetUrlEncode(raw), 'utf8')
    .digest('hex')
    .toUpperCase();
}
```

本實作已通過 `test-vectors/check-mac-value.json` 中所有向量。可使用 `node test-vectors/verify-node.js` 驗證。

---

## Webhook 冪等性（Prisma 版本）

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function handleCallback(
  orderNo: string,
  idempotencyKey: string,
  payload: any,
): Promise<'applied' | 'absorbed'> {
  try {
    // 嘗試插入新紀錄；若 idempotency_key 重複，unique constraint 會擋下
    await prisma.paymentTransaction.update({
      where: { orderNo, idempotencyKey: null },
      data: {
        status: 'paid',
        idempotencyKey,
        paidAt: new Date(),
      },
    });
    return 'applied';
  } catch (e: any) {
    // Prisma P2025 = record not found（已處理過）
    // Prisma P2002 = unique constraint violation
    if (e.code === 'P2025' || e.code === 'P2002') {
      return 'absorbed';
    }
    throw e;
  }
}
```

完整 race-safe 實作請參考 `guides/05-webhook-idempotency.md`。

---

## 與 FastAPI 版本的差異

1. **非同步模型**：Node.js 天然非同步，無需 `async def` / `await` 標註
2. **ORM**：Node.js 生態可選 Prisma、TypeORM、Sequelize；本 Skill 範例使用 Prisma
3. **設定檔**：使用 `dotenv` 套件讀取 `.env`；TypeScript 使用 `zod` 做型別驗證
4. **測試**：使用 Jest 或 Vitest；測試向量與 FastAPI 版本共用 `test-vectors/check-mac-value.json`

---

## 安全提醒

1. `ADMIN_TOKEN` 應使用 `crypto.randomBytes(16).toString('hex')` 產生
2. 所有 admin endpoint 必須透過 middleware 驗證 `Authorization: Bearer {token}`
3. Webhook endpoint 必須驗證 CheckMacValue
4. 日誌不得記錄 HashKey、HashIV 或完整信用卡號

---

## 官方資源

若本指南之內容與歐買尬官方文件不一致，以官方為準：

- 官方 AI 金流 Skill：<https://github.com/omgtwhub/>
- 歐買尬商家後台
