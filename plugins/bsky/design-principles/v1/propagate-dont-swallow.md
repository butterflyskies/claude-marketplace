# Propagate, Don't Swallow

Surface errors; don't silently discard them. An error caught and dropped —
`catch {}` with an empty body, `let _ = fallible()`, `.unwrap_or_default()` over a
real failure, a bare `except: pass` — turns a loud, locatable fault into a quiet
wrong answer that shows up somewhere far away, long after the context is gone.

**Why:** the cost of an error is lowest at its source, where you still know what
was being attempted. Swallowing it trades a clear stack trace for a corrupted
state, a missing record, or a silent no-op that the next layer trusts. Fail loud,
fail early, fail where the information is.

**How to apply:**
- Default to propagating (`?`, rethrow, return the `Result`). Handle an error
  only where you can actually do something meaningful about it.
- If you deliberately ignore one, say why in code — an explicit "this is
  best-effort, loss is acceptable because X," not a silent drop.
- Don't flatten distinct failures into one opaque value; preserve the cause
  (error chains / `source`) so the log names what went wrong.
- Never let a `catch`/`recover` swallow a programming bug (panic, assertion) as
  if it were an expected condition.

Related: [trace-the-wiring](trace-the-wiring.md), [non-vacuous-tests](non-vacuous-tests.md), [resource-lifecycle](resource-lifecycle.md)
