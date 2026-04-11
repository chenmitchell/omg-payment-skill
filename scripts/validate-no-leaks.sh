#!/usr/bin/env bash
# validate-no-leaks.sh
# 檢查 repo 中是否誤存內部個案商家資訊、真實金鑰、可辨識路徑。
#
# 禁止字串清單：
#   - 維護者個人專案代號（如 outpost、outpost-news）
#   - 常見金鑰字首樣式（僅示意，擴充時請避免產生誤擊）
#   - 個案商家之可辨識字串
#
# 允許之例外：
#   - 官方公告之測試 MerchantID 1000031
#   - 測試金鑰 TESTKEY / TESTIV 開頭字串
#
# 退出碼：0 = 無洩漏；1 = 偵測到疑似洩漏
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "== 內部資訊洩漏掃描 =="

# 禁止字串（case-insensitive，逐字檢查）
# 注意：outpost.mitch.tw 為維護者公開作品網址，已列入白名單；
# 本檢查著重於個案商家之內部實作字串（schema、路徑、internal service 名）。
FORBIDDEN=(
    "outpost-news"
    "outpost-frontend"
    "outpost-api"
    "outpost_news"
    "outpost_frontend"
    "outpost_api"
)

# 允許之公開字串（白名單）
ALLOWED_PUBLIC=(
    "outpost.mitch.tw"
    "www.mitch.tw"
)

FAIL=0

for needle in "${FORBIDDEN[@]}"; do
    # 排除 .git、scripts/validate-no-leaks.sh 本身、node_modules
    if grep -riE --exclude-dir=.git --exclude-dir=node_modules \
        --exclude="validate-no-leaks.sh" "$needle" . > /dev/null 2>&1; then
        echo "FAIL: 偵測到禁止字串 '$needle'"
        grep -riE -l --exclude-dir=.git --exclude-dir=node_modules \
            --exclude="validate-no-leaks.sh" "$needle" . || true
        FAIL=1
    fi
done

# 檢查 "outpost" 單獨出現（不是 outpost.mitch.tw 形式）
# 先過濾白名單，再檢查是否有裸 outpost
LOOSE_HITS="$(grep -riE --exclude-dir=.git --exclude-dir=node_modules \
    --exclude="validate-no-leaks.sh" 'outpost' . 2>/dev/null | \
    grep -vE 'outpost\.mitch\.tw' || true)"
if [[ -n "$LOOSE_HITS" ]]; then
    echo "WARN: 偵測到 'outpost' 字串但不屬於白名單 outpost.mitch.tw，請人工確認："
    echo "$LOOSE_HITS" | head -10
fi

# 掃描可疑金鑰樣式（32+ 位十六進位，非測試向量白名單）
# 排除已知測試常數
SUSPICIOUS_HEX="$(grep -rE --exclude-dir=.git --exclude-dir=node_modules \
    --exclude="*.json" --exclude="check-mac-value.md" \
    '[A-F0-9]{64}' . 2>/dev/null | \
    grep -v 'TESTKEY\|TESTIV\|1000031\|84A9C3EFD9D359\|E0437AB2B5A9C1DF\|D73278BDDE906AC3' || true)"

if [[ -n "$SUSPICIOUS_HEX" ]]; then
    echo "WARN: 偵測到 64 位十六進位字串（可能為 MAC 或金鑰），請人工確認："
    echo "$SUSPICIOUS_HEX" | head -20
fi

# 掃描疑似 MerchantID（7 位數字），排除官方測試用 1000031
# 先過濾 test-vectors 與 README 等允許位置
SUSPICIOUS_MID="$(grep -rE --exclude-dir=.git --exclude-dir=node_modules \
    'MerchantID[": =]+[0-9]{7}' . 2>/dev/null | \
    grep -v '1000031' || true)"

if [[ -n "$SUSPICIOUS_MID" ]]; then
    echo "FAIL: 偵測到非 1000031 之 MerchantID 引用："
    echo "$SUSPICIOUS_MID"
    FAIL=1
fi

if [[ $FAIL -eq 0 ]]; then
    echo ""
    echo "全部通過（無內部資訊洩漏）"
    exit 0
else
    echo ""
    echo "發現疑似內部資訊洩漏，請移除後再提交"
    exit 1
fi
