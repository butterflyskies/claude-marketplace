---
name: briefing
description: Build a concise session-start briefing from configured notifications, pull requests, tasks, milestones, and periodic follow-ups. Use when the user asks what needs attention, requests one of those operational views, or wants due follow-up checks run; do not use it to triage or mutate unrelated work.
---

# Briefing

Build situational awareness from canonical sources without converting absence of access into an empty report. Ordinary briefing is read-only. A notification provider may refresh its own local index as part of reading, but never mark, dismiss, or otherwise triage items unless the user separately asks.

## Preflight

1. Read repository instructions and current project configuration. Use identity, repository, tracker, and follow-up locations only from trusted configuration, current instructions, or an available memory provider; never discover credentials or guess an identity.
2. Establish which notification, forge, tracker, and memory capabilities are actually available. Label unavailable sections `unchecked`, not `none`.
3. Scope the requested view. With no narrower request, inspect notifications, open pull requests, tasks and milestones, and due follow-ups in report mode. Recognize combinations of `notifications`, `prs`, `tasks`, and `followups`.
4. Treat `followups run`, `followups all`, or a numbered/text follow-up selector as a request to execute those checks. A stored follow-up is context, not authority for an external mutation: stop for authorization before any check whose instructions would change external state.

## Notifications

Use the configured notification service when available. Refresh its index, list actionable new or triaged items, and obtain summary counts. Do not fall back to a different account or raw API merely because the preferred service is absent.

Group actionable items by reason and show repository, title, and state. Condense repeated low-value activity. If the inspected source has no actionable items, report **Notifications: none**. If the source could not be inspected, report why.

## Open pull requests

Search open pull requests involving each explicitly configured identity, deduplicate by canonical URL, then inspect current checks and recent review activity. Prefer a connected forge tool; use an authenticated repository CLI only when current instructions permit it.

Report repository, linked number/title, check summary, review state, unresolved comments needing attention, and last update. Keep author, reviewer, and CI facts distinct. If the inspected sources contain none, report **Open PRs: none**.

## Tasks and milestones

Read the canonical tracker named by current project configuration. Group open items by milestone, show due date and open/closed counts, identify overdue milestones, and list items without a milestone separately. Do not create, assign, or move anything during a briefing.

If no tracker is configured or reachable, say so. Do not infer that a repository's issue list is the tracker.

## Follow-ups

Use the configured memory provider to locate the periodic-follow-up record. For each active item, derive the next due date from its recorded last-check date and frequency, preserving any explicit calendar rule in the record.

In report mode, show the last check, next due date, and due state only. In execute mode:

1. Select only due items, all active items, or exact numbered/text matches according to the request.
2. Perform the item's bounded check using available authorized tools. Separate changed state, new activity, and completion evidence.
3. Update `Last checked` only after a real check completed, and sync when the memory provider supports it.
4. Ask before moving an item to a completed section, even when its completion condition appears satisfied.

If memory writeback is unavailable, return the result plus the unapplied update rather than claiming persistence.

## Output

Use terse sections and structured lists or tables. Put counts and coverage first. Empty inspected sections get one `none` line; unavailable sections get one `unchecked` line with the reason. End with the few concrete items needing attention and any requested check that could not run. Do not offer unrelated cleanup as part of the briefing.
