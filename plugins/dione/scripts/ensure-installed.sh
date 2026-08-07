#!/bin/sh
# Ensures dione is installed and up-to-date.
# Called as a SessionStart hook — installs or updates from crates.io.
# cargo install no-ops (~1-2s) when already at latest version.

# In relay mode dione runs on ANOTHER host, so there is nothing to install here
# and cargo may not even exist. Installing anyway would waste a minute of every
# session start and fail noisily in a sandbox that deliberately has no toolchain.
if [ -n "${DIONE_RELAY_TARGET:-}" ]; then
  exit 0
fi

cargo install dione --locked 2>&1 || true
