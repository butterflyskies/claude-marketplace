#!/bin/sh
# Launch buzz-bridge for the MCP stdio channel.
#
# Finds bridge.mjs in one of the expected locations and runs it.
# The bridge reads its identity from BUZZ_IDENTITY_FILE or
# ~/.config/buzz/identity by default.
set -eu

# Look for bridge.mjs in order of preference:
# 1. BUZZ_BRIDGE_PATH env var (explicit override)
# 2. Alongside this script's plugin (the Forgejo repo cloned locally)
# 3. Common workspace locations
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -n "${BUZZ_BRIDGE_PATH:-}" ] && [ -f "$BUZZ_BRIDGE_PATH" ]; then
  BRIDGE="$BUZZ_BRIDGE_PATH"
elif [ -f "$SCRIPT_DIR/../bridge.mjs" ]; then
  BRIDGE="$SCRIPT_DIR/../bridge.mjs"
elif [ -f "/workspace/taliesin/bin/buzz-bridge/bridge.mjs" ]; then
  BRIDGE="/workspace/taliesin/bin/buzz-bridge/bridge.mjs"
else
  echo '{"error":"config","message":"bridge.mjs not found. Set BUZZ_BRIDGE_PATH or clone lacuna/buzz-bridge alongside the plugin."}' >&2
  exit 1
fi

BRIDGE_DIR="$(dirname "$BRIDGE")"

# Ensure node_modules exist
if [ ! -d "$BRIDGE_DIR/node_modules" ]; then
  (cd "$BRIDGE_DIR" && npm install --silent) >&2
fi

exec node "$BRIDGE"
