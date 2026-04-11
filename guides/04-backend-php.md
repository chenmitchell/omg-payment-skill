# Guide 04 — PHP (Laravel) 後端骨架

本指南說明以 Laravel 建置歐買尬金流後端的標準結構。若您偏好 Python 或 Node.js，請參考 `guides/02-backend-fastapi.md` 或 `guides/03-backend-nodejs.md`。

> [!NOTE]
> 本 Skill 預設使用 FastAPI。Laravel 版本與 FastAPI 版本之架構、API endpoint、冪等性規則完全相同，使用者可依團隊技術棧擇一採用。

---

## 為何提供 Laravel 版本

Laravel 於台灣中小企業與電商系統中使用率高，且 PHP 與歐買尬官方 SDK 有較直接的對應。若您的網站已採用 Laravel，整合本指南可共用既有的 Eloquent ORM、middleware、queue 等基礎設施。

---

## 專案結構

```
backend/
├── composer.json
├── .env.example
├── app/
│   ├── Http/
│   │   ├── Controllers/
│   │   │   ├── WebhookController.php
│   │   │   ├── CheckoutController.php
│   │   │   └── Admin/
│   │   │       ├── OrderController.php
│   │   │       └── RefundController.php
│   │   └── Middleware/
│   │       └── AdminTokenAuth.php
│   ├── Services/
│   │   ├── OmgClient.php
│   │   ├── MacValue.php
│   │   └── Idempotency.php
│   └── Models/
│       ├── PaymentTransaction.php
│       └── CallbackLog.php
├── database/migrations/
│   └── 2026_01_01_create_payment_tables.php
└── routes/
    └── api.php
```

---

## 啟動方式

```bash
cd templates/backend-laravel
composer install
cp .env.example .env
php artisan key:generate
# 編輯 .env 填入 OMG 金鑰與資料庫連線
php artisan migrate
php artisan serve --port=8000
```

預設於 `http://127.0.0.1:8000` 啟動。

---

## 核心 endpoint 列表

與 FastAPI / Node.js 版本完全相同：

| Method | Path | Controller |
|---|---|---|
| `GET` | `/health` | `HealthController@index` |
| `POST` | `/webhook` | `WebhookController@receive` |
| `POST` | `/api/checkout/create-order` | `CheckoutController@createOrder` |
| `GET` | `/api/admin/orders` | `Admin\OrderController@index` |
| `GET` | `/api/admin/orders/{order_no}` | `Admin\OrderController@show` |
| `GET` | `/api/admin/orders/today` | `Admin\OrderController@today` |
| `POST` | `/api/admin/refund` | `Admin\RefundController@store` |
| `GET` | `/api/admin/payment/health-summary` | `Admin\HealthController@summary` |

---

## CheckMacValue 參考實作（PHP）

```php
<?php

namespace App\Services;

class MacValue
{
    public static function compute(array $params, string $hashKey, string $hashIv): string
    {
        unset($params['CheckMacValue']);
        ksort($params);

        $pairs = [];
        foreach ($params as $k => $v) {
            $pairs[] = "$k=$v";
        }
        $raw = "HashKey=$hashKey&" . implode('&', $pairs) . "&HashIV=$hashIv";

        return strtoupper(hash('sha256', self::dotnetUrlEncode($raw)));
    }

    public static function verify(array $params, string $hashKey, string $hashIv): bool
    {
        $received = $params['CheckMacValue'] ?? '';
        $expected = self::compute($params, $hashKey, $hashIv);
        return strtoupper($received) === $expected;
    }

    private static function dotnetUrlEncode(string $s): string
    {
        $encoded = strtolower(urlencode($s));
        $replacements = [
            '%2d' => '-', '%5f' => '_', '%2e' => '.',
            '%21' => '!', '%2a' => '*', '%28' => '(', '%29' => ')',
        ];
        return strtr($encoded, $replacements);
    }
}
```

本實作邏輯與 Python / Node.js 版本完全相同，均應通過 `test-vectors/check-mac-value.json` 中所有向量。

---

## Webhook 冪等性（Eloquent + Database transaction）

