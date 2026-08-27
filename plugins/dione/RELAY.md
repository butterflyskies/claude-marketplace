# Dione SSH Relay Mode

When `DIONE_RELAY_TARGET` is set, the plugin connects to a dione instance on
another host over an SSH byte pipe instead of running dione locally. The Discord
bot token stays on the host — only a forced-command SSH key enters the guest.

## Host-side setup

### 1. Create a dedicated key pair (on the guest)

```sh
ssh-keygen -t ed25519 -f /etc/construct/dione_relay -N "" -C "dione-relay"
```

### 2. Install the public key on the host

Add to the relay user's `~/.ssh/authorized_keys` with restrictions:

```
from="192.168.64.0/24",restrict,command="/path/to/dione --mcp" ssh-ed25519 AAAA... dione-relay
```

The key parts:

- **`from="..."`** — limit connections to the expected subnet (e.g. container
  NAT range). Adjust for your network.
- **`restrict`** — disables agent/port/X11 forwarding, PTY allocation, and user
  rc execution. This is the broadest single restriction keyword.
- **`command="..."`** — the only command this key can run. The guest's SSH
  invocation sends no trailing command; this forced command is what executes.

`restrict` alone covers forwarding, but `ClearAllForwardings=yes` is also set
client-side as defense in depth.

### 3. Configure the guest environment

Set these variables before the plugin starts (e.g. in the container's env):

| Variable | Required | Default | Description |
|---|---|---|---|
| `DIONE_RELAY_TARGET` | yes | — | SSH destination, e.g. `jim@host.local` |
| `DIONE_RELAY_KEY` | no | `/etc/construct/dione_relay` | Path to the private key |
| `DIONE_RELAY_HOST_KEY_CHECKING` | no | `accept-new` | SSH `StrictHostKeyChecking` value |
| `DIONE_RELAY_KNOWN_HOSTS` | no | `~/.ssh/known_hosts` | SSH `UserKnownHostsFile` path |

For maximum security, preseed the host key in `known_hosts` and set
`DIONE_RELAY_HOST_KEY_CHECKING=yes` to avoid TOFU.

## SSH hardening

The launch script sets:

- **`BatchMode=yes`** — no interactive prompts; fail immediately on auth issues
- **`ConnectTimeout=10`** — don't hang indefinitely on unreachable hosts
- **`ServerAliveInterval=30` / `ServerAliveCountMax=3`** — detect dead
  connections within 90 seconds
- **`ClearAllForwardings=yes`** — client-side forwarding prohibition
- **`IdentitiesOnly=yes`** — only offer the specified key, ignore ssh-agent
