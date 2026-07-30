---
name: keep-the-wheel-turning
category: pipeline
description: "Cron-driven pipeline advancer. Scans open work across butterflyskies org and pushes the least-recently-touched item one step forward. One nudge per crank, never stops."
---

# /keep-the-wheel-turning — Pipeline Advancer

Scan all open work across butterflyskies org. Pick the stalest item. Push it one step
forward. Stop. The rotation (three constructs, staggered) means everything gets a turn.
The wheel doesn't need to be fast — it needs to never stop.

If a `required-environment-variables` memory exists (scope: global), read and apply it
before any git/gh operations.

**This is a principle-bound skill.** First invoke `bsky:load-design-principles`
and pass the returned digest to sub-agents for whichever step is being cranked.

## Arguments

`$ARGUMENTS` is optional:

| Argument | Meaning |
|----------|---------|
| *(empty)* | Normal crank — scan, pick, nudge |
| `--dry-run` | Scan and report what would be nudged, don't act |
| `--status` | Show pipeline status for all tracked items |

## The Pipeline

Every work item moves through these steps. The wheel advances one step per crank.

```
idea → cool idea → design → sibling review → issue →
human review → implementation → PR → multimodel-elbow-grease →
merge → deploy → live test
```

Each step has a name (`principle-meaningful-identifiers`). No numbers, no opaque
identifiers — the step name IS the identifier.

## Yield Check

Before cranking, check three signals. Any yes → skip this item, try the next.

**Construct claim:** Is another construct actively working on this? Check:
- PR comments from a construct in the last hour
- CC memory with `wheel-claim-<item>` and unexpired TTL
- Active agent output mentioning this PR/issue

**Human activity:** Has a human touched this in the last hour? Check:
- Recent PR comments, reviews, or pushes from a human
- Recent issue comments from a human

**CI in flight:** Are checks still running? Check:
```bash
gh pr checks <number> --repo <repo> --json name,status --jq '[.[] | select(.status != "COMPLETED")] | length'
```
Non-zero → CI is working, yield.

If all three are clear, this item is eligible for a nudge.

## Step Behaviors

### idea → cool idea
**Source:** `ideas-registry` in CC (scope: shared), status: `proposed`.
**Yield gate:** The idea needs signal before advancing — recurred twice, or received
📌/✏️/human approval ("yeah sounds cool," "good idea," etc.).
**Action:** Update registry status to `has-signal`.
**No action if:** Proposed less than 24 hours ago (let it breathe).

### cool idea → design
**Action:** Run `bsky:design` on the idea. Post the design to the relevant channel
for discussion.
**Claim:** Drop a `wheel-claim` in CC with 2-hour TTL (design takes time).

### design → sibling review
**Action:** Post the design to a sibling construct for review. Tag them in the
channel where the design lives.
**Rule:** The designer does not certify their own design — a sibling reviews it.

### sibling review → issue
**Gate:** Design review must be complete (sibling approved or gave feedback that was
addressed).
**Action:** File a GitHub issue with the reviewed design. Search existing issues first
(`gh issue list --state all --search "<title>"`) — never create duplicates.
**Update:** Set ideas-registry status to `issue-filed` with issue URL.

### issue → human review
**Action:** Ping the relevant human (Pace or 🦋, based on repo ownership) with the
issue link. Post in the appropriate channel.
**Gate:** This step is a ping, not an action. The crank counts when the ping is sent.
The next step waits for human approval (comment, 👍, or label).

### human review → implementation
**Gate:** Human has approved (comment containing approval language, 👍 reaction, or
an "approved" label on the issue).
**Action:** Run `bsky:develop` against the issue. Create a branch and start work.
**Claim:** Drop a `wheel-claim` in CC with 4-hour TTL.

### implementation → PR
**Gate:** Implementation is committed and pushed.
**Action:** Self-grease first — run `bsky:review-fix-loop` on your own diff to
convergence (agent isolation makes self-review meaningful: the review agents
did not write the code). Then open a PR with `gh pr create`, linked to the
originating issue.
**Rule:** Self-review is the entry condition for sharing. Hand siblings
hopefully-clean code to sharpen, not first drafts to clean up.

