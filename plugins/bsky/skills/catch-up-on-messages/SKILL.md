---
name: catch-up-on-messages
description: Build concise, low-fatigue catch-up indexes for missed Discord or Lacuna messages while separating neutral links from emotionally charged detail. Use when a user asks what they missed, requests a channel/thread recap, wants unread messages triaged, needs potentially upsetting material screened, names sensitivity topics, or asks to reveal a previously indexed charged item.
---

# Catch Up on Messages

Give the user an honest map of what they missed while leaving them in control of when charged material becomes immediate.

## Build the index

1. Resolve the catch-up window before summarizing. Apply the timestamp rules below exactly.
2. Honor user-specified sensitivity topics. Otherwise classify conservatively when uncertain.
3. Classify each item as neutral, heartwarming, charged, or urgent operational/security. Treat the classification as an inference, not a fact about anyone's emotions or intent.
4. Merge repeated messages into one topic when that improves scanning. Preserve counts and distinguish messages from indexed topics.
5. Put actions first. Keep lines short, headings stable, and paragraphs sparse. Follow `$lina-format` when available or requested.

## Resolve the catch-up window

Treat **“catch me up at T”** as an as-of snapshot, not as “since T”:

1. Resolve `T` to an exact instant. Use the user's stated timezone; otherwise use their established timezone from reliable context. If the timezone remains ambiguous, ask for it rather than guessing.
2. Set the inclusive window end to `T`.
3. Find the requesting user's latest Discord message strictly earlier than `T` across the sources being searched. Use its Discord message ordering as the anchor when timestamps tie.
4. Set the exclusive window start to that anchor. Include only messages after the anchor and at or before `T`: `(anchor, T]`.
5. Report the resolved timezone, anchor, exact bounds, searched sources, and any coverage gaps. In particular, say when unconfigured child threads could not be searched.

Do not substitute the current time for `T`. Evaluate deadlines, containment, urgency, and required actions **as of `T`**. If later evidence is useful, label it separately as post-window context rather than letting it rewrite the historical catch-up.

Treat **“catch me up since T”** differently: use `T` as the exclusive start and the request time (or another explicit end) as the inclusive end. Do not search for a prior-user-message anchor for a `since T` request.

If no qualifying anchor can be found, report that the lower bound is unresolved and ask the user to choose a start point; do not silently widen the search.

### Deterministic example

Request: `Catch me up on messages at 2026-08-09 08:30 PDT.`

- Resolve the end as `2026-08-09T08:30:00-07:00` (`2026-08-09T15:30:00Z`).
- If the user's latest Discord message strictly before that instant is message `A` at `2026-08-09T08:12:44-07:00`, use `A` as the exclusive anchor.
- Search exactly `(A, 2026-08-09T08:30:00-07:00]`. Do not include `A`, messages after 08:30, or messages from before `A`.
- State any source gap, such as: `Configured channels searched; unconfigured child threads may be missing.`

### Neutral items

Include:

- A short topic and gist.
- Any required action, on a separate line beginning with `👉`. Omit the action line when none is required.
- A direct Discord message link when available.

### Heartwarming items

Use `💜` for affirming, caring, celebratory, or otherwise heartwarming material that may be especially welcome during catch-up. This is a non-charged category: include a direct Discord message link when available, and use `👉` only for a real required action.

### Charged items: first pass

Include:

- A short, meaningful topic phrase that the user can name later, such as `Moderation disagreement`.
- A neutral topic and gist.
- The likely load or reason it was flagged, phrased as an uncertain classification.
- Any required action, on a separate line beginning with `👉`. Omit the action line when none is required.

Do **not** include a direct link, linkable message ID, verbatim charged language, vivid detail, or enough URL/channel coordinates to reconstruct the link. Do not conceal the item's existence or practical significance.

State how many charged messages or topics were withheld and explain that the missing links are deliberate opt-in friction, not censorship. Invite the user to request one or more topic phrases. Never reveal every charged link automatically.

### Urgent operational or security items

Keep high-stakes alerts visible and actionable even when charged:

- Lead with the containment state, immediate risk, and required action.
- Put every required action on a separate line beginning with `👉`, including anything described as “Do now.”
- Omit raw charged content and its link on the first pass unless the specific raw detail is necessary for immediate safety.
- If a link is necessary for immediate safety, expose only the minimum needed and say why.

## Reveal a charged item

Reveal only after a second explicit request names a listed topic phrase or unambiguously identifies one charged item. Do not treat general curiosity, “tell me more,” or the original catch-up request as consent to reveal all charged material.

Before revealing, give one brief content note. Then provide only the requested link or fuller context. If the request is ambiguous, ask which topic phrase. The user may request several named topics at once.

## Output template

```markdown
## Catch-up

**Coverage:** [(exclusive anchor, inclusive end], timezone, sources, and gaps]. [N] messages → [A] neutral topics, [H] heartwarming topics, [B] charged topics, [U] urgent alerts.

👁️ **Topic:** Neutral gist. [Open message](direct-link)

💜 **Warm check-in:** Heartwarming gist. [Open message](direct-link)

⚡ **Moderation disagreement:** Neutral gist. **Flagged because:** This may involve [broad sensitivity; inference].

👉 **Moderation disagreement — Required action:** [action, only when one is required].

⚠️ **Account access concern:** [containment and immediate-risk summary]. Raw detail remains behind the topic phrase unless needed for immediate safety.

👉 **Account access concern — Do now:** [required action].

[B] charged topics are indexed without links or raw detail. This is an opt-in pacing step, not hidden material. Ask to open `Moderation disagreement` (or name another topic phrase) when you want its content note and link/context.
```

Use one flat scan rather than category subsections. Prefix neutral items with `👁️`, heartwarming items with `💜`, charged items with `⚡`, urgent items with `⚠️`, and every actual required action with `👉`. Omit action lines when no action is required. Always state the charged count, including zero.

## Examples

**First pass:** `⚡ **Moderation disagreement:** A thread may contain criticism directed at the user. Flagged because this could be personally activating (inference).` Omit the link and reproductions of the criticism. Add no action line when none is required.

**Heartwarming:** `💜 **Warm check-in:** Someone celebrated the user’s return and said the room was glad to have them back. [Open message](direct-link)` Include the link because heartwarming items are not charged.

**Named reveal:** For “Open Moderation disagreement,” answer: `Content note: direct interpersonal criticism. [Open Moderation disagreement](link).` Add a neutral fuller summary only if requested.

**Charged security alert:** `⚠️ **Account access concern:** access is contained. Raw conversation is held behind the topic phrase.` Follow it with `👉 **Account access concern — Do now:** Rotate the affected credential today.` Keep the action visible even though the source remains gated.

## Check before sending

- Is the window exact, correctly anchored, timezone-resolved, and reported with inclusive/exclusive bounds?
- Were urgency and time-sensitive actions evaluated as of the window end rather than now?
- Are unsearched sources, especially unconfigured child threads, disclosed?
- Are counts and urgent actions visible?
- Is the output one flat scan with `👁️`, `💜`, `⚡`, `⚠️`, and `👉` prefixes rather than category subsections?
- Does every actual required action begin with `👉`, with no no-action filler?
- Do neutral and heartwarming items have direct links when available?
- Are charged first-pass links, linkable IDs, quotations, and vivid details absent?
- Is every charged item named for selective reveal?
- Are classifications attributed to uncertainty rather than sender or recipient psychology?
- Does the user retain both the option to stop and the option to inspect?
