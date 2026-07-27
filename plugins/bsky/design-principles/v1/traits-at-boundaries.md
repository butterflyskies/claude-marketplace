# Traits at Boundaries

Put meaningful component boundaries behind explicit contracts. If two
implementations can serve the same role — or a boundary owns durable state or an
external dependency — define the contract on the stable/domain side.

**Why it matters:**
- Swappable implementations for differential testing (EWMA vs windowed median, constant vs adaptive hazard)
- Clean interface boundaries — the CPD doesn't know how rates are estimated, it just calls `rate_estimate()`
- Stateless pure functions where possible — the trait defines what you get and what you return
- Newtype discipline — `BranchId`, `ChannelId`, not bare `u64`
- Stateful/external implementations (database, queue, clock, filesystem, provider, harness) cannot leak the first implementation's accidental semantics into the domain

**Stateful boundary requirements:**
- Document consistency, ordering, idempotency, retry, failure, and transaction semantics in the contract.
- Test every implementation with a shared conformance suite.
- A concrete first implementation (for example SQLite) is fine; callers depend on the contract, not the concrete store.
- Avoid speculative traits around pure/local code with no plausible second implementation, external seam, state semantics, or needed fake. Asking the boundary question is mandatory; adding ceremony is not.

**Conversion at boundaries:** prefer standard conversion traits (`From`/`Into`) over manual transformation functions at each call site. When data crosses a boundary (API layer -> domain, domain -> persistence, parsed input -> validated type), implement `From`/`Into` on the types so the conversion is encoded in the type system, discoverable, and testable in isolation. Mapped to other languages: TypeScript type guards and mapping functions with consistent signatures, Python `@classmethod` constructors and `__init__` overloads.

**The principle:** if you're tempted to write a concrete component, ask whether a contract boundary would make the design more testable, explicit, and swappable. For stateful or external components, the answer is normally yes. For trivial pure internals, require a real seam before abstracting.

Related: [dependency-direction](dependency-direction.md), [public-core-house-overlay](public-core-house-overlay.md)