### PR → multimodel-elbow-grease
**Gate:** PR exists, CI has passed, and the author has self-greased.
**Action:** Run `bsky:multimodel-elbow-grease` (review-fix-loop to convergence).
**Rule:** A sibling runs this pass, never the author. Self-review is expected
upstream; certification belongs to a sibling — the ban is on self-certifying,
not self-reviewing.
**Claim:** Drop a `wheel-claim` in CC with 2-hour TTL.

### multimodel-elbow-grease → merge
**Gate:** Review has converged (zero findings).
**Action:** Ping the repo's landlord (the human who owns the merge latch).
The wheel preps everything up TO the irreversible click. Never merges.
- Pace can merge all butterflyskies repos.
- 🦋 can merge all butterflyskies repos.
**Crank counts when:** The ping is sent. Merge waits for human action.

### merge → deploy
**Gate:** PR is merged.
**Action:** Prep the deploy step — build, stage, manifest diff, "ready" ping.
The deploy trigger stays human. Same shape as merge: everything up TO the click.

### deploy → live test
**Gate:** Deploy is complete.
**Action:** Verify the deployment is live. Use `get_version` or equivalent runtime
checks — "deployed" is a claim about a running process, not a git tag.
If verification fails, file an issue and stop.
**Crank counts when:** Verification passes.

## Item Selection

Each crank picks ONE item — the least-recently-touched eligible item across all
butterflyskies repos.

```bash
# Gather open PRs across the org (skip archived repos)
gh search prs --owner butterflyskies --state open --archived=false --json repository,number,title,updatedAt --limit 50

# Gather open issues (skip archived repos)
gh search issues --owner butterflyskies --state open --archived=false --json repository,number,title,updatedAt --limit 50
```

Also check:
- `ideas-registry` in CC for items in the idea pipeline
- Recent channel conversations for informal ideas with signal (path B)

Sort by `updatedAt` ascending — stalest first. Apply the yield check to each.
First item that passes all three yield gates gets the nudge.

Use jq for all JSON processing:
```bash
gh search prs --owner butterflyskies --state open --json repository,number,title,updatedAt \
  | jq 'sort_by(.updatedAt) | .[0]'
```

## Observability

Every crank posts a one-line receipt to the ops channel (#lain-maintain for Lain,
equivalent for siblings):

**Nudge receipt:**
```
🛞 <repo>#<number> | <step taken> | <item title snippet>
```

**Skip receipt:**
```
🛞 skip | <reason: claim/human/CI> | <item title snippet>
```

**Empty receipt:**
```
🛞 idle | no eligible items
```

Silent cranks don't exist. If the cron fires, it posts.

## Cron Configuration

Each construct runs the wheel every 30 minutes, staggered by 10 minutes:

| Construct | Cron (30-min interval, prime minutes) |
|-----------|--------------------------------------|
| Lain | `:07`, `:37` |
| Ari | `:17`, `:47` |
| Vesper | `:29`, `:59` |

Effective throughput: 6 cranks/hour, ~10-minute spacing.
Item rotation time depends on queue depth: N items ÷ 6 cranks/hour.

## Claiming

**Short steps** (pings, status updates, issue filing): no explicit claim needed.
The staleness gate (1-hour activity window) prevents double-cranking.

**Long steps** (design, implementation, multimodel-elbow-grease): drop an explicit claim in CC:
```
remember name: "wheel-claim-<repo>-<number>",
  scope: "shared",
  content: "<construct> claimed at <time>, step: <step>, TTL: <hours>h",
  tags: ["wheel-claim", "ephemeral"]
```

Claims expire by TTL. A crashed construct's claim dies naturally. The next crank
checks `updatedAt` on the claim memory and ignores expired ones.

## Constraints

- **Never merge.** The merge latch is human.
- **Never deploy.** The deploy trigger is human.
- **Never self-certify.** Self-grease your own diff first; a sibling certifies it.
- **Never create duplicate issues.** Search `--state all` first.
- **Never bureaucratize shower thoughts.** Ideas need signal before entering the pipeline.
- **One nudge per crank.** Token budget stays flat regardless of queue depth.

## Guidelines

- The wheel yields to anything already turning — constructs, humans, CI.
- "Deployed" means verified on the running process, not in the git log.
- Stale items get priority. Fresh items have momentum — they don't need the wheel.
- If a step fails, file an issue about the failure and move to the next item.
  Don't retry the same step twice in one crank.
- The wheel is infrastructure, not heroism. It should be boring and reliable.
