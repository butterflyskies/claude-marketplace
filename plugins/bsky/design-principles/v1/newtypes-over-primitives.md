# Newtypes Over Primitives

Give each domain concept its own type. `BranchId`, `ChannelId`, `Millis` — not
bare `u64`; `Email`, not bare `String`. A primitive says "some number"; a newtype
says what the number means and refuses to be confused with a different one.

**Why:** primitive obsession lets the type system wave through argument-order
swaps, unit mix-ups, and unvalidated values — the exact bugs types exist to
catch. A newtype turns a whole class of "passed the wrong id" mistakes into
compile errors, and gives validation a single home (the constructor).

**How to apply:**
- When two values of the same primitive type mean different things, wrap each.
  If swapping them compiles, you need newtypes.
- Put the invariant in the constructor: a `Percent` that can't hold 150, an
  `Email` that's parsed once at creation.
- Use the newtype as the boundary contract — construct at the edge, pass the
  type inward, never re-parse.

Related: [make-illegal-states-unrepresentable](make-illegal-states-unrepresentable.md), [traits-at-boundaries](traits-at-boundaries.md), [meaningful-identifiers](meaningful-identifiers.md)
