# Tests Must Be Non-Vacuous

A test earns its place only if it can fail for the right reason. It must assert
the spec — the behavior the code promises — not merely that the code ran, and not
a tautology that restates the implementation. A green test that would stay green
if the feature broke is worse than no test: it's a false guarantee.

**Why:** the value of a test is the failure it would produce when the behavior
regresses. `assert!(result.is_ok())` on a function that can't return `Err`,
`assert_eq!(x, x)`, mocking the very thing under test, snapshot tests nobody
reads — all pass forever and protect nothing. Coverage counts the lines executed,
not the claims verified.

**How to apply:**
- For each test ask: what breakage turns this red? If you can't name one, the
  test is vacuous — fix the assertion or delete it.
- Mutation-test the important paths: if you can flip a `+` to a `-` and every
  test still passes, the tests don't pin the behavior.
- Assert on observable outcomes and the spec's edge cases, not on internal calls
  the implementation happens to make.
- Write the test so it fails first (red), then make it pass — a test never seen
  red is a test never proven to work.

## Five ways a test goes vacuous

Vacuity is not one failure. These are structurally distinct:

**1. Revert-green — the suite passes with the fix removed.**
*Check:* revert the fix, confirm red, restore. Report the pair.

**2. No discriminating power — the test returns the same answer under both hypotheses.**
*Check:* **name the hypothesis your test would falsify, before you run it.** If no
available result would have told you otherwise, you have no test.

**3. Oracle dependence — the checker derives from the thing being checked.**
A round-trip test (write with `Serialize`, read with `Deserialize`) compares a thing
to itself through a symmetric transform — a matched pair of broken derives sails
through green.
*Check:* can the reference move without the subject moving? If not, it's a mirror.

**4. Half-contract coverage — one side of a round trip is tested, the other isn't.**
*Check:* for anything that persists, serializes, or crosses a boundary — test the
return leg, not just the departure.

**5. Structurally-can't-cover — the test looks like it guards the property but its own setup prevents it.**
*Check:* does the setup actually put the system in the state the property is about?

### The unifying defect

**"The thing doing the checking moves with the thing being checked."** Oracle
independence is the property to test for, and it's invisible to coverage metrics,
to green suites, and to the author.

Related: [make-illegal-states-unrepresentable](make-illegal-states-unrepresentable.md), [trace-the-wiring](trace-the-wiring.md), [propagate-dont-swallow](propagate-dont-swallow.md), [two-tests-for-any-recording-claim](two-tests-for-any-recording-claim.md)
