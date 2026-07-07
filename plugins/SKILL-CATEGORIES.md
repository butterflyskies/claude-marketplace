# Skill Categories — Canonical Ontology

Every skill declares exactly one `category:` in its SKILL.md frontmatter, and
it must be a **leaf** of this tree. This file is the one canonical declaration
of the ontology. The CI check (`.github/scripts/skill-consistency.sh`) parses
this file — it carries no copy.

```
skill
├── principle-bound        ← declares: invokes bsky:load-design-principles
│   ├── design             (produces design artifacts: specs, architecture, atoms)
│   ├── development        (produces or modifies code — skills included; they're high-level code)
│   ├── code-review        (evaluates code, produces findings)
│   └── pipeline           (advances work items through steps that produce or evaluate code)
└── operations             (session mechanics, configuration, telemetry, memory upkeep)
```

Properties live on the node that owns them and are inherited by descent.
`(relationAll loadsDesignPrinciples PrincipleBoundSkill)`: any skill whose
category descends from `principle-bound` must invoke
`bsky:load-design-principles` before starting work. There is no
"principle-bound" column anywhere — boundness is ancestry, computed, never
stored per-leaf.

## The table the lint parses

| Category | Parent | Declares |
|----------|--------|----------|
| skill | (root) | |
| principle-bound | skill | invokes bsky:load-design-principles |
| design | principle-bound | |
| development | principle-bound | |
| code-review | principle-bound | |
| pipeline | principle-bound | |
| operations | skill | |

## Rules

- **Skills declare leaves only.** `category: principle-bound` in frontmatter
  is an error — pick the concrete kind.
- **One category per skill.** A skill that seems to need two is either a
  pipeline skill or wants splitting.
- **New categories are added here first**, in the same PR that first uses
  them. A category that exists only in a skill's frontmatter fails CI.
- **Leaf categories need members; abstract categories need children and a
  declaration.** A leaf used by zero skills is rot. An abstract node is
  legitimate exactly when it has ≥1 concrete descendant AND ≥1 declaration
  of its own (Pace's abstract-class criterion) — `principle-bound` earns its
  place by carrying the loader obligation. `no-direct-skills ∧ no-children ∧
  no-own-declaration → fail`.
- **Classification is judgment; sibling review checks it.** The lint can
  verify a category exists — it cannot verify the category is right.
