#!/usr/bin/env python3
"""token-audit — read session stats and emit a markdown dashboard.

Reads from /tmp/claude-session-stats.json (or $TOKEN_AUDIT_STATS) — populated by
the Claude Code statusline hook on every turn. Calculates API-equivalent cost,
burn rate, and projections.

Usage:
    token-audit.py [full|snapshot|project|bootstrap]

Environment:
    TOKEN_AUDIT_STATS  — path to stats file (default: /tmp/claude-session-stats.json)
    TOKEN_AUDIT_TIER   — subscription tier $/mo (default: 100)
"""
import json
import os
import sys
from datetime import datetime, timezone

STATS_FILE = os.environ.get("TOKEN_AUDIT_STATS", "/tmp/claude-session-stats.json")
SUB_TIER_USD = float(os.environ.get("TOKEN_AUDIT_TIER", "100"))

BOOTSTRAP = """# Statusline bootstrap required

`token-audit` reads session stats from `/tmp/claude-session-stats.json`, which is
populated by the Claude Code statusline hook on every turn.

If you don't have a custom statusline, set one up by adding this to your
`~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline-token-audit.sh"
  }
}
```

Then create `~/.claude/statusline-token-audit.sh`:

```bash
#!/usr/bin/env bash
input=$(cat)
echo "$input" | jq '{ input: (. // null), updated: now | todate }' \\
  > /tmp/claude-session-stats.json
# Print whatever you want as your statusline; the goal is just to dump stats.
echo "$input" | jq -r '.model.display_name // "claude"'
```

Make it executable: `chmod +x ~/.claude/statusline-token-audit.sh`

If you already have a custom statusline, just add the jq line to it. The file
structure is the full statusline `input` blob wrapped in
`{ input: ..., updated: ... }`.

After the next turn, `/token-audit` will work.
"""


def fmt_time(epoch):
    if not epoch:
        return "unknown"
    try:
        dt = datetime.fromtimestamp(int(epoch)).astimezone()
        return dt.strftime("%-I:%M %p %Z")
    except (ValueError, OSError):
        return "unknown"


def load_stats():
    if not os.path.exists(STATS_FILE):
        print(BOOTSTRAP)
        sys.exit(0)
    with open(STATS_FILE) as f:
        return json.load(f).get("input", {})


def extract(stats):
    ctx = stats.get("context_window", {})
    usage = ctx.get("current_usage", {})
    rl = stats.get("rate_limits", {})
    cost = stats.get("cost", {})
    return {
        "model": (stats.get("model") or {}).get("display_name", "unknown"),
        "context_pct": ctx.get("used_percentage", 0) or 0,
        "ctx_size": ctx.get("context_window_size", 1_000_000),
        "total_input": ctx.get("total_input_tokens", 0) or 0,
        "rate_5h_pct": (rl.get("five_hour") or {}).get("used_percentage", 0) or 0,
        "rate_7d_pct": (rl.get("seven_day") or {}).get("used_percentage", 0) or 0,
        "rate_5h_resets": (rl.get("five_hour") or {}).get("resets_at"),
        "rate_7d_resets": (rl.get("seven_day") or {}).get("resets_at"),
        "cost_usd": cost.get("total_cost_usd", 0) or 0,
        "duration_ms": cost.get("total_duration_ms", 0) or 0,
        "cache_read": usage.get("cache_read_input_tokens", 0) or 0,
        "cache_create": usage.get("cache_creation_input_tokens", 0) or 0,
        "input_tokens": usage.get("input_tokens", 0) or 0,
    }


def compute(d):
    hours = d["duration_ms"] / 3_600_000 if d["duration_ms"] else 0
    burn = d["cost_usd"] / hours if hours > 0 else 0
    monthly = burn * 24 * 30
    multiplier = monthly / SUB_TIER_USD if SUB_TIER_USD > 0 else 0

    cache_total = d["cache_read"] + d["cache_create"] + d["input_tokens"]
    cache_hit = (d["cache_read"] / cache_total * 100) if cache_total > 0 else 0

    def time_to(target, current, denom=None):
        denom = denom if denom is not None else current
        if denom <= 0:
            return None
        return (target - current) * (hours / denom)

    t_5h = time_to(100, d["rate_5h_pct"])
    t_7d = time_to(100, d["rate_7d_pct"])
    t_ctx = time_to(70, d["context_pct"]) if 0 < d["context_pct"] < 70 else None

    return {
        "hours": hours,
        "burn": burn,
        "monthly": monthly,
        "multiplier": multiplier,
        "cache_hit": cache_hit,
        "t_5h": t_5h,
        "t_7d": t_7d,
        "t_ctx": t_ctx,
    }


def warnings(d, c):
    out = []
    if d["rate_5h_pct"] > 80:
        out.append(f"**5h rate {d['rate_5h_pct']:.0f}%** — approaching ceiling")
    if d["rate_7d_pct"] > 90:
        out.append(f"**7d rate {d['rate_7d_pct']:.0f}%** — close to weekly limit")
    if d["context_pct"] > 70:
        out.append(f"**Context {d['context_pct']:.0f}%** — compaction territory")
    cache_total = d["cache_read"] + d["cache_create"] + d["input_tokens"]
    if cache_total > 1000 and c["cache_hit"] < 50:
        out.append(f"**Cache hit {c['cache_hit']:.0f}%** — cache misses dominating")
    return out


def print_snapshot(d, c):
    total_input_k = d["total_input"] / 1000
    ctx_size_m = d["ctx_size"] / 1_000_000
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| Model | {d['model']} |")
    print(f"| Context window | {d['context_pct']:.0f}% ({total_input_k:.0f}k / {ctx_size_m:.1f}M) |")
    print(f"| 5h rate limit | {d['rate_5h_pct']:.0f}% (resets {fmt_time(d['rate_5h_resets'])}) |")
    print(f"| 7d rate limit | {d['rate_7d_pct']:.0f}% (resets {fmt_time(d['rate_7d_resets'])}) |")
    print(f"| Session cost | ${d['cost_usd']:.2f} |")
    print(f"| Burn rate | ${c['burn']:.2f}/hr |")
    print(f"| Cache hit rate | {c['cache_hit']:.2f}% |")
    print(f"| API-equivalent | ~${c['monthly']:.0f}/mo at this rate |")
    print(f"| Subscription tier | ${SUB_TIER_USD:.0f}/mo |")
    print(f"| Multiplier | **{c['multiplier']:.1f}x** |")


def print_projections(c):
    print("### Projections")
    if c["t_5h"] is not None:
        print(f"- 5h limit: {c['t_5h']:.1f}h at current rate")
    if c["t_7d"] is not None:
        print(f"- 7d limit: {c['t_7d']:.1f}h at current rate")
    if c["t_ctx"] is not None:
        print(f"- Context compaction (70%): {c['t_ctx']:.1f}h at current rate")


def print_warnings(w):
    print("### Warnings")
    if not w:
        print("none")
    else:
        for line in w:
            print(f"- {line}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode == "bootstrap":
        print(BOOTSTRAP)
        return

    stats = load_stats()
    d = extract(stats)
    c = compute(d)
    w = warnings(d, c)
    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")

    if mode == "full":
        print(f"## Token Audit — {ts}\n")
        print_snapshot(d, c)
        print()
        print_projections(c)
        print()
        print_warnings(w)
    elif mode == "snapshot":
        print(f"## Token Snapshot — {ts}\n")
        print_snapshot(d, c)
    elif mode == "project":
        print(f"## Token Projections — {ts}\n")
        print_projections(c)
        print()
        print_warnings(w)
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        print("Valid modes: full, snapshot, project, bootstrap", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
