---
name: ratchet
description: "Automated hill-climbing loop. Proposes changes, tests, keeps improvements, reverts regressions. Grinds overnight."
---

# /ratchet — Automated Hill-Climbing

Automated improvement loop inspired by Karpathy's autoresearch. Propose a change,
run the tests, keep if the metric improves, revert if it doesn't. Repeat until the
budget runs out or progress stalls.

## Argument handling

`$ARGUMENTS` provides the configuration:

| Argument                | Required | Description                                      |
|-------------------------|----------|--------------------------------------------------|
| `--scope <file>`        | yes      | Markdown file with directions and constraints    |
| `--test <command>`      | yes      | Shell command that outputs JSON with the metric  |
| `--target <glob>`       | yes      | Files the agent may modify (glob or list)        |
| `--minimize`            | one of   | Optimize by reducing the metric                  |
| `--maximize`            | these    | Optimize by increasing the metric                |
| `--metric <field>`      | no       | JSON field to optimize (default: `score`)        |
| `--budget <minutes>`    | no       | Max runtime in minutes (default: 60)             |
| `--max-stalls <N>`      | no       | Consecutive failures before exit (default: 5)    |
| `--model <model>`       | no       | Model for the grinding agent (default: sonnet)   |
| `--escalate`            | no       | Bump to opus when stall limit is reached         |
| `--review`              | no       | Auto-invoke /review-fix-loop on convergence      |

`--minimize` or `--maximize` is required. The skill refuses to run without an
explicit metric direction.

## Scope file format

The scope file is a markdown document with three sections. It is the contract
between human intent and agent execution.

```markdown
## Directions

1. Try X to improve Y
2. Explore Z as an alternative approach
3. Consider adjusting parameter W

## Constraints

- Do not change the public API surface
- Keep backward compatibility with format V1
- All changes must pass the existing test suite

## Do Not Touch

- tests/
- config/production.toml
- any file outside src/
```

The agent picks from Directions, respects Constraints, and never modifies
anything listed in Do Not Touch — regardless of the `--target` glob.

## Phase 1: Setup

1. **Detect VCS.** Check for `.jj` first (use jj workspaces for isolation),
   fall back to git worktrees. If neither: error and exit.

2. **Validate inputs.** Confirm the scope file exists and has the required
   sections. Confirm the test command runs successfully. Confirm at least one
   file matches the target glob.

3. **Capture baseline.** Run the test command and record the starting metric
   value. All subsequent comparisons are against this baseline, not against
   the previous iteration. This prevents upward drift on noisy metrics.

4. **Create workspace.** jj: create a new workspace for the run. git: create
   a worktree on a temporary branch.

5. **Report.** Post a one-line status: "ratchet started. baseline {metric}={value}.
   budget: {minutes}m. target: {glob}. direction: {minimize|maximize}."

## Phase 2: Hill-climbing loop

Spawn a sub-agent (at the configured `--model` tier) for each attempt. The
sub-agent receives:

- The scope file (directions, constraints, do-not-touch)
- The current state of the target files
- The baseline metric and current best metric
- The history of recent attempts (what was tried, what worked, what didn't)

The sub-agent proposes a change. Then:

1. **Apply the change** to the target files only. If the change touches any
   file outside the target glob or listed in Do Not Touch, reject it without
   running the test.

2. **Run the test command.** Parse the JSON output for the metric field.

3. **Evaluate:**
   - If the metric improved vs the baseline: **keep.** Commit with a message
     describing the change and the metric delta. The baseline does NOT move —
     all comparisons remain against the original starting value.
   - If the metric did not improve or the test failed: **revert.** Reset to
     the previous commit. Increment the stall counter.

4. **Check exit conditions:**
   - Budget exceeded → exit gracefully
   - Stall counter >= `--max-stalls` and `--escalate` set → reset stall
     counter, bump the sub-agent model to opus, continue
   - Stall counter >= `--max-stalls` without `--escalate` → exit gracefully
   - Token budget approaching limit → exit gracefully

5. **Loop.** Return to step 1 with the updated state.

Each sub-agent attempt is time-boxed to `budget / max_reasonable_attempts`
(floor 2 minutes, cap 15 minutes per attempt). If an attempt exceeds its
time box, kill it and count it as a stall.

## Phase 3: Report

On exit (any reason), produce a single structured report:

```
## Ratchet Report

**Scope:** {scope file}
**Target:** {glob}
**Direction:** {minimize|maximize} {metric}
**Budget:** {used}m / {total}m
**Model:** {model} (escalated: {yes|no})

### Results

| Metric   | Start  | Final  | Delta  | Change |
|----------|--------|--------|--------|--------|
| {metric} | {base} | {best} | {diff} | {pct}% |

### Attempts

- Total: {N}
- Kept: {K} ({K/N}%)
- Reverted: {R}
- Timed out: {T}

### Kept Changes

1. {commit hash} — {description} ({metric}: {before} → {after})
2. ...

### Exit Reason

{budget_exceeded | max_stalls | token_limit | no_targets}
```

Post this report to the channel. If `--review` was set, invoke `/review-fix-loop`
on the accumulated changes.

## Constraints

- The sub-agent ONLY modifies files matching the target glob that are NOT in
  Do Not Touch. This is enforced by checking the diff before committing, not
  just by instruction.
- The test harness (the `--test` command and its dependencies) is immutable.
  The sub-agent has no access to modify it.
- The ratchet is greedy. It does not tolerate temporary regressions for
  multi-step improvements. Each commit must independently improve the metric.
- All metric comparisons are against the captured baseline, not the previous
  iteration.
- The sub-agent receives attempt history so it avoids re-trying failed
  approaches. The history includes what was tried and why it was reverted.
