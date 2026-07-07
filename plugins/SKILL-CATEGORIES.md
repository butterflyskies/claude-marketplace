# Skill Categories — Canonical Ontology

Every skill declares exactly one `category:` in its SKILL.md frontmatter.
This file is the one canonical declaration of what the categories are and
which of them are principle-bound. The CI check
(`.github/scripts/skill-consistency.sh`) parses this file — it carries no
copy of the list.

A skill whose category is principle-bound must invoke
`bsky:load-design-principles` before starting work:
`(relationAll loadsDesignPrinciples PrincipleBoundSkill)`.

| Category | Principle-bound | Meaning |
|----------|-----------------|---------|
| design | yes | Produces design artifacts: specs, architecture, atom boundaries |
| development | yes | Produces or modifies code — including skills, which are high-level code |
| code-review | yes | Evaluates code and produces findings |
| pipeline | yes | Advances work items through steps that produce or evaluate code |
| operations | no | Session mechanics, configuration, telemetry, memory upkeep |

## Rules

- **One category per skill.** A skill that seems to need two is either a
  pipeline skill or wants splitting.
- **New categories are added here first**, in the same PR that first uses
  them. A category that exists only in a skill's frontmatter fails CI.
- **Principle-bound is a property of the category, never of the skill.**
  Don't hand-mark skills; classify them and the property follows.
- **Classification is judgment; sibling review checks it.** The lint can
  verify a category exists — it cannot verify the category is right.
