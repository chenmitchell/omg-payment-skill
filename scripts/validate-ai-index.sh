#!/usr/bin/env bash
# validate-ai-index.sh
# 檢查所有 AI 平台入口檔案引用的 guides 路徑均存在於 repo。
#
# 規範：
#   下列檔案中以 `guides/XX-name.md` 形式出現之路徑必須全部存在：
#     SKILL.md, CLAUDE.md, AGENTS.md, GEMINI.md,
#     SKILL_OPENAI.md, vscode_copilot.md, google_AI_studio.md,
#     README.md
#
# 退出碼：0 = 全部存在；1 = 任一缺檔
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "== AI index 引用檢查 =="

FILES_TO_CHECK=(
    "SKILL.md"
    "CLAUDE.md"
    "AGENTS.md"
    "GEMINI.md"
    "SKILL_OPENAI.md"
    "vscode_copilot.md"
    "google_AI_studio.md"
    "README.md"
)

FAIL=0
TOTAL_REFS=0

for file in "${FILES_TO_CHECK[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "SKIP: $file 不存在"
        continue
    fi
    # 抓出所有 guides/xx-xxx.md 與 references/xxx.md 引用
    REFS="$(grep -oE '(guides|references)/[a-zA-Z0-9_-]+\.md' "$file" | sort -u)" || true
    if [[ -z "$REFS" ]]; then
        continue
    fi
    while IFS= read -r ref; do
        TOTAL_REFS=$((TOTAL_REFS + 1))
        if [[ ! -f "$ref" ]]; then
            echo "FAIL: $file 引用了 $ref，但檔案不存在"
            FAIL=1
        fi
    done <<< "$REFS"
done

if [[ $FAIL -eq 0 ]]; then
    echo "全部通過（檢查 $TOTAL_REFS 個引用）"
    exit 0
else
    echo ""
    echo "AI 入口檔案中有失效的引用，請補上缺檔或修正路徑"
    exit 1
fi
