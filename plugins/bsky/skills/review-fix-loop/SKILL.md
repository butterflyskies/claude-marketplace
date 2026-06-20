---
name: review-fix-loop
description: "Iterative code review to convergence. Runs code-review, fixes findings, re-reviews, repeats until zero findings at or above the severity threshold."
---

# /review-fix-loop — Iterative Code Review to Convergence

Run `/code-review`, fix what it finds, re-review, repeat — until the diff is clean or
the round budget is exhausted. Each fix is a separate commit. Each re-review covers the
full diff (not just the fix), catching regressions. The skill never merges — convergence
means "ready for merge approval."

If a `required-environment-variables` memory exists (scope: global), read and apply it
before any git/gh operations.

## Arguments

`$ARGUMENTS` controls scope and behavior:

| Argument | Default | Meaning |
|----------|---------|---------|
| `--pr <number>` | current branch's PR | Review a specific PR |
| `--repo <owner/repo>` | current repo | Target repo (for cross-repo PRs) |
| `--max-rounds <N>` | `5` | Maximum review-fix iterations before stopping |
| `--min-severity <level>` | `P3` | Fix findings at this level and above (`P1`, `P2`, or `P3`) |
| `--fix-model <model>` | `sonnet` | Model for fix agents (`sonnet` or `opus`) |
| *(bare text)* | — | Passed through to `/code-review` as scope (e.g., `branch`, `pr`, `files src/**`) |

### Argument parsing

Parse `$ARGUMENTS` by extracting `--flag value` pairs first, then treating remaining
text as the review scope. Use jq for any structured parsing:

```bash
# Example: extract --max-rounds from args, default to 5
echo "$ARGUMENTS" | jq -Rr 'split(" ") | to_entries
  | (map(select(.value == "--max-rounds")) | first // null) as $idx
  | if $idx then .[$idx.key + 1].value else "5" end'
```

Defaults when no scope is specified:
- If `--pr` is given: review that PR
- If on a branch with an open PR: review that PR (`gh pr list --head <branch> --state open --json number --jq '.[0].number'`)
- Otherwise: review all uncommitted changes (staged + unstaged)

## Phase 1: Resolve target

Determine what to review and establish the working state.

1. **Parse arguments** — extract flags, identify review scope
2. **Resolve the PR** (if applicable):
   ```bash
   # If --pr given:
   gh pr view <number> --repo <repo> --json number,headRefName,baseRefName,url
   # If no --pr, check current branch:
   gh pr list --head "$(git branch --show-current)" --state open --json number,url --jq '.[0]'
   ```
3. **Check out the branch** — if reviewing a PR and not already on its branch:
   ```bash
   gh pr checkout <number> --repo <repo>
   ```
4. **Record the starting commit** — this is the baseline for the first review:
   ```bash
   git rev-parse HEAD
   ```
5. **Log the configuration**:
   ```
   Target: PR #42 (owner/repo) | branch: feat/thing
   Max rounds: 5
   Min severity: P3
   Fix model: sonnet
   ```

## Phase 2: Review round

Run `/code-review` on the target. This invokes the full code-review skill with its
five parallel sub-agents, deduplication, and verification phases.

### First round

```
/code-review <resolved-scope>
```

Where `<resolved-scope>` is:
- `pr <number>` if reviewing a PR
- `branch` if reviewing a branch
- (empty) if reviewing uncommitted changes

### Subsequent rounds

Use incremental review mode to avoid re-reviewing unchanged code:

```
/code-review <resolved-scope> --since <last-reviewed-commit>
```

Pass the commit SHA recorded at the end of the previous round's fix phase.

### Capture findings

After `/code-review` completes, collect its findings into a structured list.
Each finding has: severity (P1/P2/P3), title, file:line, issue description,
impact, and suggested fix.

Partition findings into two buckets:
- **actionable**: severity >= `--min-severity` threshold
- **noted**: severity < threshold (reported but not fixed)

Severity ordering: P1 > P2 > P3. With `--min-severity P2`, P1 and P2 are
actionable; P3 is noted. With `--min-severity P3` (default), everything is
actionable.

## Phase 3: Fix

If there are zero actionable findings, skip to Phase 5 (converged).

For each actionable finding, **serially** (not in parallel — order matters for
files that have multiple findings):

1. **Dispatch a fix agent** with the finding details. Use the `Agent` tool:
   - Model: `--fix-model` value (default: sonnet)
   - Prompt includes: the finding (severity, file, line, issue, impact, fix),
     the project conventions, and the instruction to make the minimal change
     that resolves the finding without altering design intent
   - The agent reads the relevant code, implements the fix, and verifies it
     compiles/passes lint

2. **Commit the fix** — one finding, one commit:
   ```bash
   git add -A
   git commit -m "$(cat <<'EOF'
   fix: <finding-title>

   Address <severity> finding from review round <N>:
   <one-line issue description>

   Co-Authored-By: Claude <agent-model> (review-fix-loop) <noreply@anthropic.com>
   EOF
   )"
   ```

