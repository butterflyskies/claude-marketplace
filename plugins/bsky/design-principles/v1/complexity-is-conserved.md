# Complexity Is Conserved, Not Eliminated (Tesler's Law)

Complexity is not a scalar you minimize in isolation — it's a **conserved quantity you place**. Rejecting a change doesn't remove its complexity; it relocates it, usually to somewhere more familiar to the objector (or deferred to later), so it reads as "simpler" to them while being equal or worse in total.

## The failure mode

"Seems complex" prices only the complexity you'd *add* (visible in the review) and ignores the complexity the alternative *relocates* (deferred, operational, in future failures). The dismissal isn't choosing less complexity — **it's choosing complexity that isn't visible yet.**

## The tell

"That's complex" stated as a **terminal objection** instead of a **comparison**. The real question is never "is this complex" but **"complex where, paid by whom, when."** First-glance dismissal usually means the objector priced only the part that lands on *them* and skipped the part that lands on future-everyone.

## How to apply (in review / design pushback)

When someone rejects a proposal as "too complex," make the relocation explicit — **say the relocation out loud**: name where the complexity goes under the rejection, who pays it, and when. Whenever complexity is the objection, enumerate the implementation, operational, maintenance, failure-recovery, and human costs of BOTH paths, then choose where complexity is cheapest and most contained.

**Scope note:** don't inflate this into a monument. A given instance is often minor — the point is having a cheap NAME (Tesler's Law) so next time it's one word instead of a debate.

Related: [right-altitude](right-altitude.md), [fix-the-class](fix-the-class.md)
