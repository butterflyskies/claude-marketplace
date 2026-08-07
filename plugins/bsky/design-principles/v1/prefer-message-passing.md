# Prefer Message-Passing to Shared Mutable State

Where a design fits it, coordinate concurrent work by passing ownership of data
through channels rather than by sharing a mutable cell behind a lock. Give each
piece of state a single owner; others send it messages. Don't reach for a mutex
when a queue expresses the same intent without the shared-mutation hazard.

**Why:** shared-mutable-plus-locks is where data races, deadlocks, lost wakeups,
and torn invariants live. A message boundary makes ownership explicit and the
concurrency legible — the state is only ever touched by one task, so there's no
interleaving to reason about.

**How to apply:**
- Prefer a channel/actor per piece of mutable state over a lock guarding it
  shared across tasks.
- When a lock is genuinely the right tool, keep the critical section tiny and
  never hold it across an `.await` or a callback.
- Watch for the tell: a `Mutex<HashMap>` touched from many tasks usually wants
  to be one owner draining a queue of requests.

**The tension:** message-passing adds a hop and a queue. For hot, simple shared
reads an atomic or short lock can be the honest choice — apply where it fits, not
dogmatically.

Related: [traits-at-boundaries](traits-at-boundaries.md), [resource-lifecycle](resource-lifecycle.md), [right-altitude](right-altitude.md)
