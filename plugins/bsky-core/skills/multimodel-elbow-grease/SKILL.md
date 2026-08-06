---
name: multimodel-elbow-grease
description: Run the generic six-lens elbow-grease contract through multiple available Codex model/reasoning profiles, preserve raw profile receipts, deduplicate and verify findings, and report consensus, disagreement, stability, and incomplete coverage honestly. Use for nontrivial diffs where independent attention patterns materially improve review confidence.
---

# Multi-Model Elbow Grease

Codex adaptation of `butterflyskies/claude-marketplace` at
`d29910dc302e8b7008df4b9fdc291a9cc9cad115`.

Run the exact generic six-lens `elbow-grease` contract through several available
reviewer profiles, then synthesize without allowing consensus to replace
verification. The six lenses are **Safety, Design, Security, Privacy, Idiomacy,
and Tests**. Privacy is never folded into Security.

## Inputs

- the same target scopes accepted by generic `elbow-grease`;
- optional `profiles`: available Codex model and reasoning-effort pairs;
- optional `passes` per profile, default 1;
- optional severity threshold and budget.

Resolve model names from the collaboration tool's current advertised catalog.
Never pass Claude model labels or invent availability. The default uses up to
three meaningfully different available profiles. If fewer than two distinct
models exist, say that the run is multi-profile rather than multi-model.

Repeated passes measure sampling stability. Different reasoning efforts on the
same model do not count as independent model agreement.

## Preflight

1. Invoke `$load-design-principles`; stop on a missing or phantom principle set.
2. Resolve the exact generic `elbow-grease` skill path and record its SHA-256.
   Validate it against the pinned generic contract before dispatch:
   - source revision is `d29910dc302e8b7008df4b9fdc291a9cc9cad115`;
   - it assigns exactly six independent lenses named Safety, Design, Security,
     Privacy, Idiomacy, and Tests;
   - Privacy explicitly reviews data minimization, intended audience,
     persistence/retention, aggregation risk, and whether collection should
     exist at all; it does not reduce these questions to authorization;
   - Privacy remedies prefer eliminating unnecessary raw collection or using
     metadata-only/local aggregation. When persistence is necessary, remedies
     require bounded retention and the narrow intended audience. Additional
     ACLs alone do not resolve minimization or retention defects;
   - its result preserves verified/dismissed findings, source coverage, and
     honest incomplete exits.
   Stop as **INCOMPATIBLE_GENERIC** if any assertion is absent or ambiguous.
   The installed five-lens generic skill is not an acceptable fallback.
3. Resolve the target and changed-file inventory once. Preserve unrelated work.
4. Refuse trivial diffs unless the user explicitly wants the expense.
5. Compute the run matrix: `profiles × passes × six lenses`.
6. Bound concurrency by live collaboration slots. Run profile/pass invocations
   serially by default so the invoked generic review can use the remaining
   child slots for its six lenses in waves. Never launch several nested generic
   coordinators that would starve one another. Record actual wave width and
   dispatch order; never claim nonexistent parallelism.
7. Record which profiles, lenses, files, and passes will be covered.

## Run independent reviews

For every profile/pass pair, invoke the exact generic skill contract with:

- the same target snapshot and principle digest;
- one declared model/reasoning profile;
- all six lenses;
- publication disabled unless separately authorized;
- raw results returned to this coordinator.

Do not silently substitute `callisto-elbow-grease`, a five-lens skill, or a
Claude dispatcher. Record results per `profile × pass × lens`, not only per
profile/pass. If one lens fails, preserve the successful five lens receipts and
leave the failed cell open. Continue only when useful and label exact missing
lens/file cells.

## Synthesize

1. Collect raw findings and the per-run surface-coverage receipts.
2. Match findings by underlying mechanism and affected code, not wording alone.
3. Preserve the clearest source pointers and the strongest verified impact.
4. Record every profile/pass that raised each finding.
5. Keep material disagreement visible; do not majority-vote away a unique
   verified finding.
6. Verify consolidated findings against canonical code before reporting them as
   actionable.
7. Carry dismissed false positives forward with their evidence so later passes
   do not rediscover them as new work.

Consensus affects confidence, not severity. Severity follows verified impact.

When `passes > 1`, report within-profile stability (`2/3 passes`). Report
cross-model agreement only across distinct model identifiers; separately show
same-model/profile agreement.

## Output

Return a typed envelope with schema identifier
`callisto.multimodel-elbow-grease/v1`. The envelope must contain:

- target and generic-skill digest;
- principle digest;
- source revision and generic-contract validation receipt;
- advertised model catalog snapshot plus requested, dispatched, and returned
  model/reasoning identities;
- requested and completed `profile × pass × lens` matrix cells;
- complete/unreviewed file and lens coverage for every cell;
- verified findings ordered by severity, each with stable finding ID, source
  pointer, mechanism, impact, remedy, ownership status, verification status,
  profiles, and stability;
- dismissed findings with evidence and stable IDs;
- disagreement notes linked to finding IDs;
- raw per-cell receipt references;
- budget/failure status from `COMPLETE | INCOMPLETE | INCOMPATIBLE_GENERIC |
  FAILED`;
- authority state and local versus externally published state;
- continuation data: immutable target snapshot, completed cells, remaining
  cells, and restart instructions.

Fields are required even when empty. A consumer must reject a missing field or
schema mismatch rather than infer it.

Zero findings is a clean result only when every required lens and surface was
completed. Otherwise say **incomplete review with zero findings in completed
coverage**.

## Constraints

- Do not merge, deploy, self-certify, post, commit, push, open issues, or write
  memory merely because review ran.
- Keep raw profile receipts until synthesis is auditable.
- Warn before `passes > 2` and before any matrix whose estimated cost is
  unusually high for the current budget.
- Never describe six-lens arithmetic incorrectly. Requested work is the count
  of requested matrix cells; completed work is the sum of successful
  `profile × pass × lens` cells, including successful cells from partial pairs.
- A later `review-fix-loop` may consume this result, but does not inherit any
  external-write authority from it. It must consume the complete
  `callisto.multimodel-elbow-grease/v1` envelope, not a prose summary.
