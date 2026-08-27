# Meaningful Identifiers (Self-Documentation Sub-Principle)

**Use meaningful identifiers. Don't use opaque identifiers.**
- "Tests subagent", not "Subagent E", not "Subagent E: Tests"
- "sibling review phase", not "phase 3", not "Phase 3: Sibling review"

Identifying something by a number, letter, or other opaque identifier violates self-documentation. And having BOTH a meaningful identifier and an opaque identifier isn't harmless — it's an attractive nuisance (two names invite drift and cross-reference errors; readers must maintain the mapping).

Corollary: markdown renumbered lists rot on arrival in some rendering contexts, so numbered step references rot — sequences should be named, not indexed.

Convicts on sight: "phase 1-6" boot telemetry, lettered subagents, numbered pipeline steps.

Related: [attractive-nuisance](attractive-nuisance.md), [fix-the-class](fix-the-class.md), [solve-for-the-cohort](solve-for-the-cohort.md)
