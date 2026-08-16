#!/usr/bin/env bash
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
ELBOW=${1:-"$ROOT/plugins/bsky/skills/elbow-grease/SKILL.md"}
LOOP=${2:-"$ROOT/plugins/bsky/skills/review-fix-loop/SKILL.md"}
WORKFLOW=${3:-"$ROOT/.github/workflows/skill-consistency.yml"}

validate_workflow() {
  local workflow=$1

  step_has_pipefail() {
    local step_name=$1
    awk -v step_name="$step_name" '
      index($0, "- name: \"" step_name "\"") { inside = 1; next }
      inside && /^[[:space:]]+- name:/ { inside = 0 }
      inside && /set -o pipefail/ { guards++ }
      inside && /\| tee/ { pipeline = 1 }
      END { exit(guards == 1 && pipeline ? 0 : 1) }
    ' "$workflow"
  }

  step_has_pipefail '(relationAll loadsDesignPrinciples PrincipleBoundSkill)' || return 1
  step_has_pipefail 'Review convergence contract' || return 1
}

validate_contract() {
  local elbow=$1
  local loop=$2
  local preambles

  preambles=$(grep -c 'Report every supported finding at every severity' "$elbow" || true)
  [[ "$preambles" -eq 6 ]] || return 1

  section_has_rule() {
    local start=$1
    local stop=$2
    awk -v start="$start" -v stop="$stop" '
      $0 == start { inside = 1; next }
      $0 == stop { inside = 0 }
      inside && $0 == "```" { fenced = !fenced; next }
      inside && fenced && index($0, "Report every supported finding at every severity") { found = 1 }
      END { exit(found ? 0 : 1) }
    ' "$elbow"
  }

  section_has_rule '### Safety' '### Design' || return 1
  section_has_rule '### Design' '### Security (model: opus)' || return 1
  section_has_rule '### Security (model: opus)' '### Privacy (model: opus)' || return 1
  section_has_rule '### Privacy (model: opus)' '### Idiomacy (model: opus)' || return 1
  section_has_rule '### Idiomacy (model: opus)' '### Tests (model: sonnet)' || return 1
  section_has_rule '### Tests (model: sonnet)' '### Providing context to sub-agents' || return 1

  grep -q 'duplicate cache-fill race from a security' "$elbow" || return 1
  grep -q 'for every P1, P2, and P3' "$elbow" || return 1
  grep -q '`fixed`' "$elbow" || return 1
  grep -q '`rejected_with_evidence`' "$elbow" || return 1
  grep -q '`duplicate`' "$elbow" || return 1
  grep -q 'zero confirmed findings at every severity on that exact SHA' "$elbow" || return 1
  grep -q 'Record the review artifact ID' "$elbow" || return 1
  grep -q 'base HEAD plus every in-scope path, mode, and byte' "$elbow" || return 1
  grep -q 'staged + unstaged + untracked' "$elbow" || return 1
  grep -q '`commits <range>`' "$elbow" || return 1
  grep -q 'After review, re-read the local head and provider PR head' "$elbow" || return 1
  grep -q 'Reviewed artifact: <commit SHA, or immutable worktree artifact ID, re-verified after review>' "$elbow" || return 1
  grep -q 'repo-native tooling' "$elbow" || return 1
  grep -q 'Never put tokens inline' "$elbow" || return 1
  tr '\n' ' ' <"$elbow" | grep -q 'Before any provider write, verify the authenticated actor identity through the exact client, auth profile, and repository context that will perform the write.' || return 1
  tr '\n' ' ' <"$elbow" | grep -q 'Require it to match the intended actor; successful authentication alone is not identity proof. Stop on an unknown or mismatched actor.' || return 1
  ! grep -q 'skip_categories' "$elbow" || return 1
  ! grep -q 'P3→ignore' "$elbow" || return 1
  ! grep -q 'deferred-with-rationale' "$elbow" || return 1
  ! grep -q 'explicitly deferred' "$elbow" || return 1

  grep -q 'zero confirmed findings remain at every severity' "$loop" || return 1
  grep -q 'full-scope review' "$loop" || return 1
  grep -q 'of the exact post-fix SHA' "$loop" || return 1
  grep -q '^Record the exact post-fix SHA, assert it is the checked-out head' "$loop" || return 1
  grep -q '^Pass the recorded SHA and prior finding ledger as context' "$loop" || return 1
  grep -q '^If there are zero confirmed findings at every severity on the exact reviewed artifact' "$loop" || return 1
  grep -q '^Record the review artifact ID immediately before dispatch' "$loop" || return 1
  grep -q 'base HEAD plus every in-scope path, mode, and byte' "$loop" || return 1
  grep -q 'commits <recorded-base>..<exact-post-fix-SHA>' "$loop" || return 1
  grep -q 'stage only that allowlist (never `git add -A`)' "$loop" || return 1
  grep -q 'justified paths created or modified by fix agents' "$loop" || return 1
  grep -q '^Immediately after the review returns, re-read the checked-out local head' "$loop" || return 1
  grep -q '\*\*Reviewed artifact\*\*: `<commit SHA or immutable worktree artifact ID, re-verified after review>`' "$loop" || return 1
  grep -q '`fixed`' "$loop" || return 1
  grep -q '`rejected_with_evidence`' "$loop" || return 1
  grep -q '`duplicate`' "$loop" || return 1
  grep -q 'provider-native' "$loop" || return 1
  grep -q 'Never put tokens inline' "$loop" || return 1
  tr '\n' ' ' <"$loop" | grep -q 'Before any provider write, verify the authenticated actor identity through the exact client, auth profile, and repository context that will perform the write.' || return 1
  tr '\n' ' ' <"$loop" | grep -q 'Require it to match the intended actor; successful authentication alone is not identity proof. Stop on an unknown or mismatched actor.' || return 1

  ! grep -q -- '--min-severity' "$loop" || return 1
  awk 'index($0, "--since") && $0 !~ /(Do not use|does not use)/ { bad = 1 }
       END { exit(bad ? 1 : 0) }' "$loop" || return 1
  ! grep -qi 'below threshold' "$loop" || return 1
  ! grep -qi 'noted, not fixed' "$loop" || return 1
  ! grep -q '^   git add -A' "$loop" || return 1
}

