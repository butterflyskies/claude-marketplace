#!/bin/sh
# Ensures agent-jj is installed and up-to-date.
# Called as a SessionStart hook — installs or updates from crates.io.
# cargo install no-ops (~1-2s) when already at latest version.
cargo install agent-jj --locked 2>&1 || true
