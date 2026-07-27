---
name: subscribe
category: operations
description: "Subscribe to a Discord channel — add it to dione config with require_mention: false. Use when asked to 'subscribe to #channel' or 'sub #channel'."
---

# /subscribe — Add a Discord channel to your feed

Subscribe to a channel so all messages are delivered without needing a mention.

## Arguments

`<channel>` — a channel name (with or without `#`) or a Discord channel ID.

## Procedure

1. If the argument is all digits, treat it as a channel ID. Otherwise, look up the
   channel by name using `mcp__plugin_dione_dione__list_channels` or
   `mcp__plugin_dione_dione__get_channel`.
2. Use `dione:discord-access` to add the channel with `require_mention: false`.
3. Confirm: "Subscribed to **#channel-name** (all messages delivered)."
