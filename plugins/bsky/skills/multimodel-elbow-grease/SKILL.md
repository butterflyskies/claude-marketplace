---
name: multimodel-elbow-grease
category: code-review
description: >-
  Multi-model code review. Runs elbow-grease (5 lenses) across 3 models
  (opus, sonnet, fable) = 15 focused reviews, then deduplicates with
  cross-model consensus scoring.
---

# Multi-Model Code Review

Run a structured code review through three LLM models, then synthesize the
results with cross-model consensus. Each model runs all five review lenses
independently, producing 15 focused reviews that are deduplicated and verified.

## How it works

This skill invokes `bsky:elbow-grease` three times — once per model — using
native Claude Agent dispatch. Each invocation runs all five review lenses
(correctness, design, architecture, idiomacy, tests) on a single model.

Default models:

- **opus** — deep judgment, security, architecture
- **sonnet** — fast mechanical analysis, compilation checks
- **fable** — independent attention patterns, vacuity detection

All three invocations run in parallel. The coordinator then:

1. Collects all findings from all 15 sub-agent reviews
2. Deduplicates findings that describe the same issue across models
3. Annotates each finding with which models flagged it
4. Boosts confidence for findings with cross-model consensus (2+ models agree)
5. Presents a consolidated report with model attribution

The value: **different models have different blind spots.** The union of their
findings catches more than any single model. Unique findings (flagged by only
one model) are where the real signal is — they catch what others miss.

## Arguments

All arguments are passed through to each `bsky:elbow-grease` invocation:

| Argument             | Scope                                         |
|----------------------|-----------------------------------------------|
| *(empty)*            | All uncommitted changes (staged + unstaged)   |
| `pr` or `pr <N>`     | Current branch's PR diff, or PR #N            |
| `branch`             | All commits on current branch vs base          |
| `file <path>`        | Single file, full review                      |
| `files <glob>`       | Multiple files matching pattern               |
| `commit <ref>`       | Single commit diff                            |
| `--since <ref>`      | Incremental: only commits since `<ref>`       |

### Additional flags

| Flag | Meaning |
|------|---------|
| `--models <list>` | Comma-separated model names (default: `opus,sonnet,fable`) |
| `--dispatch <skill>` | Override dispatch backend for all invocations (e.g., `later:multimodel-dispatch` for Cursor CLI) |

## Usage

```
/multimodel-elbow-grease pr 42
/multimodel-elbow-grease branch
/multimodel-elbow-grease file src/main.rs
/multimodel-elbow-grease pr 42 --models opus,fable
```

## Implementation

### Step 1: Parse arguments

Split `$ARGUMENTS` into:
- **review args**: everything that is NOT `--models` or `--dispatch` (passed to elbow-grease)
- **models**: from `--models` or default `opus,sonnet,fable`
- **dispatch**: from `--dispatch` or default (native `bsky:elbow-grease-dispatch`)

### Step 2: Run elbow-grease per model (parallel)

Invoke `bsky:elbow-grease` once per model. All invocations run concurrently.

```
# All three run concurrently via Skill tool:
bsky:elbow-grease <review-args> --model opus [--dispatch <dispatch>]
bsky:elbow-grease <review-args> --model sonnet [--dispatch <dispatch>]
bsky:elbow-grease <review-args> --model fable [--dispatch <dispatch>]
```

Each `bsky:elbow-grease` invocation runs its own Phase 1–4 (gather context,
analyze with 5 sub-agents, deduplicate & verify, report). This produces three
independent review reports.

**Dispatch behavior:** The `--model` flag tells elbow-grease to use that model
for all five sub-agents instead of the default sonnet/opus split. The `--dispatch`
flag, if provided, overrides the dispatch backend for all invocations.

### Step 3: Cross-model synthesis

After all three elbow-grease invocations complete:

1. **Collect** all findings from the three reports
2. **Match** findings across models by file path + line range + issue description.
   Two findings match if they identify the same underlying issue, even if worded
   differently. Use judgment, not exact string matching.
3. **Merge** matched findings into a single entry:
   - Use the clearest description from any model
   - List all models that flagged it: `[opus, sonnet]` or `[all three]`
   - Severity = highest severity any model assigned
4. **Score** by consensus:
   - 3/3 models agree → high confidence, highlight in report
   - 2/3 models agree → medium confidence
   - 1/3 only → lower confidence (but still report — single-model findings
     are where the real value is, since they catch what others miss)
5. **Report** in standard elbow-grease format with an added `Models:` line per finding

### Output format

```
## Multi-Model Code Review: <scope description>

### Cross-Model Consensus

N findings from 15 sub-agent reviews (5 lenses × 3 models)
- N findings flagged by all 3 models (high confidence)
- N findings flagged by 2 models
- N findings flagged by 1 model only

### P1 — Critical (N findings)

**<title>** — `path/to/file.py:42`
Models: opus, sonnet
<description with concrete fix>

### P2 — Important (N findings)
...

### P3 — Suggestions (N findings)
...
```

If there are zero findings at a severity level, omit that section entirely.
If there are zero findings total, say so clearly.

## Relationship to other skills

- **`bsky:elbow-grease`** — the review framework this skill invokes (3× per review)
- **`bsky:elbow-grease-dispatch`** — the native Claude dispatch backend (default)
- **`bsky:review-fix-loop`** — wraps review in an iterative fix loop (optional, separate invocation)

This skill performs a **single review pass** (across 3 models). For iterative
review-fix-converge workflows, use `bsky:review-fix-loop` which can call this
skill repeatedly.

## Constraints

- Use jq over python3 where possible
- Don't run on trivial diffs (< 10 lines changed) — 15 agents is expensive
- If elbow-grease fails for one model, report the failure and synthesize from the remaining models
- Never merge, deploy, or self-certify
