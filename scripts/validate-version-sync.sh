#!/usr/bin/env bash
# validate-version-sync.sh
# 檢查所有平台入口檔案之版本號是否一致。
#
# 規範：
#   CHANGELOG.md 第一個 ## [X.Y.Z] 條目為 SSOT。
#   SKILL.md frontmatter 之 version 欄位必須與之相符。
#   README.md 之 Version badge 必須與之相符。
#
# 退出碼：0 = 全部一致；1 = 任一不符
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "== 版本同步檢查 =="

# 1. 從 CHANGELOG.md 取 SSOT 版本
SSOT_VERSION="$(grep -m1 '^## \[' CHANGELOG.md | sed -E 's/^## \[([^]]+)\].*/\1/')"
if [[ -z "$SSOT_VERSION" ]]; then
    echo "FAIL: 無法從 CHANGELOG.md 讀取 SSOT 版本"
    exit 1
fi
echo "SSOT version: $SSOT_VERSION"

FAIL=0

# 2. SKILL.md frontmatter
SKILL_VER="$(grep -m1 '^version:' SKILL.md | awk '{print $2}')"
if [[ "$SKILL_VER" != "$SSOT_VERSION" ]]; then
    echo "FAIL: SKILL.md frontmatter version ($SKILL_VER) != SSOT ($SSOT_VERSION)"
    FAIL=1
else
    echo "OK  : SKILL.md"
fi

# 3. README.md badge
if ! grep -q "version-${SSOT_VERSION}-blue" README.md; then
    echo "FAIL: README.md Version badge 不含 $SSOT_VERSION"
    FAIL=1
else
    echo "OK  : README.md"
fi

# 4. CHANGELOG.md 第一條必須是 SSOT 版本
CHANGELOG_FIRST="$(grep -m1 '^## \[' CHANGELOG.md | sed -E 's/^## \[([^]]+)\].*/\1/')"
if [[ "$CHANGELOG_FIRST" != "$SSOT_VERSION" ]]; then
    echo "FAIL: CHANGELOG.md 第一條版本不是 $SSOT_VERSION"
    FAIL=1
else
    echo "OK  : CHANGELOG.md"
fi

if [[ $FAIL -eq 0 ]]; then
    echo ""
    echo "全部通過（SSOT = $SSOT_VERSION）"
    exit 0
else
    echo ""
    echo "版本不同步，請修正上述檔案"
    exit 1
fi
