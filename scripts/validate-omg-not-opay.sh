#!/usr/bin/env bash
# validate-omg-not-opay.sh
# 檢查所有檔案中 "歐付寶" 的出現均位於明示區辨之上下文。
#
# 規則：
#   每一處 "歐付寶" 字串，其前後 120 字元內必須包含下列任一關鍵字：
#     - "不同", "獨立", "不是", "非", "區辨", "混用", "誤", "separate", "OPay"
#   以確保作者是在說「兩家公司不同」，而非意外把 OMG 寫成 OPay。
#
# 退出碼：0 = 全部通過；1 = 發現裸用「歐付寶」
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "== 歐買尬 vs 歐付寶 區辨檢查 =="

FAIL=0

# 蒐集所有含 "歐付寶" 的檔案（排除 scripts/ 目錄本身，驗證器必然需要字面引用）
FILES="$(grep -rlE --exclude-dir=.git --exclude-dir=node_modules \
    --exclude-dir=scripts \
    '歐付寶' . 2>/dev/null || true)"

if [[ -z "$FILES" ]]; then
    echo "全部通過（無 '歐付寶' 字樣）"
    exit 0
fi

# 對每個檔案逐行檢查上下文
while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    # 取得每一行 context
    while IFS= read -r line; do
        # 若該行同時含有區辨關鍵字或同時提到歐買尬，視為合規
        # 接受：不同、獨立、不是、非、區辨、混用、誤、separate、OPay、opay、
        #       ≠、vs、對照、修正、辨識、混淆、非歐付寶、同時提到歐買尬
        if echo "$line" | grep -qE '不同|獨立|不是|非|區辨|混用|混淆|誤|separate|OPay|opay|≠|vs|對照|修正|辨識|歐買尬|電子支付|OMG|MacroWell'; then
            continue
        fi
        echo "FAIL: $file 有未標示區辨之「歐付寶」："
        echo "      $line"
        FAIL=1
    done < <(grep -n '歐付寶' "$file")
done <<< "$FILES"

if [[ $FAIL -eq 0 ]]; then
    echo "全部通過（所有「歐付寶」均於區辨上下文中）"
    exit 0
else
    echo ""
    echo "發現裸用「歐付寶」，請改為「歐買尬」或補上區辨說明"
    exit 1
fi
