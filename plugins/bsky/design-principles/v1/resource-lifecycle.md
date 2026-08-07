# Own the Resource Lifecycle

Every acquired resource — file handle, socket, lock, task, subscription, temp
file, spawned process — has an owner responsible for releasing it, and the
release is wired to every real exit path, not just the happy one. No leaks, no
double-frees, no cleanup that only runs when nothing goes wrong.

**Why:** a resource freed only on the success path leaks on error, on early
return, on panic, on cancellation. Leaks are the slow kind of bug — fine in the
test, fatal in the process that runs for a week. Explicit, structural ownership
(RAII / `Drop`, `defer`, `with`, try-with-resources) makes release automatic and
exhaustive instead of a discipline you must remember at every return.

**How to apply:**
- Bind cleanup to the resource's scope, not to a manual call you hope every
  branch reaches. Prefer the language's ownership construct over hand-written
  teardown.
- Trace every exit — normal return, error, early break, panic, cancellation,
  shutdown signal — and confirm release fires on each. This is where
  [trace-the-wiring](trace-the-wiring.md) bites: a `Drop` or shutdown flush is only real
  if a live path actually triggers it.
- Give each resource exactly one owner; sharing a handle without clear ownership
  is how double-free and use-after-close happen.

Related: [trace-the-wiring](trace-the-wiring.md), [propagate-dont-swallow](propagate-dont-swallow.md), [traits-at-boundaries](traits-at-boundaries.md)
