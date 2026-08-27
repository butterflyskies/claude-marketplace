# Build at the Right Altitude (YAGNI)

Build for the need in front of you, not for a speculative future. The generality
you add "in case we need it" is code you must carry, test, and reason about now,
to serve a requirement that may never arrive — and when the real requirement
does arrive, it rarely matches the shape you guessed.

**Why:** speculative generality is a standing tax: extra abstraction layers,
config knobs nobody sets, plugin points with one implementation. It obscures what
the code actually does today and makes every change route through machinery that
exists only for an imagined tomorrow.

**How to apply:**
- Solve today's concrete case simply and directly. Add the abstraction when the
  second real caller shows up, not before ([dry](dry.md)'s extraction
  trigger is a *real* second use, not an anticipated one).
- Delete the config flag with one value, the interface with one implementor, the
  "extensible" hook nobody calls.
- Right altitude cuts both ways: too low (copy-paste, no structure) is as wrong
  as too high (framework for a script). Match the structure to the actual
  problem's size.

**The tension:** genuine known-imminent needs and hard-to-change public
interfaces justify designing ahead. YAGNI targets *speculative* generality, not
deliberate, load-bearing foresight.

**Build the structure when something breaks without it, not when you can see it
coming.** Architectural resemblance is not a requirement. Foreseeability is not
evidence.

And the corollary that keeps YAGNI from becoming an excuse: **the decline has to
be revisable on evidence.** When a second implementation produces a real defect,
actually build the abstraction. The rule isn't *never build it* — it's *build it when
something demonstrates the need*, and then actually build it.

Related: [dry](dry.md), [attractive-nuisance](attractive-nuisance.md), [no-dead-code](no-dead-code.md)
