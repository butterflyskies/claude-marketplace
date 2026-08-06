---
name: skill-forge
description: Create, revise, audit, validate, and optionally prepare publication of Codex skills. Use when asked to build a new skill, adapt an existing workflow into a Codex skill, improve a skill package, find repeated work that merits a skill, or stage an approved skill change for a marketplace repository.
---

# Skill Forge

Use the system `skill-creator` skill as the authoring authority. This skill adds a marketplace-oriented workflow around it; it does not replace its format, initialization, metadata, validation, or forward-testing rules.

## Establish the request

Classify the work as one of:

- **Create:** build a new skill from a concrete need.
- **Revise:** change an existing skill while preserving unaffected behavior.
- **Adapt:** translate a skill from another harness without carrying unavailable tools or semantics across the boundary.
- **Audit:** examine repeated work and propose skill candidates with evidence.
- **Validate:** inspect an existing package read-only, run structural and representative behavioral checks, and return receipts; make fixes only when separately requested.
- **Publish:** prepare an already reviewed candidate for an explicitly named repository.

Confirm the destination. Use the user's requested staging directory. If none was supplied, ask; if the user has no preference, choose a non-discovered staging directory outside live skill roots. Writing under `$CODEX_HOME/skills`, a plugin cache, or another auto-discovered skills root is installation and requires explicit activation/install authorization. Do not assume a particular marketplace checkout.

## Gather evidence

For create, revise, adapt, validate, or publish work:

1. Inventory the current package, then read the complete `SKILL.md` and every directly required resource.
2. Inspect nearby skill descriptions for responsibility overlap.
3. Identify concrete triggering prompts, required tools, inputs, outputs, and failure boundaries.
4. Separate portable intent from harness-specific mechanics. Replace a mechanism only when a real Codex capability provides equivalent evidence; otherwise narrow or omit it explicitly.

For an audit:

1. Use only session handoffs, feedback, issue history, or other records the user placed in scope.
2. Rank repeated workflows by frequency, consequence, and how much deterministic guidance would help.
3. Report candidate name, trigger description, evidence, overlap, required resources, and estimated effort.
4. Draft candidates only when the user asked for drafts or application.

## Build and validate

1. Read and follow `skill-creator` completely, including `references/openai_yaml.md`.
2. Initialize new skills with `init_skill.py`.
3. Keep frontmatter to `name` and `description`.
4. Put deterministic repeated operations in tested scripts and detailed conditional material in directly linked references.
5. Generate `agents/openai.yaml` with a prompt that explicitly invokes `$skill-name`.
6. Run `quick_validate.py` on every completed skill.
7. Exercise every bundled script with representative success and failure inputs.
8. Forward-test behavior on fresh agents when the workflow is complex and doing so stays within the user's authority and risk budget.

## Review the candidate

Present the resulting path, behavioral scope, validation receipts, unresolved gaps, and any deliberate omissions. For revisions, summarize the meaningful delta rather than dumping unchanged text. Treat review as a gate: a structurally valid skill is not automatically approved for activation or publication.

## Prepare publication only when authorized

Publication is a separate state-changing action. After explicit approval:

1. Read repository instructions and verify the exact git/GitHub actor required by the workspace.
2. Reconcile the candidate against the current target branch before writing.
3. Re-read the reconciled package and rerun structural validation plus representative bundled-script checks.
4. Verify the effective authenticated actor for every exact write path and stop on mismatch.
5. Commit only the reviewed skill package and its required marketplace metadata.
6. Push and open a draft pull request using the workspace's approved publishing workflow.
7. Report the commit and PR receipts. Do not merge unless separately authorized.

If publication is not authorized, leave the candidate staged and provide a handoff. Never turn “create a skill” into an implicit commit, push, PR, installation, or shared-state mutation.
