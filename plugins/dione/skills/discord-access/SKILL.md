---
name: discord:access
description: Manage Dione Discord channel access — edit allowlists, add/remove channels, set DM policy. Use when the user asks to allow someone, add a channel, check who's allowed, or change access policy.
---

# /discord:access — Dione Access Management

Manage access control for the Dione Discord channel.

## When to invoke

- User asks to allow/remove a Discord user
- User asks to add/remove a guild channel
- User asks to change DM policy
- User asks who's allowed or what channels are active
- User asks to check pending access requests

## Behavior

1. **Determine config path**: `$DIONE_STATE_DIR/config.toml` or
   `~/.claude/channels/dione/config.toml`

2. **Parse the argument** to determine the action:

| Command | Action |
|---------|--------|
| *(no args)* | Display current access state |
| `allow <user_id>` | Add user snowflake to `access.allow_from` |
| `remove <user_id>` | Remove user from `access.allow_from` |
| `admin <user_id>` | Add user to `access.admins` |
| `unadmin <user_id>` | Remove user from `access.admins` |
| `policy <queue\|drop\|disabled>` | Set `access.dm_policy` |
| `channel add <channel_id> [--no-mention] [--allow id1,id2]` | Add a guild channel |
| `channel rm <channel_id>` | Remove a guild channel |
| `set <key> <value>` | Set a delivery/mention config value |

3. **Edit the config file** using `toml_edit` semantics (preserve comments and
   formatting). Read the current file, modify the relevant section, write back
   atomically.

4. **Display confirmation** showing what changed.

## Display format (no args)

```
DM policy: queue
Allowed users (3): 184695..., 221773..., 339201...
Admins (1): 184695...

Guild channels:
  846209781206941736 — require_mention: true, allow_from: (any)
  912345678901234567 — require_mention: false, allow_from: 184695..., 221773...

Mention patterns: ["(?i)\\bdione\\b"]
```

## Notes

- User IDs are Discord snowflakes (numeric). Enable Developer Mode in Discord
  to copy them (right-click → Copy User ID / Copy Channel ID).
- Changes take effect immediately (config is hot-reloaded per message).
- The `access.admins` list controls who receives permission prompts and access
  request notifications. It's separate from `access.allow_from`.
