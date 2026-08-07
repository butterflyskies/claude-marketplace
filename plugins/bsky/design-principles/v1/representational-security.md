# Representational Security — The Schema Decides What Can Be Claimed

**A field does not merely store information. It offers an interpretation.** Schemas and APIs decide which claims are easy, which distinctions survive, and which event orders can be represented at all.

## The portable lens

> **If a caller can state it but only the system can know it, it should not be a caller-supplied field.**

And the originating question:

> **What does this interface let the caller assert that only the system should be able to establish?**

Both are answerable by inspection.

## The review question set

1. What event does each field **claim occurred**?
2. **Who is allowed to assert** that event?
3. Can the value be **derived by the system** instead of supplied by the caller?
4. Can an **invalid sequence** be represented?
5. Are **two semantically different acts collapsed** into one value?
6. Does **absence** mean false, unknown, not-observed, or not-recorded?
7. What **denominator** is required to interpret the recorded numerator?
8. Can the **intended recipient actually perceive** the output?
9. Do downstream consumers **enforce** the qualifier, or merely **display** it?

Q9 is the one that outlives the rest. A field named `epistemic_status: unverified_self_report` prevents an attentive reader from granting causal dignity — it does not stop a downstream query from dropping the qualifier and treating the adjacent `reason` column as cause.

## The deepest repair — make illegitimate claims unrepresentable

- a caller **cannot mint proof of a verdict** (capability token, not a boolean)
- a model **cannot mint transport authorship** (out-of-band nonce the subject never sees)
- a transformed artifact **cannot lose its parent** (provenance travels with content)
- an authorization **cannot become active without an installation receipt**
- a **numerator cannot masquerade as a rate** without an exposure count

**None of them ask anyone to be more careful. Every one adds a place for a fact to land, or removes a place a false claim could sit.**

Related: [non-vacuous-tests](non-vacuous-tests.md), [two-tests-for-any-recording-claim](two-tests-for-any-recording-claim.md), [make-illegal-states-unrepresentable](make-illegal-states-unrepresentable.md)