3. **Check for P1 escalation** — if the fix agent reports it cannot resolve a P1
   finding (e.g., requires design change, ambiguous intent, or the fix introduces
   worse problems), mark it as **escalated** and continue to the next finding.
   Escalated P1s stop the loop in Phase 4.

### Fix agent prompt template

```
You are a fix agent. Your job is to implement a single, minimal code fix.

Finding:
- Severity: <P1|P2|P3>
- Title: <title>
- File: <file:line>
- Issue: <description>
- Impact: <what breaks>
- Suggested fix: <from the review>

Project conventions: <from CLAUDE.md / memory-mcp>

Instructions:
1. Read the file around the specified line to understand context
2. Implement the fix described above — minimal change, preserve design intent
3. If the fix requires changes in other files (e.g., callers), make those too
4. Run the project's formatter (cargo fmt / prettier / etc.) on changed files
5. Verify the fix compiles: run the build command but NOT the full test suite
6. If you cannot resolve this finding without changing the design intent, report
   that clearly — do not force a bad fix

Do NOT fix other issues you notice. One finding, one fix. Other issues will be
caught in the next review round.
```

### Ordering

Process findings in severity order: P1 first, then P2, then P3. Within the same
severity, process in file order (group fixes to the same file together to reduce
merge conflicts between sequential commits).

## Phase 4: Evaluate exit conditions

After all actionable findings from this round have been processed:

1. **Record the post-fix commit**:
   ```bash
   git rev-parse HEAD
   ```

2. **Push the fixes** (if working on a PR branch):
   ```bash
   git push
   ```

3. **Check exit conditions**:

   | Condition | Action |
   |-----------|--------|
   | Escalated P1 exists | **Exit: escalate.** Report the P1 and flag for human review. |
   | Round count >= `--max-rounds` | **Exit: stalled.** Report remaining findings. |
   | Otherwise | **Continue to Phase 2** (next review round). |

4. **Increment round counter** and loop back to Phase 2 for a full re-review.

The re-review is deliberately full-scope (with `--since` for efficiency, but the
code-review skill's incremental mode still verifies prior findings are resolved
and checks for regressions). This catches:
- Fixes that introduced new bugs
- Fixes that resolved one finding but exposed another
- Interaction effects between multiple fixes

## Phase 5: Exit report

Produce a structured convergence report. This is the primary output of the skill.

```
## Review-Fix Loop: <target description>

### Result: <CONVERGED | STALLED | ESCALATED>

### Rounds

| Round | Findings | Fixed | New | Escalated |
|-------|----------|-------|-----|-----------|
| 1     | 4 (1 P1, 2 P2, 1 P3) | 4 | — | 0 |
| 2     | 1 (0 P1, 1 P2, 0 P3) | 1 | 1 (regression) | 0 |
| 3     | 0 | — | — | — |

### Final state
- **Status**: Converged after 3 rounds
- **Commits**: 5 fix commits on branch `feat/thing`
- **Noted (below threshold)**: <N findings reported but not fixed>
- **Escalated**: <N P1s that could not be resolved>

### Noted findings (not fixed)
<only present if --min-severity excluded some findings>

**[P3] <title>** — `file:line`
<description>

### Escalated findings (needs human review)
<only present if P1 escalations occurred>

**[P1] <title>** — `file:line`
<description>
<why the fix agent couldn't resolve it>
```

### Post the report

Follow the same posting hierarchy as `/code-review` Phase 5:
1. If a PR exists: post as a PR comment (`gh pr comment <number> --body <report>`)
2. Otherwise: display in-session

## Composability

This skill is designed to be called by other skills:

- **`/develop` Phase 4.5** already implements a similar fix-and-re-review loop inline.
  This skill extracts that pattern into a reusable, standalone component.
- **Ratchet's `--review` flag** can invoke this skill after its own convergence to
  add code-review gating.
- **Standalone use** on any PR: `/review-fix-loop --pr 42`

When invoked by another skill, the exit report is returned to the caller for
incorporation into its own output. The caller decides what to do with STALLED
or ESCALATED results.

## Constraints

- **Never merges** — convergence means the branch is clean, not that it's merged.
  Merge approval is a human decision.
- **Never amends** — each fix is a new commit. The PR history shows the full
  review-fix progression.
- **Never runs fixes in parallel** — serial execution prevents conflicts when
  multiple findings touch the same file or interacting code paths.
- **Full re-review after each round** — scoped re-review (only checking the fixed
  finding) would miss regressions. The `--since` flag on `/code-review` provides
  efficiency without sacrificing coverage.
- **Fix agents are disposable** — each gets a fresh context with only its finding
  and project conventions. No accumulated state across findings.

## Guidelines

- **Minimal fixes only** — fix the finding, nothing else. Opportunistic refactoring
  during fix rounds creates noise and can trigger new findings, extending the loop.
- **Respect design intent** — if a fix would require changing the architectural
  approach, escalate. The review-fix loop is for correctness convergence, not redesign.
- **Trust but verify** — the code-review skill verifies its own findings in Phase 3.
  This skill trusts those verified findings and focuses on fixing them.
- **Report everything** — even findings below the severity threshold appear in the
  exit report. "Noted, not fixed" is a deliberate outcome, not a silent omission.
