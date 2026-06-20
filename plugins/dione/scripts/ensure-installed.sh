#!/bin/sh
# Ensures dione is installed and up-to-date.
# Called as a SessionStart hook — installs or updates from crates.io.
# cargo install no-ops (~1-2s) when already at latest version.
cargo install dione --locked 2>&1 || true
