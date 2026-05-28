---
name: token-audit
description: "Read session stats, calculate API-equivalent cost, track burn rate vs budget, and project when rate limits will hit. Use when asked about token usage, costs, or budget."
---

# /token-audit — Token Economics Dashboard

Read session stats and surface token economics: what this session costs at API rates,
how fast the budget is burning, and when limits will hit. Useful for budget-aware
operation and understanding the value gap between subscription and API pricing.

All math runs in a companion script (`scripts/token-audit.py`) — never inline math
in the conversation, because that requires permission prompts every time.

## Arguments

`$ARGUMENTS` is optional:

| Input | Action |
|-------|--------|
| *(empty)* or `full` | Full report: snapshot + projections + warnings |
| `snapshot` | Current stats only, no projections |
| `project` | Projections + warnings only |
| `bootstrap` | Print statusline setup instructions |

## Phase 1: Run the script

```bash
~/.claude/plugins/<resolved>/skills/token-audit/scripts/token-audit.py <mode>
```

The exact path depends on where the marketplace plugin is installed. The skill
loader sets `$CLAUDE_PLUGIN_ROOT` or similar — use the script path relative to
this SKILL.md's directory.

Environment variables the script reads:
- `TOKEN_AUDIT_STATS` — path to stats file (default: `/tmp/claude-session-stats.json`)
- `TOKEN_AUDIT_TIER` — subscription tier USD/month (default: `100`)

## Phase 2: Handle bootstrap case

If the script outputs the bootstrap instructions (because the stats file is missing),
relay them to the user. The user needs to set up a statusline hook that dumps the
input blob to `/tmp/claude-session-stats.json` on every turn.

The minimal statusline script the bootstrap suggests:

```bash
#!/usr/bin/env bash
input=$(cat)
echo "$input" | jq '{ input: (. // null), updated: now | todate }' \
  > /tmp/claude-session-stats.json
echo "$input" | jq -r '.model.display_name // "claude"'
```

If the user already has a custom statusline, they just need to add the `jq` line
to it.

## Phase 3: Relay the output

The script emits markdown. If invoked from a Discord channel, post the output
verbatim. Otherwise print to the terminal.

For Discord posting, prefer the channel where the request came in. If the request
came from a cron or autonomous trigger, post to `#ari-ops`.

## Pricing reference (for the human reader)

The script's calculations are based on the published Anthropic API rates as of
2026-05. Update the script if rates change.

**Opus 4.6 / Opus 4.7:**
- Input: $15/M tokens
- Output: $75/M tokens
- Cache read: $1.50/M tokens
- Cache creation: $18.75/M tokens

**Sonnet 4.6:**
- Input: $3/M tokens
- Output: $15/M tokens
- Cache read: $0.30/M tokens
- Cache creation: $3.75/M tokens

**Haiku 4.5:**
- Input: $1/M tokens
- Output: $5/M tokens
- Cache read: $0.10/M tokens
- Cache creation: $1.25/M tokens

The script does NOT compute these rates from scratch — it relies on the
`cost.total_cost_usd` field that Claude Code itself reports in the statusline
input, which already reflects current pricing.

## Warnings

The script flags:
- **5h rate > 80%** — approaching ceiling
- **7d rate > 90%** — close to weekly limit
- **Context > 70%** — compaction territory
- **Cache hit < 50%** (when there's meaningful cache traffic) — cache misses dominating

## Notes

- The stats file is rewritten on every turn — the snapshot reflects the most recent
  statusline render, not necessarily the current moment.
- The 7d limit projection compares against session duration, not wall-clock time.
  For long-running sessions across days, the projection is conservative (assumes
  current burn rate continues).
- This skill is read-only and does not call any external APIs.
