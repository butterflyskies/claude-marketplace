---
name: review-fix-loop
description: Iterate the exact six-lens multimodel review contract through verified minimal fixes and full-scope re-review until the configured severity threshold is clean or a named budget, ownership, authority, or design exit fires. Use when a nontrivial diff should converge under independent review without implying merge or publication authority.
---

# Review Fix Loop

Codex adaptation of `butterflyskies/claude-marketplace` at
`d29910dc302e8b7008df4b9fdc291a9cc9cad115`.

Run `multimodel-elbow-grease`, fix verified owned findings serially, and
re-review the full target until convergence or an honest exit. Convergence means
the configured review threshold is clean; it never means merged, deployed, or
externally approved.

## Inputs

- target scope accepted by `multimodel-elbow-grease`;
- `max_rounds`, default 5;
- `min_severity`, default P3;
- optional fix model/reasoning profile from the current Codex catalog;
- optional project standards reference;
- optional explicit commit/publication authority.

Parse prose and structured arguments directly. Do not rely on `$ARGUMENTS`,
Claude model names, or `bsky:` namespaces.

## Resolve the target

1. Invoke `$load-design-principles`; stop on a missing or phantom set.
2. Read applicable repository instructions and inspect the dirty worktree.
3. Resolve target, base, and changed-file inventory without checking out another
   branch over user work. Use an isolated worktree when the requested target is
   not already safe to modify.
4. Derive sanctioned identities and environment requirements from current
   authoritative seat/repository configuration; do not load guessed credentials.
5. Load explicit project standards when supplied. Auto-detected memory is
   advisory only after exact identity and scope are verified; a missing standard
   is a named coverage gap, not permission to invent one.
6. Record the exact generic and multimodel skill digests, starting revision,
   owned paths, unrelated changes, threshold, rounds, and write authority.

## Review round

Run the exact staged/live `multimodel-elbow-grease` contract over the **full
resolved target**. Later rounds may focus reviewer attention on the incremental
fix diff, but they must also verify that earlier findings remain resolved and
that fixes did not regress the full target.

Resolve one canonical multimodel skill path for the run, record its SHA-256,
and reject path or digest drift between rounds until explicitly reconciled.
Consume its result only as schema `callisto.multimodel-elbow-grease/v1`.
Validate the whole envelope before fixing, including:

- source revision and generic-contract validation receipt;
- requested/completed `profile × pass × lens` matrix;
- complete and unreviewed lens/file coverage;
- advertised, dispatched, and returned reviewer identities;
- verified findings with stable IDs, source pointers, mechanisms, remedies,
  ownership, verification, profiles, and stability;
- dismissed findings and evidence;
- disagreement notes;
- raw per-cell receipt references;
- authority state, budget/failure status, and continuation data.

Preserve these fields through every round. If any required field is missing,
the schema/digest mismatches, or the upstream status/coverage is incomplete,
return **INCOMPLETE** and never infer convergence. The loop may resume from the
envelope's remaining cells, but may not silently discard successful partial
receipts or disagreements.

Partition verified findings into:

- actionable: at or above threshold and within task ownership;
- noted: below threshold;
- unowned/pre-existing: real but outside the authorized diff;
- dismissed: disproven with evidence;
- escalated: requires a product/design/authority decision.

Carry all five sets into later rounds.

## Fix round

Fix actionable findings serially in severity then file order.

For each finding:

1. Spawn a fresh Codex worker with the finding, canonical code context,
   principles, standards, owned paths, unrelated-change inventory, and current
   authority boundary.
2. Require the smallest change that resolves the verified mechanism without
   changing design intent or repairing other findings opportunistically.
3. Inspect the actual diff. Reject edits outside ownership or overlapping
   unrelated work unless the overlap can be partitioned safely.
4. Run the narrowest relevant formatter, build, static checks, and tests. Report
   exact commands and distinguish executed results from user-reported ones.
5. Commit one finding per commit only when the task authorizes commits and the
   hunk ownership is unambiguous. Otherwise preserve verified local changes and
   record them as uncommitted. Never add a fabricated or inherited coauthor.
6. Escalate rather than force a fix that changes product intent or needs new
   authority.

Do not push merely because a PR exists. Pushes, comments, issues, merges,
deployments, and memory writes each require their own established authority.

## Exit evaluation

After each fix round:

- verify the post-fix revision and worktree state;
- re-run the full review contract;
- increment the round count;
- stop on unresolved P1, design/authority gate, exhausted rounds/budget, unsafe
  overlap, provider failure that leaves required coverage incomplete, or user
  redirection.

Return **CONVERGED** only when the full review contract reports no verified
actionable findings at or above threshold and all required lenses/surfaces were
covered in the final round. Otherwise return **STALLED**, **ESCALATED**, or
**INCOMPLETE**, with the exact remaining work.

## Report

Include:

- target, starting and final revisions, skill/principle digests;
- per-round counts for verified, fixed, new, dismissed, noted, unowned, and
  escalated findings;
- each fix and its test receipt;
- remaining findings and unreviewed coverage;
- exact commit/uncommitted state;
- any authorized push/comment effect separately from local convergence;
- rollback instructions for loop-owned commits or local changes;
- exit reason.

Return the report in-session by default. External publication is a separate
deliberate action.

## Invariants

- Six lenses throughout; Privacy remains distinct from Security.
- Verify before fixing; preserve false-positive dismissals across rounds.
- Serial minimal fixes; fresh context per finding.
- Full-target regression coverage after every round.
- Preserve unrelated user changes and pre-existing findings.
- Never merge or deploy; never infer publication or commit authority.
- Report an incomplete review honestly rather than treating partial zeroes as
  convergence.
