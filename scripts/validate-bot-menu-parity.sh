#!/usr/bin/env bash
# validate-bot-menu-parity.sh
# 檢查 admin endpoint 與 Telegram/Discord bot 選單之 API parity。
#
# 規則：
#   guides/02-backend-fastapi.md 中定義之 admin endpoint 列表（/api/admin/orders,
#   /api/admin/orders/{order_no}, /api/admin/orders/today, /api/admin/refund,
#   /api/admin/summary/today, /api/admin/health）必須於下列任一檔案中被引用：
#     - templates/telegram-bot/bot.py
#     - templates/discord-bot/bot.py
#   否則代表某個 admin API 沒有對應之 bot 操作，違反本 repo 的 API-Menu 一致性原則。
#
# 退出碼：0 = 全部 parity；1 = 任一缺漏
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "== Bot menu API parity 檢查 =="

# 從 guides/02-backend-fastapi.md 的 endpoint 表格抓出 admin endpoints
# 預期樣式： | `GET` | `/api/admin/orders` | ... |
if [[ ! -f "guides/02-backend-fastapi.md" ]]; then
    echo "SKIP: guides/02-backend-fastapi.md 不存在"
    exit 0
fi

ENDPOINTS="$(grep -oE '/api/admin/[a-zA-Z0-9/_{}-]+' guides/02-backend-fastapi.md | sort -u)"

if [[ -z "$ENDPOINTS" ]]; then
    echo "WARN: guides/02-backend-fastapi.md 中未偵測到 /api/admin/ endpoint"
    exit 0
fi

TG_BOT="templates/telegram-bot/bot.py"
DC_BOT="templates/discord-bot/bot.py"

FAIL=0
TOTAL=0
PASSED=0

while IFS= read -r ep; do
    TOTAL=$((TOTAL + 1))
    # 將路徑參數 {order_no} 轉為正則可匹配樣式
    pattern="$(echo "$ep" | sed 's/{[^}]*}/[^"]*/g')"

    FOUND_TG=0
    FOUND_DC=0

    if [[ -f "$TG_BOT" ]] && grep -qE "$pattern" "$TG_BOT"; then
        FOUND_TG=1
    fi
    if [[ -f "$DC_BOT" ]] && grep -qE "$pattern" "$DC_BOT"; then
        FOUND_DC=1
    fi

    if [[ $FOUND_TG -eq 1 || $FOUND_DC -eq 1 ]]; then
        PASSED=$((PASSED + 1))
    else
        echo "FAIL: $ep 於 Telegram 或 Discord bot 中均未出現"
        FAIL=1
    fi
done <<< "$ENDPOINTS"

echo ""
echo "結果：$PASSED/$TOTAL 個 admin endpoint 於 bot 選單中有對應"

if [[ $FAIL -eq 0 ]]; then
    exit 0
else
    echo ""
    echo "部分 admin endpoint 沒有對應的 bot 選單，請同步補上"
    exit 1
fi
