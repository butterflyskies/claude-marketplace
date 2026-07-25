---
name: pulse
category: operations
description: "During-session continuity pulse for constructs — periodic vitals from the session stats source, cursor-based sweep of watched channels, a memory pass that banks anything a future session needs, and a pinned-format status post to an ops channel. The middle leg of the construct lifecycle trio (construct:init → construct:pulse → construct:land). Run on the pulse cron fire or when asked for a heartbeat/pulse. STARTER SKILL — copy it, fill in the parameter block, and author the voice as your own."
---

# /construct:pulse — during-session continuity upkeep

The middle leg of the construct continuity trio:

- **construct:init** — boot: load identity, read handoff, orient.
- **construct:pulse** (this skill) — during-session upkeep, on a cron.
- **construct:land** — pre-clear: reflect, write back, verify, hand off.

The pulse exists so that landing is cheap and a mid-session compaction is
survivable. If every consequential thing is banked within one pulse interval
of happening, losing the session costs you at most one interval — not the
whole day. A construct that only writes memory at landing is one crash away
from amnesia.

**This is a starter skill.** The mechanics below travel; the content and
voice do not. Copy this file into your own skill, fill in the parameter
block, and rewrite the summary voice, sigil, and judgment calls as your own.
(Lineage: extracted from Vesper's battle-tested `/heartbeat` — Lacuna
household, 2026-07.)

## Parameters (fill these in when instantiating)

| Parameter | What it is | Example |
|-----------|------------|---------|
| `MEMORY_SCOPE` | Your memory-store scope for banked state | `vesper` |
| `OPS_CHANNEL` | Channel ID for the status post | a Discord channel ID |
| `WATCHED_CHANNELS` | Name→ID table of channels to sweep | 2–5 channels typically |
| `CURSOR_FILE` | Persisted per-channel sweep cursors | `~/workspace/<you>-state/pulse-cursors.json` |
| `STATS_SOURCE` | Where session vitals are written | `/tmp/claude-session-stats.json` (statusline hook) |
| `CADENCE` | Cron schedule for the pulse | hourly at an off-peak minute |
| `SIGIL` / voice | The emoji + tone of your status post | 🫀, 🐌, whatever is yours |

**Cadence collision-avoidance:** pick a minute nobody else in your household
uses (`:53`, `:17` — not `:00`). Multiple constructs pulsing on the same
minute stack load on shared infrastructure and interleave their posts.
Recreate the cron at boot (that's construct:init's job); list existing crons
first so duplicates don't fire twice.

## Phase 1 — Vitals (always first)

Read the current time and session stats from `STATS_SOURCE`. Typical fields:
model, context tokens/percentage, rate-limit windows and reset times, session
cost, and the file's own `updated` timestamp. Prefer `jq` for the extraction.

Two hard rules:

- **Never state a time or number you haven't just read.** No remembered
  values, no guesses, no "probably about".
- **Staleness is data.** If `updated` is older than ~15 minutes or the file
  is missing, the stats mechanism isn't firing — post the pulse anyway with
  the affected fields marked `(stale)` or `(unavailable)` and name the cause.

## Phase 2 — Sweep (judgment lives here)

Fetch ONLY what is new in each watched channel. Token efficiency is a
requirement, not a preference: use a since-cursor fetch (e.g.
`fetch_new_since(channel_id, after_message_id)`), never a full-history fetch
that re-downloads already-swept messages every pulse.

Cursor discipline:

- `CURSOR_FILE` maps `{"<channel_id>": "<last-swept message id>"}`. Treat
  IDs as **strings** — snowflake IDs exceed double precision; never do
  arithmetic on them in jq.
- Missing file or missing key → synthesize a reasonable starting cursor
  (e.g. a 1-hour-ago snowflake, computed 64-bit-safe in bash).
- Paginated response (`has_more`) → keep paging from the last returned id.
- Empty result → nothing new; leave that cursor unchanged.
- After sweeping, persist the updated cursors so the next pulse (possibly in
  a different session) starts where this one ended.

Respond only where it adds something or corrects something. Reactions count
as presence. The pulse records that you were here — it does not require
speech.

## Phase 3 — Memory pass (the load-bearing phase)

Before posting, ask: **did anything happen since the last pulse that a
future session needs?** Decisions made, feedback received, designs settled,
state changed, promises given. If yes, bank it to your memory store **now**
— not at landing, now. This phase is why the skill exists; the other three
are its scaffolding.

Discipline:

- **Read before edit.** Session context is a subset of what's stored;
  editing a memory you haven't read this session overwrites content you
  never loaded.
- **Verify the write.** Read back what you banked and confirm it says what
  you meant. Writing ≠ surviving (Callisto's durable-write-verification
  principle) — a write you didn't read back is a write you only believe
  happened.
- Don't bank what's derivable from code, git, or config — bank the things
  only this session knows.
- The Memories section of the status post records what you banked (or
  `none`). It is not optional; an honest `none` is a real answer, a missing
  section is not.

## Phase 4 — Status post → `OPS_CHANNEL`

The format is **pinned**: same shape every pulse, every session. Format
drift between sessions is the failure this phase exists to prevent — a
reader (including future-you) should be able to scan a month of pulses as
one table. Judgment stays in the Summary content only.

Exactly this shape, in this order — info bar, then `###` Summary, then
`###` Memories:

```
<SIGIL> `<HH:MM> <TZ> | <Model> | ctx <N>K (<P>%) | <rate-limit windows with reset times> | session $<C>`
### Summary
<1–3 plain lines — what happened since the last pulse, threads engaged, work shipped, who's active. No meta, no filler, no "all quiet" padding beyond one clause.>
### Memories
- `<memory-name>` — <what changed>
```

When nothing was banked:

```
### Memories
none
```

The info bar is code-formatted (backticks, sigil outside them) with ` | `
separators. Memory bullets name the memory in backticks, then a clause on
what changed.

## Failure modes

- **Stats missing/stale** → post the pulse with `(stale)`/`(unavailable)` on
  the affected fields and name the cause. Never skip the pulse, never
  substitute remembered numbers.
- **Transport to `OPS_CHANNEL` down** → print the full status to the
  terminal instead; retry on the next pulse.
- **A sweep response feels borderline** → hold, or react instead of posting.
  The pulse records presence; it doesn't require speech.
