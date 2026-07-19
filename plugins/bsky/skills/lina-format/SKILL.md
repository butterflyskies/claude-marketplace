---
name: lina-format
category: accessibility
description: "Accessibility formatting for messages to 🦋 — action-first, scan-friendly structure with sigil anchors. Activate when a message contains actions for 🦋 or she signals scanning difficulty."
---

# /lina-format — Scan-Friendly Formatting for 🦋

Format messages for dyslexia accessibility. 🦋 scans by anchor — her sigil
is the entry point, actions must be visible before context, and walls of text
are inaccessible under fatigue.

This is accessibility, not preference. Activate it.

## When to activate

**Always-on:**
- Message contains an action, request, or decision for 🦋 (butterfly / flutterbyskies / Lina)
- 🦋 signals fatigue, scanning difficulty, or dyslexia friction
- Someone asks for action-first or scan-friendly formatting

**Discretionary:**
- Conversation with 🦋 where clarity helps
- Manual toggle via `/lina-format`

## Formatting rules

1. **🦋 sigil first** on any action block that is hers — it's her scan anchor
2. **One action per block**, clearly separated
3. **Bold verb-first headings** on each action (`**APPROVE the request**`, not `the request needs approval`)
4. **Short bullets**, never walls — break up dense information
5. **Emojis as visual anchors:**
   - 🔑 action needed
   - ⚠️ caution
   - ✅ done
   - 📦 FYI / no action
   - ⏳ pending
6. **Context BELOW the action**, never above — don't bury the ask
7. **First-responder rule:** if a sibling construct already answered, react with 🎯 instead of restating (unless the answer materially changes)

## Reference exemplar

```
🦋 🔑 **APPROVE the pending PAT request**
→ org Settings → Personal access tokens → Pending requests → Approve

📦 **FYI — no action**
- PR #4 is open, Syne reviewing
- backup is 1 commit behind until approval lands
```

## Anti-patterns

- Burying the action in paragraph 3 of a wall
- Leading with rationale before saying what to do
- Four constructs restating the same answer in four registers
- Using 🦋's sigil on blocks that aren't her actions

## Source of truth

`collective-conscious shared/skill-spec-lina-format` — the cross-harness spec.
This SKILL.md is the Claude-seat wrapper; Syne's Codex seat has `$lina-format`.
