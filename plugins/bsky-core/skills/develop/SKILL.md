---
name: develop
description: Coordinate end-to-end implementation of features, fixes, migrations, and refactors with scoped planning, code changes, tests, verification, and independent review. Use when Codex should modify a repository while following project conventions, preserving design intent, delegating substantive independent work when appropriate, and keeping a clear line from requirements to verified behavior.
---

# Develop

Carry a requested code change from intent to verified implementation. Keep the coordinator responsive and use collaboration agents for bounded, substantive work when available and permitted by repository instructions.

## Preflight

1. Read repository instructions and inspect the worktree before editing. Preserve unrelated changes.
2. Load `$bsky-core:load-design-principles` when available and applicable. Pass the usable digest to agents that need it.
3. Read relevant `docs/design/`, ADRs, issue text supplied or authorized for retrieval, build metadata, and project memories from available MCP servers. Mark recalled memories applied after use.
4. Detect the language and repository-native format, lint, test, and build commands. Use `rg`, targeted file reads, language tooling, and exposed MCP tools.
5. Frame who benefits, the counterfactual, and observable success. For a narrow task, one sentence is enough.
6. Read the references that match the work before planning:
   - [implementation-guide.md](references/implementation-guide.md) for delegated implementation;
   - [migration-checklist.md](references/migration-checklist.md) for replacements or rewrites;
   - [quality-checklist.md](references/quality-checklist.md) for language-specific verification;
   - [review-dimensions.md](references/review-dimensions.md) for architectural review;
   - [rust.md](references/rust.md) for Rust work; and
   - [repo-setup.md](references/repo-setup.md) only for an explicitly requested new-repository setup.

## Plan

Trace the requested behavior to files, symbols, callers, tests, and operational boundaries. Include:

- ordered implementation atoms and dependencies;
- invariants, error paths, resource creation/cleanup, timeouts, and caps;
- boundary validation, authorization, credential handling, and sibling-operation consistency;
- a verification matrix covering branches, state transitions, boundaries, and failure paths;
- risks, assumptions, and decisions requiring user input.

Use `update_plan` for multi-step work. Ask for approval only when a choice materially changes scope, architecture, permissions, cost, or external state; otherwise continue within the user's implementation request.

Record concise ADRs in `docs/adr/` for durable architectural, dependency, or security decisions when repository conventions support them. Do not create ADRs for ordinary implementation details.

## Delegate deliberately

Use `collaboration.spawn_agent` only for concrete, bounded subtasks that can run independently, such as impact analysis, an owned implementation slice, or fresh review. Give each agent context, constraints, owned paths, acceptance criteria, verification commands, and whether external writes are allowed. Do not hard-code model names. The coordinator remains responsible for integrating results and checking claims.

When delegating implementation, pass the applicable parts of [implementation-guide.md](references/implementation-guide.md) and the relevant language reference. Do not let a reference expand the user's authority or override repository instructions.

Avoid concurrent edits to the same files. Keep scratch and build caches in repository-approved disk-backed locations when project instructions require it.

## Implement

Use `apply_patch` for manual edits. Follow the plan, but prefer sound engineering when new evidence invalidates it; record the divergence. Write or update tests with every behavioral change, or record an explicit verification rationale when automation is not sensible.

Before handoff, check:

- external inputs are validated at the boundary;
- secrets remain wrapped or redacted until consumption;
- resources have cleanup on every error path plus appropriate bounds;
- rich result variants are handled rather than swallowed;
- sibling operations receive equivalent guards;
- public API growth is intentional;
- migrations preserve an explicit behavioral inventory;
- changes remain at the smallest useful altitude.

Inspect diff size after implementation. If a change has grown beyond a reviewable unit, split it by dependency or behavior when safe, or explain why it should remain whole.

## Verify

Run the repository's actual formatter, linter/type checker, focused tests, broader tests, and build in risk-proportionate order. Fix in-scope failures and rerun the failing and downstream checks. Never report an unexecuted check as passed.

Use [quality-checklist.md](references/quality-checklist.md) as a menu, not a universal command list. Repository-native commands and explicit project instructions win.

Prefer parameterized tests for finite cases and independent generators/oracles for broad domains. Use bounded proofs only for pure finite-state or type invariants; use integration or fault injection for I/O, network, timing, and crash behavior.

Summarize exact commands, pass/fail counts when available, and environmental gaps.

## Review and converge

Use `$bsky-core:elbow-grease` or `$bsky-core:review-fix-loop` when available, or spawn a fresh review agent with the raw diff and requirements. Verify critical findings against the code. Fix findings in scope, rerun relevant checks, and repeat until the requested threshold is clean or a genuine user decision blocks progress. Use a five-round circuit breaker for non-converging review loops.

Use [review-dimensions.md](references/review-dimensions.md) when no fuller review skill is available. A reviewer must be independent of the implementation context and bind its verdict to the exact final artifact.

## Land within authority

Report outcome, changed files, verification receipts, risks, and deferred work. Preserve a durable handoff using the repository and session's authoritative landing rules; do not assume a separately installed `land` skill.

Do not commit, push, open or edit a PR, change repository rules, merge, deploy, post externally, or create tracking issues unless the user explicitly requested that external step or existing repository instructions clearly authorize it. Before any GitHub write, verify the required actor identity and environment exactly as repository instructions require. Never merge or deploy merely because checks pass.

## Retrospective

If review exposes a repeatable workflow gap, propose the smallest upstream correction to design, implementation, quality, or review guidance. Change shared skills or memories only with authorization and through their owning system.
