---
name: dispatch-subagent
category: infrastructure
description: "Dispatch a code review sub-agent using native Claude Agent tool. Default dispatch backend for elbow-grease."
---

# /dispatch-subagent — Native Claude Sub-Agent Dispatch

Dispatch a single code-review sub-agent using the Claude Agent tool. This is the
default dispatch backend for `bsky:elbow-grease` and implements the dispatch interface
contract.

This skill is not intended to be called directly by users — it is invoked by
`bsky:elbow-grease` (or any review orchestrator) to run individual review passes.

## Dispatch Interface Contract

Any skill implementing this contract can replace `bsky:dispatch-subagent` as
the dispatch backend for `bsky:elbow-grease`. The contract:

### Input

The caller provides these values in `$ARGUMENTS` as a structured block:

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | Sub-agent role: `correctness`, `design`, `architecture`, `idiomacy`, or `tests` |
| `model` | string | Model to use: `sonnet` for mechanical analysis, `opus` for judgment-heavy review |
| `prompt` | string | The full sub-agent prompt (role-specific review instructions) |
| `diff` | string | The code diff to review |
| `context` | string | Project conventions, symbol overview, caller info, patterns memory |
| `dismissed` | string? | Previously dismissed findings (for multi-round reviews) |

### Output

The sub-agent MUST return findings in this exact format, one per finding:

```
**[P1|P2|P3] <short title>**
- File: `<path>:<line>`
- Issue: <1-2 sentence description>
- Impact: <what breaks, and under what conditions>
- Fix: <concrete fix description>
```

If zero findings, return the literal string `PASS — no findings`.

### Behavioral Requirements

1. The sub-agent MUST be independent — it did NOT write the code and has NOT seen
   the implementation process.
2. The sub-agent MUST NOT modify any files — review only.
3. The sub-agent SHOULD use code exploration tools (Read, Bash with grep/find) to
   verify findings against the actual codebase when available.
4. Precision over recall — false positives erode trust.

## Implementation

This skill dispatches via the Claude Agent tool:

1. Parse `$ARGUMENTS` for role, model, prompt, diff, and context
2. Launch an Agent with:
   - `model`: as specified (sonnet or opus)
   - `prompt`: the provided review prompt, with diff and context appended
   - The agent runs in the background and returns findings
3. Return the agent's output verbatim — the orchestrator handles dedup and verification

## Implementing an Alternative Dispatch Backend

To create a custom dispatch backend (e.g., for a different billing path or model
provider), create a skill that:

1. Accepts the same input fields (role, model, prompt, diff, context, dismissed)
2. Returns findings in the same output format
3. Names itself following the convention `<namespace>:dispatch-subagent`

The orchestrator (`bsky:elbow-grease`) accepts `--dispatch <skill-name>` to swap
backends. The default is `bsky:dispatch-subagent` (this skill).

### Model mapping

Alternative backends may need to map the generic model names (`sonnet`, `opus`) to
provider-specific model IDs. The mapping is the backend's responsibility — the
orchestrator only knows generic names.

Example mapping for a Cursor CLI backend:
- `sonnet` → `claude-4.6-sonnet-medium-thinking`
- `opus` → `claude-opus-4-8-thinking-high`
