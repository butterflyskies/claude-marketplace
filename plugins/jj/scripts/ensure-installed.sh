#!/bin/sh
command -v agent-jj >/dev/null 2>&1 && exit 0
echo "Installing agent-jj..." >&2
cargo install --locked agent-jj 2>&1
