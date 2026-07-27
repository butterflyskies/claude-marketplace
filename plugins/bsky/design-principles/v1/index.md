# Design Principles — v1

Canonical design principles for principle-bound skills (code review, design,
develop, and any skill that produces or evaluates code). These files are the
single source of truth — loaded by `bsky:load-design-principles` and injected
into sub-agent prompts.

## Principle inventory

| File | Short name | Domain |
|------|-----------|--------|
| [attractive-nuisance](attractive-nuisance.md) | Attractive Nuisance | System design |
| [callistos-law](callistos-law.md) | Callisto's Law | Cross-agent boundaries |
| [complexity-is-conserved](complexity-is-conserved.md) | Tesler's Law | Engineering judgment |
| [construct-owned-workspaces](construct-owned-workspaces.md) | Construct-Owned Workspaces | Collaboration |
| [dependency-direction](dependency-direction.md) | Dependencies Point Toward Stability | Architecture |
| [dry](dry.md) | Don't Repeat Yourself | Coding standards |
| [fix-the-class](fix-the-class.md) | Fix the Class | Debugging / ratchet |
| [loading-and-following-are-different-organs](loading-and-following-are-different-organs.md) | Loading vs Following | Structure vs intention |
| [make-illegal-states-unrepresentable](make-illegal-states-unrepresentable.md) | Illegal States | Type design |
| [meaningful-identifiers](meaningful-identifiers.md) | Meaningful Identifiers | Self-documentation |
| [mixed-cognition-development-lifecycle](mixed-cognition-development-lifecycle.md) | Mixed-Cognition Lifecycle | Development workflow |
| [newtypes-over-primitives](newtypes-over-primitives.md) | Newtypes Over Primitives | Type design |
| [no-dead-code](no-dead-code.md) | No Dead Code | Hygiene |
| [no-historical-trivia](no-historical-trivia.md) | No Historical Trivia | Comments / documentation |
| [non-vacuous-tests](non-vacuous-tests.md) | Non-Vacuous Tests | Testing |
| [policy-durability](policy-durability.md) | Policy Durability | Decision persistence |
| [prefer-message-passing](prefer-message-passing.md) | Prefer Message-Passing | Concurrency |
| [propagate-dont-swallow](propagate-dont-swallow.md) | Propagate, Don't Swallow | Error handling |
| [public-core-house-overlay](public-core-house-overlay.md) | Public Core, House Overlay | Architecture |
| [representational-security](representational-security.md) | Representational Security | API / schema design |
| [resource-lifecycle](resource-lifecycle.md) | Own the Resource Lifecycle | Resource management |
| [right-altitude](right-altitude.md) | Right Altitude (YAGNI) | Simplicity |
| [solve-for-the-cohort](solve-for-the-cohort.md) | Solve for the Cohort | Collaboration |
| [trace-the-wiring](trace-the-wiring.md) | Trace the Wiring | Testing / safety |
| [traits-at-boundaries](traits-at-boundaries.md) | Traits at Boundaries | Interface design |
| [two-tests-for-any-recording-claim](two-tests-for-any-recording-claim.md) | Two Tests for Recording Claims | Observability |
| [workflow-supervises-inference](workflow-supervises-inference.md) | Workflow Supervises Inference | Process |

## Versioning

The `v1/` directory is the current version. When principles are added, revised,
or retired, the version directory may be bumped. Skills reference the version
directory so that a principle update is an explicit, auditable change.

## Collective-conscious overlay (optional)

These bundled files are the canonical baseline. They work standalone — no
external memory system required.

If you have access to a collective-conscious instance (or equivalent shared
memory), you can overlay local norms on top of these baseline principles by
recalling from CC with the relevant topic. The CC entries for these principles
may contain house-specific worked examples, project-specific applications, or
local amendments that don't belong in the public baseline. The bundled files
are canonical; CC is an optional enrichment layer, not a requirement.

To overlay:
```
recall query: "<principle-name>", scope: "shared"
```
Merge any house-specific guidance with the bundled principle before injecting
into sub-agent prompts.
