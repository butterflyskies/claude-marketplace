---
name: scope-sharpen
description: Decompose an approved design or specification into small, testable implementation atoms with explicit interfaces, dependencies, and coverage. Use when work is too broad or ambiguous for reliable implementation; do not use it to implement the atoms or expand the source scope.
---

# Scope Sharpen

Turn a source specification into an implementation-ready dependency graph. An atom is sharp when a capable implementation agent can complete it in one coherent change without inventing a requirement or asking a material clarifying question.

This is a scoping workflow, not implementation. Load `$bsky-core:load-design-principles` when available and apply the relevant digest because atom boundaries are design decisions.

## Inputs and modes

Establish:

- the source specification, from a local artifact or an exact memory record;
- an optional maximum decomposition depth, defaulting to three;
- whether the user wants independent forward-testing;
- the requested output artifact, defaulting to `atoms.md` only when repository writes are in scope.

A requested model or execution profile is a preference, not a capability claim. Use it only when the active provider exposes it. Never substitute a named model silently or hard-code a provider tier as part of the atom contract.

If the source design is unapproved, contradictory, or missing a decision that changes decomposition, stop with the exact ambiguity. Sharpening must not settle product questions by accident.

## Orient and trace requirements

Read the complete source and its applicable repository instructions. Identify stable requirements, non-goals, invariants, data and trust boundaries, components, interfaces, migrations, configuration, observability, and verification obligations.

Create a requirement inventory before splitting. Give every requirement a stable source reference so coverage and scope can be checked mechanically or by exact citation later. Report the source identity, requirement count, initial component count, and depth limit.

## Decomposition loop

For each candidate piece:

1. Decide whether it can be implemented as one coherent change with a clear oracle and without unresolved design choices.
2. If yes, emit one atom with inputs, outputs, invariants, acceptance test, dependencies, complexity, and parallel-safety.
3. If no, split along real interfaces or independently verifiable behavior. Define the boundary between children and recurse.
4. Remove implementation code from the result. Describe interfaces, behavior, and executable verification commands, but do not write the implementation.
5. At the depth limit, change the decomposition strategy if a better boundary is evident. Otherwise mark `NEEDS DESIGN DECISION` or `NEEDS MANUAL SPLIT`; never force a misleading atom.

An atom must not depend on ambient conversation for its meaning. Include exact file/module or interface targets when known, relevant source requirement IDs, negative behavior, and a falsifiable completion condition. Keep implementation choices open unless the source already fixed them.

## Validate the graph

Before presenting the atoms:

- Coverage: map every source requirement to one or more atoms and flag gaps.
- Scope: map every atom back to source requirements and remove or flag additions.
- Dependencies: verify every referenced atom exists, detect cycles, and distinguish hard prerequisites from parallel-safe work.
- Interfaces: check adjacent atoms agree on ownership, inputs, outputs, failure behavior, and migration ordering.
- Verification: ensure each atom has an observable oracle and that aggregate tests cover cross-atom behavior.
- No-code gate: remove implementation bodies or patches that slipped into the artifact.

Forward-testing is optional. When requested and collaboration agents are available and allowed, give a fresh agent one atom plus only its source constraints and ask for a plan in an isolated workspace. A clarifying question, invented requirement, or missing oracle means the atom is not sharp. Do not let the evaluator implement, publish, or mutate live state. When delegation is unavailable, perform a bounded ambiguity audit and label it as the fallback rather than claiming independent validation.

## Output contract

Produce a DAG containing:

- source identity and generation time;
- requirement coverage count and any gaps;
- a dependency graph;
- one section per atom with a one-sentence outcome, source requirement IDs, complexity, suggested capability profile, inputs, outputs, invariants, test condition, dependencies, and parallel-safety;
- cross-atom integration tests and unresolved design decisions;
- scope-creep and manual-split flags.

Use Mermaid only when it materially improves a nontrivial graph; a compact adjacency list is sufficient otherwise. Keep the artifact free of implementation code. Writing the artifact does not authorize dispatching, committing, pushing, or implementing any atom.

End with atom count, coverage ratio, gap count, scope-creep count, manual-split count, and the next decision or implementation-ready frontier.
