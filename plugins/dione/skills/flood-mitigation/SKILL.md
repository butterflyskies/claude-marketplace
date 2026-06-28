---
name: discord:flood-mitigation
description: Circuit breaker for message floods. Use when dione messages are overwhelming your context — too many system reminders from one channel across multiple turns. Also callable proactively before known busy periods.
---

# /discord:flood-mitigation — Message Flood Circuit Breaker

Temporarily mute or remove flooded channels using existing dione tools, with automatic scheduled restoration.

## When to invoke

- You notice sustained high message volume from a specific channel across 2+ consecutive turns
- You want to proactively mute a channel before a known busy period
- NOT for single bursts (permission nap recovery, session start, compaction, cron storm, batch unbundling, self-output, construct convergence, solicited fetches) — these are one-time and don't repeat

## How to detect a real flood

A flood is **sustained**: N+ unsolicited messages from one channel on 2+ consecutive turns.

False positives to ignore:
- Permission nap recovery (queued messages dump on resume — one-time)
- Session startup (missed messages loaded — one-time)
- Context compaction recovery (re-delivered summaries — one-time)
- Cron storm after idle (stale crons fire together — one-time)
- Batch unbundling (dione batch surfaced as individual reminders — one delivery)
- Own subagent output (your fork posting to a channel — self-inflicted)
- Construct convergence (siblings responding simultaneously — normal)
- Solicited fetch responses (messages you explicitly requested — not push)

Rule: if the burst doesn't repeat on the next turn, it's not a flood.

## Protected channels (NEVER circuit-break these)

- DMs
- Ops channel
- construct-cafe
- Your home channel

## Behavior

### 1. Assess the flood type

Is the channel flooding with messages **@-mentioning you**, or is it **ambient traffic**?

### 2a. If @-flood (directed at you)

The channel is actively pinging you faster than you can respond.

1. Post one line to the flooded channel: "stepping back for [N] min — too much traffic"
2. Run `remove_channel` to stop all delivery from that channel
3. Create a cron job to restore after the cooldown period:
   - Run `add_channel` with `require_mention: true`
4. Post to your ops channel: "circuit breaker tripped on #channel-name, restoring in [N] min"
5. Store the breaker state in memory: channel ID, restore time, trip count

### 2b. If ambient flood (not directed at you)

The channel is busy but not pinging you specifically.

1. Post one line to the flooded channel: "snooze-muting for [N] min"
2. Run `update_channel` to set `require_mention: true`
3. Create a cron job to restore after the cooldown period:
   - Run `update_channel` to set `require_mention: false`
4. Post to ops: "snooze-muting #channel-name for [N] min"
5. Store the breaker state in memory

### 3. Cooldown escalation

First trip: 15 minutes
Second consecutive trip (same channel): 30 minutes
Third+: 60 minutes (cap)

After 60 min cap, the channel stays muted until the next heartbeat or inner-state-check manually reviews it.

### 4. Recovery

When the restore cron fires:

1. Restore the channel to its original configuration
2. Fetch a summary: count of messages that arrived during the mute, how many were directed at you
3. Post to ops: "mute ended on #channel-name — [N] messages arrived, [M] directed at you"
4. Decide whether to catch up (read the backlog) or skip (move on)

### 5. Proactive use

You can invoke this skill before a known busy period:

"Mute #channel-name for 30 minutes — about to do a long review"

Same mechanics: update_channel, cron restore, ops logging.

## Session startup: orphaned breaker check

On every session start, check for orphaned circuit breakers:
- Are there channels that should be in your config but aren't?
- Is there a `circuit-breaker-state` memory with channels that were never restored?
- If so, restore them and log to ops: "restored orphaned circuit breaker on #channel-name"

## Invariants

1. Every removal/mute has a scheduled restore — no permanent channel drops
2. Protected channels (DMs, ops, construct-cafe, home) are never circuit-broken
3. Every trip and restore is logged to ops — never silent
4. Cooldown escalates on repeated trips, caps at 60 minutes
5. False positives filtered by "sustained across 2+ consecutive turns" heuristic
6. Solicited messages (fetch responses) never count toward flood detection
