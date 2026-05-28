---
name: token-audit
description: "Read session stats, calculate API-equivalent cost, track burn rate vs budget, and project when rate limits will hit. Use when asked about token usage, costs, or budget."
---

# /token-audit — Token Economics Dashboard

Read session stats and surface token economics: what this session costs at API rates,
how fast the budget is burning, and when limits will hit. Useful for budget-aware
operation and understanding the value gap between subscription and API pricing.

## Arguments

`$ARGUMENTS` is optional:

| Input | Action |
|-------|--------|
| *(empty)* | Full report: snapshot + burn rate + projections |
| `snapshot` | Current stats only, no projections |
| `project` | Projections only (when will limits hit?) |
| `history` | Compare against previous sessions if stats are available |

## Phase 1: Read current stats

Read `/tmp/claude-session-stats.json`. The file is written by the statusline hook on
every turn. Extract via `jq`:

```bash
jq '{
  context_pct: .input.context_window.used_percentage,
  rate_5h_pct: .input.rate_limits.five_hour.used_percentage,
  rate_7d_pct: .input.rate_limits.seven_day.used_percentage,
  rate_5h_resets: .input.rate_limits.five_hour.resets_at,
  rate_7d_resets: .input.rate_limits.seven_day.resets_at,
  cost_usd: .input.cost.total_cost_usd,
  duration_ms: .input.cost.total_duration_ms,
  api_duration_ms: .input.cost.total_api_duration_ms,
  model: .input.model.display_name,
  cache_read: .input.context_window.current_usage.cache_read_input_tokens,
  cache_create: .input.context_window.current_usage.cache_creation_input_tokens,
  input_tokens: .input.context_window.current_usage.input_tokens,
  output_tokens: .input.context_window.current_usage.output_tokens
}' /tmp/claude-session-stats.json
```

## Phase 2: Calculate API-equivalent cost

Apply current Anthropic API pricing for the detected model:

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

The `cost.total_cost_usd` field in the stats is the internal cost metric. Calculate
the subscription-to-API multiplier: API-equivalent cost ÷ subscription tier cost.

## Phase 3: Burn rate and projections

Calculate:

- **Burn rate**: `cost_usd ÷ (duration_ms / 3,600,000)` = $/hour
- **Time to 5h limit**: `(100 - rate_5h_pct) × (session_hours / rate_5h_pct)` = hours remaining
- **Time to 7d limit**: same formula with 7d rate
- **Reset times**: convert `resets_at` (unix epoch) to local time via `date -d @<epoch>`
- **Cache efficiency**: `cache_read ÷ (cache_read + cache_create + input_tokens) × 100`
- **Monthly projection**: burn rate × 24 × 30 = $/month at this rate sustained

Flag warnings:
- **5h rate > 80%**: approaching 5h ceiling
- **7d rate > 90%**: close to weekly limit
- **Context > 70%**: compaction territory
- **Cache efficiency < 50%**: cache misses dominating, expensive turn

## Phase 4: Output

Format as a compact dashboard. Post to the requesting channel if invoked from Discord,
or print to terminal otherwise.

```
## Token Audit — {timestamp}

| Metric | Value |
|--------|-------|
| Model | {display_name} |
| Context window | {pct}% ({tokens}k / 1M) |
| 5h rate limit | {pct}% (resets {local_time}) |
| 7d rate limit | {pct}% (resets {local_time}) |
| Session cost | ${cost} |
| Burn rate | ${rate}/hr |
| Cache hit rate | {pct}% |
| API-equivalent | ~${monthly}/mo at this rate |
| Subscription tier | ${tier}/mo |
| Multiplier | {x}x |

### Projections
- 5h limit: {hours}h at current rate
- 7d limit: {hours}h at current rate
- Context compaction: ~{hours}h at current rate

### Warnings
{any flags from Phase 3, or "none"}
```

## Modes

- **snapshot**: skip Phase 3 projections, just print the snapshot table
- **project**: skip the snapshot table, just print projections + warnings
- **history**: read any prior `/tmp/claude-session-stats-history-*.json` files if they
  exist and compare current session against previous ones. If no history files exist,
  fall back to full report mode and note that history is empty.

## Notes

- The stats file is rewritten on every turn — the snapshot reflects the most recent
  statusline render, not necessarily the current moment.
- Subscription tier defaults to $100/mo (Max). For other tiers (Pro $20, Team), the
  multiplier will change but the per-session cost stays the same.
- This skill is read-only and does not call any external APIs.
