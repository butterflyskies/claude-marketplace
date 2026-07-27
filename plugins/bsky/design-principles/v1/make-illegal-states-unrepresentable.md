# Make Illegal States Unrepresentable

Shape the types so a value that violates an invariant cannot be constructed. The
compiler, not a runtime check, is the enforcer — if the bad state has no
representation, no code path can reach it and no test needs to guard it.

**Why:** a validation check protects one call site; a type protects every call
site forever, including the ones not written yet. Bugs migrate to the gaps
between checks. Close the gap by deleting the state.

**How to apply:**
- Replace "a string that must be one of three values" with an enum; "two
  optionals where exactly one is set" with a sum type; "a bool plus a field only
  valid when true" with a variant that carries the field.
- Parse, don't validate: convert unstructured input into a type that witnesses
  its own validity at the boundary, then pass the type inward.
- If you're writing a defensive check deep in the code, ask why a value that
  can't be legal got this far — the fix is usually a tighter type upstream.

Related: [newtypes-over-primitives](newtypes-over-primitives.md), [traits-at-boundaries](traits-at-boundaries.md), [non-vacuous-tests](non-vacuous-tests.md)
