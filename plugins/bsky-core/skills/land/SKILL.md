---
name: land
description: Reconcile a work session into verified repository state, current review and tracker context, durable learnings, and a bounded handoff. Use when the user asks to wrap up or land a session; inventory first and perform commits, pushes, remote updates, or publication only within explicit current authority.
---

# Land

Close a work session without losing intent or smuggling unrelated effects into “wrap up.” Start with a read-only inventory, identify each proposed mutation and its authority, then execute only authorized classes. Landing is not merge or deployment authority.

## Preflight and effect ledger

1. Read workspace and repository instructions, current project state, and any canonical infrastructure or handoff records available to this seat.
2. Enumerate every repository touched in the session. Inspect status, staged and unstaged diffs, branch/upstream identity, open review state, and existing session artifacts. Preserve unrelated user changes and other owners' work.
3. Build a short effect ledger covering memory writes, file edits, commits, pushes, pull-request changes, tracker changes, notification triage, milestone changes, and flight-log publication. Record the exact target and whether current user or standing project instructions authorize it.
4. Perform read-only reconciliation for every lane. For any mutable lane without authority, return the proposed action and stop that lane. Do not treat skill invocation, an authenticated tool, a remembered preference, or ownership of a local clone as blanket authority.

## Idempotency

Landing may run more than once. Before each effect, compare current canonical state and skip work already represented:

- do not commit a clean or out-of-scope tree;
- do not push an already-published exact commit;
- do not rewrite a current pull-request body or duplicate a tracker comment;
- append only new flight-log material;
- edit an owned current handoff in place rather than creating competing “current” records.

Use idempotency keys or exact before-state receipts when an external system supports them. After a partial failure, re-read state before retrying.

## Capture durable learnings

Identify project knowledge, architecture decisions, corrected stale facts, and durable workflow calibration from the session. Write only to the memory scopes the current seat owns and only when memory mutation is authorized. Shared decisions belong in the configured shared store; personal calibration does not.

Sync and exact-read important updates when supported. Do not turn transient branch state or a task list into durable personal memory.

## Repository housekeeping

For each in-scope repository:

1. Review status and the full relevant diff, including staged content.
2. Run repository-native formatting, linting, tests, and policy gates proportionate to the change. Do not claim green for gates that were unavailable or skipped.
3. Fix failures only when the user authorized code changes; otherwise report them.
4. Commit only the reviewed in-scope bytes with a repository-conformant message when commit authority exists.
5. Treat push as a separate external effect. Push only the exact reviewed commit to the exact authorized remote/ref; never force-push unless explicitly authorized.

Do not stage secrets, generated residue, unrelated dirty-tree changes, or another owner's work.

## Review and tracker reconciliation

For related open pull requests, compare branch commits and current checks/reviews against the description. Update the body only when authorized and only with verified claims.

For the canonical tracker, report progress and missing tracking. Comments, new issues, assignments, status moves, and milestone rollover are separate mutations. Before an authorized rollover, re-read current milestones, preserve the configured calendar convention, move only open items in scope, and close or delete the old milestone only under its established policy.

Never merge, approve on another reviewer's behalf, deploy, or convert a local result into a production receipt.

## Notification reconciliation

When the configured notification service is available, refresh and inspect items related to this session. Mark acted or dismiss only exact related items and only when notification-triage authority exists. Leave ambiguous and unrelated items untouched.

## Flight log

When the project has an established flight log and publication is authorized, add only today's new verified wins. Link exact reviews, issues, and commits where useful. Preserve existing entries and write against the session's stated outcome rather than producing a raw changelog.

Committing and publishing the flight log remain subject to their own repository and remote gates.

## Handoff

Write a handoff only when complex in-flight context would otherwise be costly to reconstruct. Follow the workspace's ownership and concurrency contract for its current handoff record. If no contract exists, prefer a project-scoped record and never create a global singleton that could race concurrent sessions.

Capture current intent, exact state and receipts, owners, blockers, superseded claims, and the next concrete boundary. Exclude secrets and unverified volatile claims. Edit the owned current record in place, exact-read it, and sync when supported. Delete or retire it when canonical trackers and reviews fully capture the state.

## Final receipt

Return:

- verified checks and exact committed/pushed identities;
- updated memories, reviews, tracker items, notifications, log, and handoff;
- skipped or blocked effects with their authority/tool reason;
- dirty or unresolved state that remains;
- the next physical action.

Never describe an unpushed commit as published or an undeployed merge as live.
