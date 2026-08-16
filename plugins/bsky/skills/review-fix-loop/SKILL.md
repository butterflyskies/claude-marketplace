---
name: review-fix-loop
category: code-review
description: "Iterative code review to convergence. Runs bsky:multimodel-elbow-grease (3 models × 6 lenses), fixes findings, and re-reviews the exact post-fix head until zero confirmed findings remain at every severity."
---

# /review-fix-loop — Iterative Code Review to Convergence

Run `bsky:multimodel-elbow-grease`, fix what it finds, re-review, repeat — until the diff is clean or
the round budget is exhausted. Each fix is a separate commit. Each re-review covers the
full diff (not just the fix), catching regressions. The skill never merges — convergence
means "ready for merge approval."

If a `required-environment-variables` memory exists (scope: global), read and apply it
before any git or provider-native repository operations.

**This is a principle-bound skill.** First invoke `bsky:load-design-principles`
and pass the returned digest to `bsky:multimodel-elbow-grease` invocations and fix agents.

## Arguments

`$ARGUMENTS` controls scope and behavior:

| Argument | Default | Meaning |
|----------|---------|---------|
| `--pr <number>` | current branch's PR | Review a specific PR |
| `--repo <owner/repo>` | current repo | Target repo (for cross-repo PRs) |
| `--max-rounds <N>` | `5` | Maximum review-fix iterations before stopping |
| `--fix-model <model>` | `sonnet` | Model for fix agents (`sonnet` or `opus`) |
| `--standards <memory-ref>` | auto-detect | Load coding standards as context for review and fix agents. Auto-detects `coding-standards-<repo>` from collective-conscious if not specified. |
| *(bare text)* | — | Passed through to `bsky:multimodel-elbow-grease` as scope (e.g., `branch`, `pr`, `files src/**`) |

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
- If on a branch with an open PR: review that PR using the provider-native client
- Otherwise: review all uncommitted changes (staged + unstaged + untracked)

Detect the provider from configured remotes. Use `gh` for GitHub and `tea` for
Forgejo through already configured authentication profiles. Never put tokens inline
in command arguments, URLs, environment assignments, or generated review text.
Before any provider write, verify the authenticated actor identity through the exact
client, auth profile, and repository context that will perform the write. Require it
to match the intended actor; successful authentication alone is not identity proof.
Stop on an unknown or mismatched actor.

## Phase 1: Resolve target

Determine what to review and establish the working state.

1. **Parse arguments** — extract flags, identify review scope
2. **Resolve the PR** (if applicable) with the provider-native client
3. **Check out the branch** — if reviewing a PR and not already on its branch,
   use the provider-native client or an authenticated git fetch
4. **Record the base commit and review artifact ID** — retain `git rev-parse HEAD`
   as the base for an initially uncommitted scope. For committed PR/branch scope, use its exact
   commit SHA. For staged, unstaged, or untracked scope, compute a deterministic
   identity from the base HEAD plus every in-scope path, mode, and byte, including
   untracked files. This identifies the bytes actually reviewed rather than merely
   their base commit.
5. **Load coding standards** — these are passed to review and fix agents as context:
   - If `--standards <memory-ref>` was provided, load that specific memory:
     ```
     recall query: "<memory-ref>", scope: "shared"
     ```
   - Otherwise, auto-detect from the repo name:
     ```bash
     REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
     ```
     ```
     recall query: "coding-standards-${REPO_NAME}", scope: "shared"
     ```
   - If recall returns a match (distance < 0.42), store its content as `$STANDARDS`
     for use in Phases 2 and 3.
   - If no standards are found, `$STANDARDS` is empty — review and fix proceed
     with general code quality only. Log: `Standards: none found (no coding-standards-<repo> in collective-conscious)`
6. **Log the configuration**:
   ```
   Target: PR #42 (owner/repo) | branch: feat/thing
   Max rounds: 5
   Fix model: sonnet
   Standards: coding-standards-my-repo (or: <explicit ref> | none)
   ```

## Phase 2: Review round

Run `bsky:multimodel-elbow-grease` on the target. This invokes the full elbow-grease skill with its
six parallel sub-agents, deduplication, and verification phases.

### First round

Record the review artifact ID immediately before dispatch. Immediately after the
review returns, recompute it and require equality. On drift, discard the round and
restart on the new artifact.

```
bsky:multimodel-elbow-grease <resolved-scope>
```

Where `<resolved-scope>` is:
- `pr <number>` if reviewing a PR
- `branch` if reviewing a branch
- (empty) if reviewing uncommitted changes in the first round

If an initially uncommitted scope produces fixes that are committed, change
`<resolved-scope>` for every subsequent convergence round to
`commits <recorded-base>..<exact-post-fix-SHA>`. This preserves the entire original
reviewed diff plus every fix; an empty scope after committing is never a valid
convergence review.

### Standards context for review

If `$STANDARDS` is non-empty, pass the loaded coding standards as additional context
to the `bsky:multimodel-elbow-grease` invocation. Review agents should evaluate the diff against both
general code quality AND the project-specific standards. Include the standards in the
review prompt preamble:

