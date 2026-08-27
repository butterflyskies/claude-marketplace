# Dependencies Point Toward Stability

Arrange dependencies so they flow toward the parts that change least: the core
domain and its abstractions. Volatile, replaceable details (I/O, frameworks,
transport, storage) depend on the stable center; the center depends on nothing
outward. When you must cross the grain, invert with an interface the stable side
owns.

**Why:** if a stable module depends on a volatile one, every churn in the detail
ripples into the core. Point the arrows inward and the blast radius of a
detail-change stops at the detail. It also keeps the domain testable in
isolation — no database or network needed to exercise the logic.

**How to apply:**
- The domain defines the interface it needs (`trait Store`); the database module
  implements it. The dependency arrow runs from database -> domain, not the
  reverse.
- Watch for a core type importing a concrete adapter, a framework annotation, or
  a transport struct — that's an arrow pointing the wrong way.
- No dependency cycles between modules: a cycle means neither side is the stable
  one, and nothing can be reasoned about or replaced independently.

Related: [traits-at-boundaries](traits-at-boundaries.md), [make-illegal-states-unrepresentable](make-illegal-states-unrepresentable.md), [right-altitude](right-altitude.md)
