#!/usr/bin/env bash
# validate-agents-parity.sh
# 檢查所有 AI 平台入口檔案均包含核心聲明與官方資源連結。
#
# 每一份入口檔案必須包含：
#   1. 非官方聲明字串
#   2. 歐買尬 vs 歐付寶 區辨提醒
#   3. 官方資源 URL: https://github.com/omgtwhub
#
# 退出碼：0 = 全部包含；1 = 任一缺漏
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "== AI 入口檔案 parity 檢查 =="

FILES=(
    "SKILL.md"
    "CLAUDE.md"
    "AGENTS.md"
    "GEMINI.md"
    "SKILL_OPENAI.md"
    "vscode_copilot.md"
    "google_AI_studio.md"
    "README.md"
)

REQUIRED_MARKERS=(
    "非官方"
    "歐付寶"
    "omgtwhub"
)

FAIL=0

for file in "${FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "SKIP: $file 不存在"
        continue
    fi
    MISSING=""
    for marker in "${REQUIRED_MARKERS[@]}"; do
        if ! grep -q "$marker" "$file"; then
            MISSING+="$marker "
        fi
    done
    if [[ -n "$MISSING" ]]; then
        echo "FAIL: $file 缺少關鍵字：$MISSING"
        FAIL=1
    else
        echo "OK  : $file"
    fi
done

if [[ $FAIL -eq 0 ]]; then
    echo ""
    echo "全部通過"
    exit 0
else
    echo ""
    echo "部分入口檔案缺少核心聲明，請補齊"
    exit 1
fi