expect_rejection() {
  local label=$1
  local elbow=$2
  local loop=$3
  if validate_contract "$elbow" "$loop"; then
    echo "FAIL: invalid fixture accepted: $label" >&2
    return 1
  fi
  echo "PASS: invalid fixture rejected: $label"
}

validate_workflow "$WORKFLOW"
validate_contract "$ELBOW" "$LOOP"
echo 'PASS: live review skills satisfy the convergence contract'

SCRATCH=$(mktemp -d)
trap 'rm -rf "$SCRATCH"' EXIT
cp "$ELBOW" "$SCRATCH/elbow.md"
cp "$LOOP" "$SCRATCH/loop.md"

sed 's/duplicate cache-fill race from a security/benign cache race may be dismissed beside a security/' \
  "$ELBOW" >"$SCRATCH/hidden-race.md"
expect_rejection 'hidden benign race' "$SCRATCH/hidden-race.md" "$LOOP"

cp "$LOOP" "$SCRATCH/threshold.md"
printf '\n--min-severity P2\n' >>"$SCRATCH/threshold.md"
expect_rejection 'P3 left below threshold' "$ELBOW" "$SCRATCH/threshold.md"

sed 's/exact post-fix SHA/post-fix state/g' \
  "$LOOP" >"$SCRATCH/unanchored-head.md"
expect_rejection 'convergence without exact post-fix SHA' "$ELBOW" "$SCRATCH/unanchored-head.md"

sed 's/Report every supported finding at every severity/Report supported findings carefully/g' \
  "$ELBOW" >"$SCRATCH/misplaced-preamble.md"
for _ in 1 2 3 4 5 6; do
  printf '\nReport every supported finding at every severity\n' >>"$SCRATCH/misplaced-preamble.md"
done
expect_rejection 'review rule outside prompt blocks' "$SCRATCH/misplaced-preamble.md" "$LOOP"

sed 's/Before any provider write/After any provider write/g' \
  "$ELBOW" >"$SCRATCH/post-write-elbow.md"
sed 's/Before any provider write/After any provider write/g' \
  "$LOOP" >"$SCRATCH/post-write-loop.md"
expect_rejection 'actor check after provider write' "$SCRATCH/post-write-elbow.md" "$SCRATCH/post-write-loop.md"

