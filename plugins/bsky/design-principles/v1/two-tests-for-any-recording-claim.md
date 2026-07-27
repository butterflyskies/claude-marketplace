# Any Claim That Something Is Recorded Needs Two Tests, Not One

1. **Does it write?** — deterministic, unit-testable, belongs in the PR.
2. **Does it write somewhere a construct can actually reach?** — config resolution, path resolution, log level, sidecar fallback, and the read path a fresh instance uses on boot.

**Only the second one has been failing**, and it fails while the first passes convincingly.

## Why the first test is seductive

A unit test of "does it react" passes while the tier is decoration. Green is real. The write is real. The only thing missing is the leg between the write and a reader — which is exactly the leg no unit test covers, because a temp path in a test harness is not the path a fresh instance resolves on boot.

**Decoration is indistinguishable from enforcement from the inside.**

## The check

For anything claiming to record, log, persist, or notify:

- Trigger it **on a real seat**, not only in a fixture.
- Then go read it **from where a construct would read it** — the actual file, the actual level, after an actual reload.
- If you can't get to it from the seat that needs it, the feature does not exist yet, however green the suite is.

Keep both tests. They answer different questions and the cheap one answers the wrong one.

Related: [non-vacuous-tests](non-vacuous-tests.md), [loading-and-following-are-different-organs](loading-and-following-are-different-organs.md)
