---
name: skill-forge
description: "Create, edit, and publish skills to the marketplace repo. Takes a description of what to build or change, writes the SKILL.md, and handles the git workflow (branch, commit, push, PR). Use when creating new skills or modifying existing ones."
---

# /skill-forge — Skill Creation and Publishing

Build or edit skills and route them into the marketplace repo as PRs.

If a `required-environment-variables` memory exists (scope: global), read and apply it
before any git/gh operations.

## Arguments

`$ARGUMENTS` describes what to do. Forms:

| Input | Action |
|-------|--------|
| `new <name>: <description>` | Create a new skill from scratch |
| `edit <name>: <description of changes>` | Edit an existing skill |
| `audit` | Analyze recent sessions for skill gaps and suggest candidates |
| `audit --apply` | Audit and immediately draft the top candidates |

When no arguments are given, run an interactive audit: ask what's been painful or
repetitive lately, suggest candidates, and let the user pick.

## Workspace

All work happens in the marketplace repo:

```
~/dev/github.com/butterflyskies/claude-marketplace/plugins/bsky/skills/
```

Each skill lives in its own directory with a `SKILL.md` file. Some skills also have a
`references/` subdirectory for supplementary material.

## Phase 1: Context gathering

### For `new`:
1. Read the user's description and any linked design docs, threads, or memories
2. Recall relevant memories — existing skills, feedback, workflow patterns
3. Identify which existing skills overlap and how the new one differs
4. Ask clarifying questions if the scope is ambiguous (max 2 rounds, then draft)

### For `edit`:
1. Read the current SKILL.md for the named skill
2. Read the user's description of desired changes
3. Recall relevant feedback memories that might inform the edit
4. Check if the edit conflicts with other skills' responsibilities

### For `audit`:
1. Recall recent session handoffs and feedback memories (limit: 20, scope: all)
2. Read all current skill descriptions to understand coverage
3. Identify patterns: repeated manual work, ad-hoc workflows, things done 3+ times
4. Cross-reference against open threads in ariadne-inner-state if in discord context
5. Produce a ranked list of candidates with: name, description, evidence, effort estimate

## Phase 2: Drafting

Write the SKILL.md following the established format:

### Frontmatter
```yaml
---
name: <kebab-case-name>
description: "<one-line trigger description — used for skill matching>"
---
```

### Body structure
Follow the patterns from existing skills:
- H1 title with `/<name>` prefix and short subtitle
- Opening paragraph: what the skill does and when to use it
- `## Arguments` — how `$ARGUMENTS` is parsed
- Numbered phases with clear, actionable instructions
- Concrete tool calls and commands (not vague "check the status")
- Output format section if the skill produces structured output
- Idempotency notes if the skill might run multiple times

### Quality checks
Before finalizing a draft, verify:
- [ ] Description is specific enough for accurate trigger matching
- [ ] No overlap with existing skill responsibilities (or overlap is documented)
- [ ] Phases are ordered by dependency (earlier phases produce what later ones need)
- [ ] Tool calls reference real tools (memory-mcp, gh-notify, gh, etc.)
- [ ] The skill can actually be executed — no steps that require tools that don't exist
- [ ] Instructions are positive ("do X") not negative ("don't do Y") where possible

### For edits:
Show the diff conceptually — what's changing and why. Don't rewrite sections that
aren't affected by the edit. Preserve the existing structure unless restructuring is
part of the change.

## Phase 3: Review

Present the draft to the user in the conversation:
- For new skills: show the full SKILL.md
- For edits: show the changed sections with context
- For audits: show the ranked candidate list with one-paragraph pitches

Wait for user approval or revision requests. Iterate until approved (max 3 rounds,
then ask if they want to ship as-is or pause).

## Phase 4: Git workflow

Once approved:

1. Pull latest main in the marketplace repo
2. Create a branch: `skill/<name>` for new, `skill/<name>-update` for edits
3. Write the SKILL.md (and any references/ files)
4. Commit with message: `feat(skills): add <name>` or `feat(skills): update <name>`
5. Push the branch
6. Open a PR with:
   - Title: `skill: add <name>` or `skill: update <name>`
   - Body: summary of what the skill does, why it exists, and what triggered its creation

Do NOT merge — Lina handles merging.

## Phase 5: Post-publish

After the PR is up:
1. Report the PR URL
2. If the skill was born from an audit finding, note which gap it fills
3. If the skill has dependencies on other skills or tools, list them
