---
name: unsubscribe
category: operations
description: "Unsubscribe from a Discord channel — remove it from dione config. Use when asked to 'unsubscribe from #channel' or 'unsub #channel'."
---

# /unsubscribe — Remove a Discord channel from your feed

Stop receiving messages from a channel entirely.

## Arguments

`<channel>` — a channel name (with or without `#`) or a Discord channel ID.

## Procedure

1. If the argument is all digits, treat it as a channel ID. Otherwise, look up the
   channel by name using `mcp__plugin_dione_dione__list_channels` or
   `mcp__plugin_dione_dione__get_channel`.
2. Use `dione:discord-access` to remove the channel.
3. Confirm: "Unsubscribed from **#channel-name** (no longer receiving messages)."
