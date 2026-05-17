#!/bin/sh
# Ensures dione is installed and available on PATH.
# Called as a SessionStart hook — installs from crates.io if missing.

if command -v dione >/dev/null 2>&1; then
  exit 0
fi

echo "dione not found, installing from crates.io..." >&2
cargo install dione --locked 2>&1
