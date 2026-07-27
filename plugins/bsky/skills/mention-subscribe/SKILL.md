---
name: mention-subscribe
category: operations
description: "Mention-subscribe to a Discord channel — add it to dione config with require_mention: true. Use when asked to 'mention-subscribe to #channel' or 'mostly-unsub #channel'."
---

# /mention-subscribe — Listen to a channel only when mentioned

Add a channel to your feed but only receive messages that mention you directly.
Useful for high-traffic channels where you want to be reachable but not flooded.

## Arguments

`<channel>` — a channel name (with or without `#`) or a Discord channel ID.

## Procedure

1. If the argument is all digits, treat it as a channel ID. Otherwise, look up the
   channel by name using `mcp__plugin_dione_dione__list_channels` or
   `mcp__plugin_dione_dione__get_channel`.
2. Use `dione:discord-access` to add the channel with `require_mention: true`.
3. Confirm: "Mention-subscribed to **#channel-name** (only @mentions delivered)."
