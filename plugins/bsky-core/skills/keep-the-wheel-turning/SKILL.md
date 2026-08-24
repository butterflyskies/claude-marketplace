---
name: keep-the-wheel-turning
description: Advance exactly one eligible item through a shared software-delivery pipeline while yielding to active humans, agents, claims, and CI. Use for a scheduled or explicit pipeline crank, a dry-run selection, or a status scan across ideas, designs, issues, pull requests, deployments, and live verification.
---

# Keep the Wheel Turning

Inspect the pipeline, choose the least-recently-touched eligible item, advance it by one named step, emit a receipt when the configured channel is available, and stop. A crank advances at most one item.

## Modes

- Normal: scan, select, and perform one authorized nudge.
- `--dry-run`: report the selected item and proposed nudge without writes.
- `--status`: report tracked items and current steps without writes.

If required tools, actor verification, or authorization are unavailable, degrade to a read-only result. Do not fabricate an empty queue or a successful nudge.

Normal mode permits writes only when a standing authorization matrix names the allowed transition, write class, actor, and destination. A schedule, configured tool, channel, or repository is not authorization. Without that matrix, perform the selection as a dry run and return a read-only receipt.

## Pipeline

```text
idea → cool idea → design → sibling review → issue → human review →
implementation → PR → independent review → merge-ready → deploy-ready → live test
```

Use step names as identifiers. Read relevant repository instructions and load `$bsky-core:load-design-principles` when available and applicable to the selected nudge.

## Scan and select

Gather open ideas, issues, pull requests, and deployment records from the canonical tools available in the environment. For GitHub, prefer the connected GitHub app for read-only inventory; use `gh` only when project instructions authorize and configure it. Include archived repositories only if explicitly requested.

Sort candidates by their canonical last-activity timestamp ascending. For each candidate, yield when any of these is true:

- another construct or agent has an unexpired claim or recent work;
- a human commented, reviewed, approved, or pushed within the configured freshness window (default one hour);
- CI or another state transition is still in flight;
- the next step requires a permission, identity, or tool that is not available.

Choose the first candidate that clears every gate. Keep fact and inference separate when activity sources disagree.

Before any mutable nudge, atomically claim the exact item and step or reserve an idempotency key in the canonical store. On conflict, rescan from the oldest eligible candidate. After acquiring the claim, re-read canonical activity and state; yield and release the claim if either changed. If the available store cannot provide atomic exclusion, scheduled cranks must remain read-only.

## Advance one step

- `idea → cool idea`: require repeated signal or explicit human interest; let proposals younger than 24 hours breathe.
- `cool idea → design`: use `$design`; claim long work in the shared canonical store when that store is available.
- `design → sibling review`: request review from a different construct or a fresh collaboration agent. The designer cannot certify the design.
- `sibling review → issue`: require completed review; search all issue states before creating anything.
- `issue → human review`: send one clear review request to the relevant human through the configured channel.
- `human review → implementation`: require canonical approval, then use `$develop`; claim long work.
- `implementation → PR`: require committed, pushed implementation and converged self-review; create the PR only through a verified, authorized actor path.
- `PR → independent review`: require passing CI and prior self-review; use `$bsky-core:review-fix-loop` or an equivalent fresh reviewer. The author cannot certify the result.
- `independent review → merge-ready`: when findings are resolved, notify the human merge owner. Never merge.
- `merge-ready → deploy-ready`: after canonical merge confirmation, prepare build, manifest diff, and readiness evidence. Never trigger deployment.
- `deploy-ready → live test`: after canonical deployment confirmation, verify the running service or artifact. A tag or merged commit is not runtime proof.

For substantive design, implementation, or review, use `collaboration.spawn_agent` when available and permitted so the main thread remains responsive. Give the agent a bounded step, owned artifacts, receipts required, and explicit prohibition on unapproved external writes. Do not hard-code a model.

## Claims and receipts

Use short-lived claims for long steps in addition to the atomic pre-mutation reservation. Store owner, item, step, start time, TTL, and clear condition in the canonical shared system. Ignore expired claims; do not infer that a missing claim proves inactivity when other activity evidence exists. Release or disposition the reservation after the nudge so a crash cannot masquerade as completion.

After a real crank, post or return exactly one concise receipt:

```text
🛞 <item> | <step taken> | <title>
🛞 skip | <claim, human, CI, permission, or tool reason> | <title>
🛞 idle | no eligible items found in the inspected sources
```

Use Dione or another channel tool only when it is exposed, the destination is configured, the current thread is correctly bound when required, and the write is within the crank's authorization. If delivery fails, retain the local result and report the failed receipt; do not claim it posted.

## Hard constraints

- Advance at most one item per crank.
- Never merge or deploy.
- Never self-certify.
- Never create duplicate issues.
- Never convert an unsignaled thought into tracked work.
- Never retry the same failed step twice in one crank.
- Never treat an ops post, memory, comment, or tag as a canonical approval or runtime receipt when the owning system says otherwise.
