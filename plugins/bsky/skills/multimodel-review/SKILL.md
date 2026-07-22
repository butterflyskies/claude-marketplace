---
name: multimodel-review
category: code-review
description: "Multi-model code review via native Claude agents (default) or Cursor CLI. Runs the same diff through multiple LLMs in parallel and synthesizes findings."
---

# /multimodel-review — Multi-Model Code Review

Run a code diff through multiple LLMs in parallel and synthesize their findings.
Different models have different attention patterns — the union of their findings
catches more than any single model.

## Arguments

`$ARGUMENTS` determines the review target, model selection, and dispatch backend:

| Argument | Meaning |
|----------|---------|
| `<owner/repo>#<PR>` | Fetch PR diff via gh CLI |
| `<file-path>` | Read a local diff file |
| `--models <list>` | Comma-separated model aliases (default depends on dispatch) |
| `--dispatch <backend>` | `claude` (default) or `cursor` |
| `--channel <id>` | Discord channel to post results (default: caller's channel) |

### Model aliases

#### Claude dispatch (default)

Models run via native Claude Agent tool, in **parallel**.

| Alias | Agent `model` param | Provider |
|-------|-------------------|----------|
| `opus` | `opus` | Anthropic |
| `sonnet` | `sonnet` | Anthropic |
| `haiku` | `haiku` | Anthropic |
| `fable` | `fable` | Anthropic |

**Default set:** `opus,sonnet,fable`

Haiku is available for alpha testing (`--models opus,sonnet,fable,haiku`) but
excluded from the default set until data shows it contributes novel findings.

#### Cursor dispatch (`--dispatch cursor`)

Models run via Cursor CLI on the macbook portal (Later billing), **sequentially**.

| Alias | Cursor model ID | Provider |
|-------|----------------|----------|
| `grok` | `cursor-grok-4.5-high` | xAI |
| `grok-low` | `cursor-grok-4.5-low` | xAI |
| `composer` | `composer-2.5` | Cursor |
| `gpt53` | `gpt-5.3-codex-high` | OpenAI |
| `gpt52` | `gpt-5.2-codex-high` | OpenAI |
| `fable` | `claude-fable-5-high` | Anthropic (via Cursor) |
| `opus` | `claude-opus-4-8-high` | Anthropic (via Cursor) |
| `opus-think` | `claude-opus-4-8-thinking-high` | Anthropic (via Cursor) |
| `sonnet` | `claude-sonnet-5-high` | Anthropic (via Cursor) |
| `gemini` | `gemini-3.1-pro` | Google (via Cursor) |

**Default set (cursor):** `grok,composer,opus`

## Execution

### Step 1: Parse arguments

Determine:
- **Target**: PR reference, file path, or branch diff
- **Dispatch**: `claude` (default) or `cursor`
- **Models**: parse `--models` or use backend's default set
- **Channel**: parse `--channel` or use caller's channel

### Step 2: Fetch the diff

**Claude dispatch:**

Use the local gh CLI directly (no macbook portal needed):

```bash
# For a PR
gh pr diff <N> --repo <owner/repo> > /tmp/multimodel-diff.txt

# For a branch
git diff main...HEAD > /tmp/multimodel-diff.txt
```

**Cursor dispatch:**

Use the macbook portal to run gh with the PaceHeartLater account (for Latermedia
access) or the default account (for butterflyskies):

```bash
# Initialize macbook portal MCP session
SESSION=$(curl -s -D - -X POST http://localhost:8902/mcp \
  -H 'Content-Type: application/json' \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"multimodel","version":"1.0"}}}' \
  2>/dev/null | grep -i mcp-session-id | awk '{print $2}' | tr -d '\r\n')
```

Then call `run_command` with:
```
GH_TOKEN=$(gh auth token -u PaceHeartLater) gh pr diff <N> --repo <owner/repo>
```

For butterflyskies repos, omit the `GH_TOKEN=` prefix (default account works).

Write the diff to `/tmp/multimodel-diff.txt` on the macbook via `write_file`.

**For a local file**: read it with the Read tool.

### Step 3: Build the review prompt

The review prompt is the same for both backends:

```
You are a code reviewer. Review the following diff for bugs, security issues,
and correctness problems. Do NOT comment on style, formatting, or minor nits.

For each finding, output exactly this format:
SEVERITY: P1|P2|P3
FILE: <file path>
LINE: <line number or "N/A">
FINDING: <one-line description>
DETAIL: <brief explanation>
---

If you find nothing, output: NO_FINDINGS

Here is the diff:

<DIFF CONTENT>
```

Inline the diff content directly into the prompt.

### Step 4: Dispatch to models

#### Claude dispatch (default) — parallel

Launch ALL selected models simultaneously using the Agent tool. Each Agent call
gets the same prompt with the diff inlined.

```
For each model in the selected set:
  Agent({
    name: "review-<model>",
    description: "Code review via <model>",
    model: "<model>",
    prompt: "<review prompt with inlined diff>"
  })
```

Send all Agent calls in a SINGLE message so they run concurrently. Do NOT
launch them sequentially — parallel execution is the whole point of using
native agents over Cursor CLI.

Collect each agent's output when it completes.

#### Cursor dispatch — sequential

For each selected Cursor model, run via the macbook portal:

```bash
curl ... run_command:
  "cat /tmp/multimodel-review-prompt.txt | cursor agent --model <MODEL_ID> --print --trust --output-format text 2>&1"
```

Use the macbook portal MCP session from Step 2. Set timeout to 120 seconds per
model. Cursor models run sequentially on the macbook (one at a time).

### Step 5: Synthesize

Parse each model's output for the SEVERITY/FILE/LINE/FINDING/DETAIL blocks.
If a model didn't follow the format, extract findings best-effort.

Build a synthesis:

```
## Multi-Model Review: <target>

### Consensus findings (N+ models agree)
<findings that appear in 2+ models' output — match by file + approximate line + similar description>

### Unique findings
<findings from only one model, grouped by model>

### Model coverage
| Model | Findings | Unique | Time |
|-------|----------|--------|------|
| <model 1> | N | N | Ns |
| <model 2> | N | N | Ns |
| ... | ... | ... | ... |

### Raw outputs
<collapsed sections per model, for reference>
```

**Consensus matching**: two findings are "about the same thing" if they reference
the same file within ~10 lines and describe a similar issue. Use judgment, not
exact string matching. When findings agree, present the clearest description and
note which models flagged it.

**Unique findings are the signal.** The whole point of multi-model review is that
one model catches what others miss. Unique findings should be presented prominently,
not buried.

### Step 6: Post results

Post the synthesis to the specified Discord channel via `mcp__plugin_dione_dione__reply`.
If the output is too long for one message (Discord 2000 char limit), split into
multiple messages.

**NDA rule**: if the target is a Latermedia repo, post ONLY to #lain-mundane
(1521280506698797077) or its threads, regardless of where the skill was invoked.

## Macbook portal interaction pattern (cursor dispatch only)

All macbook portal calls go through the selene portal (`mcp__selene-portal__run_command`).
The pattern is curl-over-MCP:

```bash
# Inside a selene-portal run_command:
curl -s -X POST http://localhost:8902/mcp \
  -H 'Content-Type: application/json' \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{
    "name":"run_command",
    "arguments":{"command":"...","token":"$MACBOOK_TOKEN"}
  }}'
```

For `write_file`, use `"name":"write_file"` with `"arguments":{"path":"...","content":"...","token":"..."}`.

Content with special characters must be JSON-escaped. For large diffs, write to a
file on selene first (`python3 -c "import json; ..."` to escape), then pass the
escaped content to the macbook portal's write_file.

## Constraints

- Never post Latermedia code outside #lain-mundane
- Use jq over python3 where possible
- Don't run reviews on trivial diffs (< 10 lines changed)
- If a backend is unavailable (macbook portal down for cursor, Agent tool errors for claude), report and stop
- The review prompt must be self-contained (diff inlined, not referenced)
- Claude dispatch is free (included in Claude Code subscription); Cursor dispatch costs Later money
