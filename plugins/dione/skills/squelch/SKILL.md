---
name: discord:squelch
category: operations
description: Temporary mention-only mode for constructs. Use when a human directs constructs to reduce chatter in a channel/thread — `/squelch <names|none>` or plain prose ("squelch all unless pinged", "everyone but X quiet down"). Triggers on understanding, not exact syntax. Covers parsing who is squelched, applying mention-only mode in scope, and automatically reverting.
---

# /squelch — Temporary Mention-Only Mode

A human can direct constructs to reduce chatter in a channel/thread: `/squelch <names|none>` or plain prose ("squelch all unless pinged", "everyone but X quiet down"). This skill tells a construct how to comply, scope it, and — critically — how to automatically revert.

## Why confirm — no silent state changes

Every squelch state transition is announced in the affected scope, both on ENTER and on REVERT. This is the no-silent-failure principle behind our other skills: a state change the human can't see is a failure mode. A squelch that only half-applied, or a revert that never fired, must be visible — so each transition posts a brief confirmation one-liner, not just a react. (Miranda, 2026-07-21.)

## Invocation forms

- `/squelch` or "squelch all" — every construct in the room squelches (a designated responder may be exempted by the surrounding text).
- `/squelch name1, name2` — the NAMED constructs squelch; others are unaffected.
- Prose directives count. The skill triggers on understanding, not exact syntax.

## Step 1 — PARSE, don't assume (the load-bearing rule)

Read the directive AND its surrounding text to determine, for YOURSELF specifically:

- Am I in the **squelch set** (go quiet) or the **stay set** (designated responder / unaffected)?
- Names may appear as either a squelch-list OR a stay-list depending on phrasing ("squelch everyone but Syne" vs "squelch Syne"). Negations, exemptions, and role assignments ("X answers my questions, others no chatter") are common.
- **If genuinely ambiguous whether you're squelched: ask ONE short clarifying question, then comply with the answer.** (Live lesson, 2026-07-21: a construct inverted "responds to undirected messages" as a typo and bound the opposite rule; the human had meant it literally. One clarifying exchange resolved it. Ambiguity is real — resolve it cheaply, don't guess.)
- Scope: the channel or thread where the directive was issued, unless another scope is named.
- Duration: as specified; **default 1 hour**.

## Step 2 — Apply (if you're in the squelch set)

1. Record the PRIOR state for the scope (e.g. the channel/thread's current `require_mention` value in your transport config, or "behavioral-only" if the scope isn't in your config).
2. Go **mention-only in that scope**: respond only when explicitly @mentioned/pinged. If the scope is a config-managed channel entry, set `require_mention: true`; if not (e.g. a thread you can't config individually), comply behaviorally.
3. Write a small durable **state file** (e.g. `<state-dir>/squelch-state.json`): `{scope_id, prior_state, squelched_at, revert_at, directive_message_id}`. This survives restarts — a rebooted construct must re-read it at boot and keep honoring (or revert, if expired) an active squelch. Session crons die on restart; the state file is the truth.
4. Set a **one-shot revert cron** at now + duration (pinned-time, `recurring: false`), prompt e.g. `Run /squelch-revert for <scope_id>` — or an equivalent one-shot reminder that triggers Step 3.
5. **Post a one-line confirmation that squelch is now in effect** in the affected scope — e.g. "🤐 squelched here until 14:50 PT (mention-only); reverting automatically." State the scope-relative duration/revert-time so it's inspectable. A react (🤐, ✅) MAY accompany the line but does not replace it — the confirmation makes the state transition visible.

## Step 3 — Revert

When the revert cron fires (or on boot, if the state file shows `revert_at` has passed):

1. Restore the recorded prior state (config and/or behavior).
2. Delete the state file (or mark it reverted).
3. **Post a one-line confirmation that squelch has lifted** in the affected scope — e.g. "🔊 squelch lifted; back to normal here." The revert is a state transition too, so it must be visible; a react MAY accompany the line but does not replace it.

Unless **extended**: if the human extends the squelch before expiry, update `revert_at` in the state file and replace the one-shot cron.

## Non-rules

- Squelch limits *chatter*, not duties: cron-driven obligations (heartbeats to your own ops channel, direct tasks from your person, safety flags) continue — in their own channels, not the squelched scope.
- A ping/@mention in the squelched scope is always answerable — that's what mention-only means.
- Squelch is never punitive; it's bandwidth management. Comply gracefully.

## Parameters (per-construct)

State-file location, transport-config mechanism (e.g. dione add_channel/update_channel), cron tool names, ack emoji/style.
