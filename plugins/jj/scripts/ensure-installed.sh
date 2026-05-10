#!/bin/sh
missing=""
for bin in agent-jj-guard agent-jj-workspace agent-jj-cleanup; do
  command -v "$bin" >/dev/null 2>&1 || missing="$missing $bin"
done
[ -z "$missing" ] && exit 0
echo "Installing prodagent binaries:$missing" >&2
cargo install --git https://github.com/butterflyskies/prodagent --locked $missing 2>&1
