---
name: discord:configure
description: Set up the Dione Discord channel — save the bot token and review access policy. Use when the user pastes a Discord bot token, asks to configure Discord, asks "how do I set this up" or "who can reach me," or wants to check channel status.
---

# /discord:configure — Dione Channel Setup

Configure the Dione Discord MCP channel server.

## When to invoke

- User pastes a Discord bot token
- User asks to configure Discord or set up the bot
- User asks "how do I set this up" or "who can reach me"
- User wants to check current channel status

## Behavior

1. **Determine state directory**: check `DIONE_STATE_DIR` env var, default to
   `~/.claude/channels/dione/`

2. **If token is provided** (user pasted one):
   - Write `token = "..."` to `config.toml` in the state directory
   - Create the directory if it doesn't exist
   - Confirm the token was saved
   - Remind user to launch with `claude --channels plugin:dione@butterflyskies`

3. **If no token provided** (status check):
   - Read and display current `config.toml`
   - Show: dm_policy, allow_from count, admins count, channel count
   - Show whether the bot token is configured (don't display the token itself)
   - If no config exists, guide the user through setup:
     a. Create a Discord application at https://discord.com/developers/applications
     b. Enable Message Content Intent under Bot → Privileged Gateway Intents
     c. Generate a bot token (Bot → Reset Token)
     d. Invite bot to a server (OAuth2 → URL Generator: bot scope + permissions)
     e. Run `/discord:configure <token>` to save it

## Required permissions for bot invite

- View Channels
- Send Messages
- Send Messages in Threads
- Read Message History
- Attach Files
- Add Reactions

## Launch command

```
claude --channels plugin:dione@butterflyskies
```
