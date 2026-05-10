#!/bin/sh
command -v cc-toolgate >/dev/null 2>&1 && exit 0
echo "cc-toolgate not found, installing from crates.io..." >&2
cargo install cc-toolgate --locked 2>&1