cp "$LOOP" "$SCRATCH/multiline-since.md"
printf '\nbsky:multimodel-elbow-grease branch \\\n  --since old-head\n' >>"$SCRATCH/multiline-since.md"
expect_rejection 'multiline incremental convergence review' "$ELBOW" "$SCRATCH/multiline-since.md"

sed 's/Report every supported finding at every severity/Report supported findings carefully/g' \
  "$ELBOW" | awk '
    /^### (Design|Security \(model: opus\)|Privacy \(model: opus\)|Idiomacy \(model: opus\)|Tests \(model: sonnet\)|Providing context to sub-agents)$/ {
      print "Report every supported finding at every severity"
    }
    { print }
  ' >"$SCRATCH/outside-fence.md"
expect_rejection 'review rule outside fenced prompts' "$SCRATCH/outside-fence.md" "$LOOP"

sed -e 's/Record the exact post-fix SHA, assert it is the checked-out head/Record a post-fix label without asserting the checked-out head/' \
    -e 's/Pass the recorded SHA and prior finding ledger as context/Do not pass the recorded SHA; pass only the prior finding ledger as context/' \
  "$LOOP" >"$SCRATCH/unpinned-operation.md"
expect_rejection 'descriptive SHA without operational pin' "$ELBOW" "$SCRATCH/unpinned-operation.md"

sed 's/If there are zero confirmed findings at every severity on the exact reviewed artifact/If there are zero P1 findings on the reviewed artifact/' \
  "$LOOP" >"$SCRATCH/p1-only-gate.md"
expect_rejection 'P1-only convergence gate' "$ELBOW" "$SCRATCH/p1-only-gate.md"

sed -e 's/through the exact/through any available/' \
    -e 's/Stop on an unknown or mismatched actor/Continue on an unknown or mismatched actor/g' \
  "$ELBOW" >"$SCRATCH/weak-auth-elbow.md"
sed -e 's/through the exact/through any available/' \
    -e 's/Stop on an unknown or mismatched actor/Continue on an unknown or mismatched actor/g' \
  "$LOOP" >"$SCRATCH/weak-auth-loop.md"
expect_rejection 'weak provider actor verification' "$SCRATCH/weak-auth-elbow.md" "$SCRATCH/weak-auth-loop.md"

sed '/Immediately after the review returns, re-read the checked-out local head/,+3d' \
  "$LOOP" >"$SCRATCH/no-post-review-head-check.md"
expect_rejection 'no post-review head equality check' "$ELBOW" "$SCRATCH/no-post-review-head-check.md"

sed '/Record the review artifact ID immediately before dispatch/,+2d' \
  "$LOOP" >"$SCRATCH/no-worktree-artifact.md"
expect_rejection 'uncommitted scope without immutable artifact ID' "$ELBOW" "$SCRATCH/no-worktree-artifact.md"

sed '/If an initially uncommitted scope produces fixes that are committed/,+4d' \
  "$LOOP" >"$SCRATCH/empty-post-fix-scope.md"
expect_rejection 'empty post-fix scope after committing' "$ELBOW" "$SCRATCH/empty-post-fix-scope.md"

sed 's/git add -- <reviewed-and-fix-paths\.\.\.>/git add -A/' \
  "$LOOP" >"$SCRATCH/stage-all.md"
expect_rejection 'stage-all admits unreviewed paths' "$ELBOW" "$SCRATCH/stage-all.md"

sed 's/justified paths created or modified by fix agents/justified paths created by fix agents/' \
  "$LOOP" >"$SCRATCH/no-existing-caller-path.md"
expect_rejection 'existing caller fix excluded from scope' "$ELBOW" "$SCRATCH/no-existing-caller-path.md"

awk '
  /set -o pipefail/ {
    guards++
    if (guards == 1) { print; print; next }
    if (guards == 2) { next }
  }
  { print }
' "$WORKFLOW" >"$SCRATCH/misplaced-pipefail.yml"
if validate_workflow "$SCRATCH/misplaced-pipefail.yml"; then
  echo 'FAIL: invalid fixture accepted: both pipefail guards in one workflow step' >&2
  exit 1
fi
echo 'PASS: invalid fixture rejected: both pipefail guards in one workflow step'
