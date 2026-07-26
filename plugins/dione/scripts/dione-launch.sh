#!/bin/sh
# Launch dione for the MCP stdio channel.
#
# Two deployments, one plugin:
#
#   default          run dione here, in this environment. Unchanged behaviour.
#   relay (opt-in)   connect to a dione already running on another host, over an
#                    `ssh -T` byte pipe, when DIONE_RELAY_TARGET is set.
#
# The relay exists for sandboxed constructs: dione holds the Discord bot token,
# and a container that runs dione locally must therefore hold the token too. With
# the relay, dione stays on the host and only a forced-command ssh key enters the
# guest — the token never crosses the boundary. ssh -T is a transparent byte pipe,
# so channel push (dione's inbound delivery) survives it unchanged.
#
# Absent DIONE_RELAY_TARGET this is exactly `dione`, so existing installs see no
# behavioural change.
set -eu

if [ -n "${DIONE_RELAY_TARGET:-}" ]; then
  exec ssh -T \
    -i "${DIONE_RELAY_KEY:-/etc/construct/dione_relay}" \
    -o IdentitiesOnly=yes \
    -o StrictHostKeyChecking="${DIONE_RELAY_HOST_KEY_CHECKING:-accept-new}" \
    -o UserKnownHostsFile="${DIONE_RELAY_KNOWN_HOSTS:-$HOME/.ssh/known_hosts}" \
    "$DIONE_RELAY_TARGET"
  # NOTE: no trailing command. The host's authorized_keys forced-command decides
  # what runs, so anything sent here would be ignored — and relying on it would
  # give a false impression that the guest chooses.
fi

exec dione "$@"