```php
<?php

namespace App\Services;

use App\Models\PaymentTransaction;
use Illuminate\Support\Facades\DB;

class Idempotency
{
    /**
     * 以 SELECT ... FOR UPDATE 搭配 idempotency_key unique index 處理 webhook 重送。
     *
     * @return string 'applied' | 'absorbed' | 'early-dup'
     */
    public static function handleCallback(string $orderNo, string $idempotencyKey, array $payload): string
    {
        return DB::transaction(function () use ($orderNo, $idempotencyKey, $payload) {
            $tx = PaymentTransaction::where('order_no', $orderNo)
                ->lockForUpdate()
                ->first();

            if (!$tx) {
                return 'early-dup'; // 訂單尚未建立，屬早到或錯送
            }

            if ($tx->idempotency_key === $idempotencyKey) {
                return 'absorbed'; // 已處理過同一事件
            }

            if ($tx->status === 'paid') {
                return 'absorbed'; // 已付款，忽略重送
            }

            $tx->status = 'paid';
            $tx->idempotency_key = $idempotencyKey;
            $tx->paid_at = now();
            $tx->save();

            return 'applied';
        });
    }
}
```

完整 race-safe 實作與 11 項單元測試請參考 `guides/05-webhook-idempotency.md`。

---

## Migration 範例

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('payment_transactions', function (Blueprint $table) {
            $table->id();
            $table->string('order_no', 40)->unique();
            $table->integer('amount');
            $table->string('status', 20)->default('pending');
            $table->string('payment_method', 20)->nullable();
            $table->string('provider', 20)->default('omg');
            $table->string('trade_no', 40)->nullable();
            $table->string('idempotency_key', 128)->nullable()->unique();
            $table->timestamp('paid_at')->nullable();
            $table->timestamps();
            $table->index(['status', 'created_at']);
        });

        Schema::create('callback_logs', function (Blueprint $table) {
            $table->id();
            $table->string('order_no', 40)->index();
            $table->json('payload');
            $table->boolean('mac_valid');
            $table->string('processed', 20); // absorbed | applied | early-dup
            $table->timestamp('received_at')->useCurrent();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('callback_logs');
        Schema::dropIfExists('payment_transactions');
    }
};
```

---

## Admin token middleware

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class AdminTokenAuth
{
    public function handle(Request $request, Closure $next)
    {
        $token = $request->bearerToken() ?? $request->header('X-Admin-Token');
        if ($token !== config('services.omg.admin_token')) {
            abort(401, 'unauthorized');
        }
        return $next($request);
    }
}
```

於 `routes/api.php` 套用：

```php
Route::middleware('admin.token')->prefix('api/admin')->group(function () {
    Route::get('orders', [Admin\OrderController::class, 'index']);
    Route::get('orders/today', [Admin\OrderController::class, 'today']);
    Route::get('orders/{orderNo}', [Admin\OrderController::class, 'show']);
    Route::post('refund', [Admin\RefundController::class, 'store']);
    Route::get('payment/health-summary', [Admin\HealthController::class, 'summary']);
});
```

---

## 與其他版本的差異

1. **ORM**：Laravel 使用 Eloquent；FastAPI 使用 SQLAlchemy；Node.js 使用 Prisma
2. **Middleware**：Laravel 使用 class-based middleware；FastAPI 使用 dependency injection
3. **Queue**：Laravel 內建 queue 系統，可用於 webhook 重試；其他版本需自行整合（Celery、BullMQ）
4. **設定檔**：Laravel 使用 `config/services.php` 而非直接讀取 `.env`

---

## 安全提醒

1. `ADMIN_TOKEN` 應以 `Str::random(32)` 產生，並僅寫入 `.env`
2. 所有 admin endpoint 必須透過 `admin.token` middleware 驗證
3. Webhook endpoint 必須驗證 CheckMacValue，不通過者不得寫入資料庫
4. 日誌（包含 Laravel 之 `storage/logs/laravel.log`）不得記錄 HashKey、HashIV 或完整信用卡號
5. 於 `bootstrap/app.php` 之 exception handler 中排除敏感欄位

---

## 官方資源

若本指南之內容與歐買尬官方文件不一致，以官方為準：

- 官方 AI 金流 Skill：<https://github.com/omgtwhub/>
- 歐買尬商家後台
