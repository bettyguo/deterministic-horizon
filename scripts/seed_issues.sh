#!/usr/bin/env bash
# Seed the public backlog: create milestones (with due dates) and file every
# draft in .github/ISSUE_DRAFTS/ as a GitHub issue.
#
# Idempotent: drafts whose title already exists as an open issue are skipped,
# milestones that already exist are left alone.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRAFTS_DIR="$REPO_ROOT/.github/ISSUE_DRAFTS"

# ---- Milestones --------------------------------------------------------------
# Title|Due (ISO 8601 UTC)|Description
MILESTONES=(
  "v1.0.1|2026-06-04T23:59:59Z|Polish: docs, demo, snapshot tests, CLI fix"
  "v1.1.0|2026-07-09T23:59:59Z|Coverage: new model adapters + UX"
  "v1.2.0|2026-08-20T23:59:59Z|Scale: new tasks + async evaluation"
  "v1.3.0|2026-10-29T23:59:59Z|Research: architecture studies"
)

# ---- Preflight ---------------------------------------------------------------
command -v gh >/dev/null 2>&1 || {
  echo "error: gh (GitHub CLI) is required. Install from https://cli.github.com/" >&2
  exit 1
}
command -v jq >/dev/null 2>&1 || {
  echo "error: jq is required to parse GitHub responses." >&2
  exit 1
}
gh auth status >/dev/null 2>&1 || {
  echo "error: gh is not authenticated. Run 'gh auth login' first." >&2
  exit 1
}

REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
echo "==> Repo: $REPO"

# ---- Create milestones -------------------------------------------------------
existing_milestones="$(gh api "repos/$REPO/milestones?state=all" --paginate \
  | jq -r '.[] | .title')"

for entry in "${MILESTONES[@]}"; do
  title="${entry%%|*}"
  rest="${entry#*|}"
  due="${rest%%|*}"
  desc="${rest#*|}"

  if echo "$existing_milestones" | grep -Fxq "$title"; then
    echo "    milestone exists: $title"
  else
    echo "    creating milestone: $title (due $due)"
    gh api "repos/$REPO/milestones" \
      -f title="$title" \
      -f state="open" \
      -f description="$desc" \
      -f due_on="$due" >/dev/null
  fi
done

# Build a map: milestone title -> number
declare -A MILESTONE_NUMBER
while IFS=$'\t' read -r number title; do
  MILESTONE_NUMBER["$title"]="$number"
done < <(gh api "repos/$REPO/milestones?state=all" --paginate \
  | jq -r '.[] | [.number, .title] | @tsv')

# ---- File issues -------------------------------------------------------------
existing_issue_titles="$(gh issue list --state all --limit 500 \
  --json title -q '.[].title')"

shopt -s nullglob
for draft in "$DRAFTS_DIR"/*.md; do
  name="$(basename "$draft")"
  [[ "$name" == "README.md" ]] && continue

  # Parse front-matter (between first two '---' lines).
  fm="$(awk '/^---$/{c++; next} c==1{print} c==2{exit}' "$draft")"
  body="$(awk 'BEGIN{c=0} /^---$/{c++; next} c>=2{print}' "$draft")"

  title="$(echo "$fm" | sed -n 's/^title:[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p')"
  milestone="$(echo "$fm" | sed -n 's/^milestone:[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p')"
  labels="$(echo "$fm" \
    | awk '/^labels:/{flag=1; next} /^[^[:space:]-]/{flag=0} flag && /^[[:space:]]*-/{sub(/^[[:space:]]*-[[:space:]]*/,""); print}' \
    | paste -sd, -)"

  if [[ -z "$title" ]]; then
    echo "    skip $name (no title)" >&2
    continue
  fi

  if echo "$existing_issue_titles" | grep -Fxq "$title"; then
    echo "    issue exists: $title"
    continue
  fi

  ms_num="${MILESTONE_NUMBER[$milestone]:-}"
  if [[ -z "$ms_num" ]]; then
    echo "    warn: milestone '$milestone' not found for $name; filing without milestone" >&2
  fi

  echo "==> filing: $title"
  args=(--title "$title" --body "$body")
  [[ -n "$labels" ]] && args+=(--label "$labels")
  [[ -n "$ms_num" ]] && args+=(--milestone "$milestone")

  gh issue create "${args[@]}"
done

echo "==> done."
