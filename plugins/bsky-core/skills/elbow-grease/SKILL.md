---
name: elbow-grease
description: "Perform systematic, evidence-backed code review of a pull request, branch, diff, commit, or selected files through six independent lenses: Safety, Design, Security, Privacy, Idiomacy, and Tests. Use when the user asks for review, risk analysis, defect finding, or an independent quality/security/privacy pass and wants verified findings rather than automatic fixes."
---

# Elbow Grease

Review a bounded change through six independent lenses, verify every reported defect against the actual code, and return actionable findings. This skill is review-only unless the user separately authorizes fixes or external writes.

Read [lenses.md](references/lenses.md) before dispatching reviewers.

## Establish the review surface

1. Read repository instructions and inspect the worktree without disturbing unrelated changes.
2. Resolve the requested target: pull request, branch, commit, diff, or named files. If the target is implicit, use the current local diff and say so. For cross-seat or independent acceptance review, require a pushed remote ref and bind the review to its fetched full commit SHA and full base SHA. Use the handoff: `Review remote branch <name> at exact commit <full SHA> over exact base <full SHA>.` A local path, pasted/reconstructed diff, or mutable branch name alone is not review authority. Verify the fetched object before review; any successor SHA invalidates the prior receipt.
3. Read the raw diff plus enough surrounding code to understand callers, configuration, schemas, tests, resource lifecycles, and trust boundaries. A diff is evidence, not the whole system.
4. Load `$bsky-core:load-design-principles` when available and materially applicable. Recall project review patterns only when their memory server is exposed; mark recalled memories applied after use.
5. Record scope, requirements or intended behavior, repository state, and verification commands. Separate observed facts from inference.
6. Locate the governing scope packet and record its owner, requirements, non-goals, permitted surfaces, and starting footprint. If none exists, report **NO GOVERNING SCOPE PACKET**. Continue evidence-gathering if useful, but do not infer scope authority from the diff or prescribe an architectural expansion as required work.

For changes larger than roughly 500 lines, tell the user and divide the review into logical slices while preserving one final cross-cutting pass.

## Run six independent lenses

Use one fresh `collaboration.spawn_agent` reviewer per lens when agents are available and delegation is permitted. If concurrency is limited, run them in waves; do not merge lenses or expose one reviewer's suspected findings to another before independent analysis.

Give every reviewer:

- the same raw target and intended behavior;
- relevant repository instructions and boundaries;
- one named lens from `references/lenses.md`;
- permission for read-only inspection and safe, non-mutating verification only;
- a requirement to cite file and line, explain the failure mechanism and impact, and propose a concrete remedy;
- a requirement to return no finding when the claim cannot be supported.

Do not hard-code a model or claim cross-model coverage unless distinct models actually ran. The coordinator owns synthesis and cannot outsource verification.

If collaboration agents are unavailable, perform six explicitly separated passes in the same order and disclose that independence was limited.

## Verify and deduplicate

For every candidate finding:

1. Read the cited implementation and relevant callers or consumers.
2. Reproduce the behavior with the narrowest safe command, test, or counterexample when practical.
3. Reject style preferences, speculative risks without a reachable mechanism, duplicates, out-of-scope pre-existing defects, and claims contradicted by repository contracts.
4. Check sibling operations for the same defect shape.
5. Track dismissed findings with a short reason so the same claim is not rediscovered during synthesis.

A severe label requires severe, reachable impact. Use:

- **Critical**: immediate catastrophic security, privacy, integrity, or availability risk.
- **High**: likely major harm, data loss, privilege failure, or core behavior break.
- **Medium**: material correctness, reliability, maintainability, or test gap with a concrete failure path.
- **Low**: bounded defect or hardening opportunity worth fixing, not a preference.

## Classify scope disposition

Assign every verified finding exactly one disposition, independently of severity:

- `in_scope_fix`: the smallest remedy maps directly to an approved requirement and remains within permitted surfaces.
- `bounded_in_scope_mitigation`: a contained mitigation preserves approved semantics without taking on the broader systemic remedy.
- `separate_prerequisite_or_followup`: the defect is real, but its remedy belongs in separately owned work; it blocks this change only when the scope owner explicitly makes it a prerequisite.
- `scope_revision_required`: the remedy changes approved architecture or product semantics, adds a public/operator tool, persistent artifact, protocol, state machine, or new subsystem, reverses a non-goal, or absorbs a systemic defect shared by existing features.

Severity proves urgency and impact; it does not authorize expanded scope. For every `scope_revision_required` finding, emit this block verbatim and stop before implementation:

> **SCOPE EXPANSION: STOP.** The finding is valid, but fixing it here changes the architecture or expands the agreed scope. I am stopping. Proposed next state: record targeted issues, decide priority and blocking status, then either resume the original slice under unchanged semantics or supersede it with an explicitly approved scope.

The reviewer may describe bounded and systemic remedy options, but must return the choice to the recorded scope owner.

## Report

Put verified findings first, ordered by severity. Each finding must include:

```text
[Severity] Short title
Location: path/to/file.ext:line
Lens: Safety | Design | Security | Privacy | Idiomacy | Tests
Disposition: in_scope_fix | bounded_in_scope_mitigation | separate_prerequisite_or_followup | scope_revision_required
Scope evidence: requirement/non-goal reference, or missing-packet statement
Mechanism: what the code does and how the failure is reached
Impact: observable consequence
Remedy: smallest concrete correction
Evidence: command, test, trace, or code path used to verify it
```

Then report open questions, verification gaps, and a compact scope summary including disposition counts and any scope stop. Include a completion receipt such as `Lens coverage: Safety ✓ · Design ✓ · Security ✓ · Privacy ✓ · Idiomacy ✓ · Tests ✓ (independent agents)`; identify `single-coordinator degraded` instead when fresh agents were unavailable. If no finding survives verification, say `Zero verified findings` and name the residual limits of the review.

Do not edit code, commit, push, open or modify a pull request, post review comments, create issues, or mutate shared memory unless the user explicitly authorizes that distinct action. Passing review is not authorization to merge or deploy.
