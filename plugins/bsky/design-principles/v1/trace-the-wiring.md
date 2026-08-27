# Trace the Wiring, Not Just the Unit Test

A safety, cleanup, or fallback mechanism is only real if a real code path
triggers it. A unit test proves the mechanism works *when invoked* — it says
nothing about whether production ever invokes it. A tested-but-unreachable safety
net is worse than none: it buys false confidence while the hole stays open.

**Why:** the dangerous gaps live in the layer the test doesn't reach — the exit
path that skips the trigger, the token nobody fires, the handler whose `break`
jumps over the flush. Coverage of the mechanism and coverage of its *wiring* are
different claims; passing the first while failing the second is exactly how a
"guaranteed" drain silently loses data.

**How to apply:**
- For any safety/cleanup/drain/rollback, don't stop at "is it tested?" Ask "what
  real path triggers it, and is that path exercised?"
- Follow the trigger backwards to every entry and exit: normal return, EOF,
  SIGTERM, panic, error return, cancellation. If any real exit skips it, the net
  has a hole the unit test can't see.
- Distrust a comment that asserts a signal "was already sent" — verify it fires
  on *this* path, don't take the annotation's word.
- This is the class of gap an independent review pass exists to catch: the core
  logic can be airtight while every surviving bug lives in a layer it didn't
  reach.

Related: [resource-lifecycle](resource-lifecycle.md), [non-vacuous-tests](non-vacuous-tests.md), [propagate-dont-swallow](propagate-dont-swallow.md), [fix-the-class](fix-the-class.md)
