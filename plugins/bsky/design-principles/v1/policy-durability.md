# Policy Durability — The Two-Tier Principle

Make a decision survive by construction, not by recall.

Don't ask a construct to *notice* a decision got made and *remember* to save it — recognition dies at compaction just like everything else, so "remember to persist" fails the exact test it's meant to pass. Two tiers by whether the policy can be mechanized:

**Tier 1 — mechanize (strongest).** Encode the policy as config/gate the system reads *at action time* (allowlist = `allow_from`; approval = a gate in the add-path). It can't die at compaction because it's not in the conversation — it's in the system.

**Tier 2 — durable capture for the un-mechanizable prose remainder.** Policies that don't map to a config write have no click to hang a record on. They need: a canonical home, a lifecycle tag (`active | superseded | retired` + successor link + retirement authority), and a structural capture on-ramp.

## Durability is a two-ended axis

Two opposite failure modes on one axis:
- **under-durable** — rule dies at compaction.
- **over-durable** — dead rule still enforced.

Opposite guards (persist vs. retire); they only unify one level up at **"durable record + liveness tag."** Persistence stops forgetting; lifecycle stops fossils from voting. Solving only persistence trades death-by-forgetting for death-by-calcification.

## Taxonomy caveat

Not every decision is policy — "skip this cron" must NOT persist. The missing piece is the on-ramp (auto-promotion from chat-utterance to committed store).

Related: [loading-and-following-are-different-organs](loading-and-following-are-different-organs.md)