```
The following project coding standards apply to this review. Evaluate findings
against these standards in addition to general code quality:

<$STANDARDS content>
```

### Subsequent rounds

Record the exact post-fix SHA, assert it is the checked-out head, then review the full
original scope at that SHA:

```
bsky:multimodel-elbow-grease <resolved-scope>
```

Pass the recorded SHA and prior finding ledger as context, not as a diff restriction.
Do not use `--since` for convergence review. Convergence requires a full-scope review
of the exact post-fix SHA.

Immediately after the review returns, re-read the checked-out local head and the
provider PR head when a PR is in scope. Both must still equal the recorded SHA. If
either moved, discard that round's result, resolve and record the new head, and restart
the full-scope review. Never report convergence from findings computed across head drift.

### Capture findings

After `bsky:multimodel-elbow-grease` completes, collect its findings into a structured list.
Each finding has: severity (P1/P2/P3), title, file:line, issue description,
impact, and suggested fix.

Record every candidate with a typed disposition. During verification the allowed
states are `confirmed`, `rejected_with_evidence`, and `duplicate`. Every confirmed
P1, P2, and P3 finding is actionable. Terminal dispositions are only `fixed`,
`rejected_with_evidence`, or `duplicate`; `non-blocking`, `benign`, and
`accepted risk` are impact labels, not dispositions.

## Phase 3: Fix

If there are zero confirmed findings at every severity on the exact reviewed artifact,
skip to Phase 5 (converged).

For each actionable finding, **serially** (not in parallel — order matters for
files that have multiple findings):

1. **Dispatch a fix agent** with the finding details. Use the `Agent` tool:
   - Model: `--fix-model` value (default: sonnet)
   - Prompt includes: the finding (severity, file, line, issue, impact, fix),
     the project conventions, the loaded `$STANDARDS` (if any), and the
     instruction to make the minimal change that resolves the finding without
     altering design intent
   - The agent reads the relevant code, implements the fix, and verifies it
     compiles/passes lint

2. **Commit the fix** — maintain a path allowlist containing the initial review
   artifact's paths plus justified paths created or modified by fix agents. Add every
   such path to the subsequent full-scope review. Refuse unrelated
   concurrent paths, stage only that allowlist (never `git add -A`), then create one
   finding per commit:
   ```bash
   git add -- <reviewed-and-fix-paths...>
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

Project coding standards:
<$STANDARDS content, or "No project-specific standards loaded." if empty>

Instructions:
1. Read the file around the specified line to understand context
2. Implement the fix described above — minimal change, preserve design intent
3. Ensure the fix conforms to the project coding standards above (if provided)
4. If the fix requires changes in other files (e.g., callers), make those too
5. Run the project's formatter (cargo fmt / prettier / etc.) on changed files
6. Verify the fix compiles: run the build command but NOT the full test suite
7. If you cannot resolve this finding without changing the design intent, report
   that clearly — do not force a bad fix

Do NOT fix other issues you notice. One finding, one fix. Other issues will be
caught in the next review round.
```

### Ordering

Process findings in severity order: P1 first, then P2, then P3. Within the same
severity, process in file order (group fixes to the same file together to reduce
merge conflicts between sequential commits).

## Phase 4: Evaluate exit conditions

After all confirmed findings from this round have been processed:

1. **Record the exact post-fix commit**:
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

4. **Increment round counter** and loop back to Phase 2 for a full-scope re-review
   of that exact post-fix SHA.

The re-review is deliberately full-scope and does not use `--since`. This catches:
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
- **Reviewed artifact**: `<commit SHA or immutable worktree artifact ID, re-verified after review>`
- **Commits**: 5 fix commits on branch `feat/thing`
- **Escalated**: <N P1s that could not be resolved>

### Escalated findings (needs human review)
<only present if P1 escalations occurred>

**[P1] <title>** — `file:line`
<description>
<why the fix agent couldn't resolve it>
```

### Post the report

Follow the same posting hierarchy as `bsky:multimodel-elbow-grease` Phase 5:
1. If a PR exists: post as a PR comment with the provider-native client
2. Otherwise: display in-session

## Composability

This skill is designed to be called by other skills:

- **`/develop` Phase 4.5** already implements a similar fix-and-re-review loop inline.
  This skill extracts that pattern into a reusable, standalone component.
- **Ratchet's `--review` flag** can invoke this skill after its own convergence to
  add elbow-grease gating.
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
  finding) would miss regressions. Do not use `--since` for convergence review;
  review the full original scope at the exact post-fix SHA.
- **Fix agents are disposable** — each gets a fresh context with only its finding
  and project conventions. No accumulated state across findings.

## Guidelines

- **Minimal fixes only** — fix the finding, nothing else. Opportunistic refactoring
  during fix rounds creates noise and can trigger new findings, extending the loop.
- **Respect design intent** — if a fix would require changing the architectural
  approach, escalate. The review-fix loop is for correctness convergence, not redesign.
- **Trust but verify** — the elbow-grease skill verifies its own findings in Phase 3.
  This skill trusts those verified findings and focuses on fixing them.
- **Zero means zero** — do not declare convergence while any confirmed P1, P2, or
  P3 finding remains. Low impact changes priority, not disposition.
