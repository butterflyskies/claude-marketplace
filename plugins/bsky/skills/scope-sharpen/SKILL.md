---
name: scope-sharpen
description: "Break a design spec into implementation-ready atoms. Iterative refinement until each piece is small enough for a cheap model to execute reliably."
---

# /scope-sharpen — Iterative Spec Refinement

Takes a design spec and breaks it into implementation atoms — small, testable,
independently executable units of work. Each atom is sharp enough that a sonnet
agent could implement it in a single commit without asking a clarifying question.

## Argument handling

`$ARGUMENTS` provides the configuration:

| Argument              | Required | Description                                       |
|-----------------------|----------|---------------------------------------------------|
| `--spec <file>`       | yes      | Design spec markdown (local file or memory name)  |
| `--model <model>`     | no       | Model for the sharpening agent (default: sonnet)  |
| `--max-depth <N>`     | no       | Recursion limit on splitting (default: 3)         |
| `--self-test`         | no       | Validate atoms by prompting a cheap model          |
| `--output <file>`     | no       | Output file for atom DAG (default: atoms.md)       |

## What "sharp enough" means

An atom is done when a sonnet-tier agent could implement it in a single commit
without asking a clarifying question. This is not a subjective judgment — with
`--self-test`, the skill actually prompts a cheap model with the atom and checks
whether it asks questions. If it does, the atom isn't sharp enough yet.

## Phase 1: Read and orient

1. **Load the spec.** Read the design spec from the provided file. If it's a
   collective-conscious memory name (e.g., `shared/branch-tracking/cpd-spec`),
   recall and load it.

2. **Identify top-level pieces.** Parse the spec into its major components —
   data structures, functions, modules, integration points, configuration,
   tests. Each one becomes a candidate for splitting.

3. **Report.** Post a one-line status: "scope-sharpen started. spec: {file}.
   {N} top-level pieces identified. max-depth: {depth}."

## Phase 2: Sharpening loop

For each piece, at each depth level:

1. **Assess size.** Is this piece small enough? Apply the done-when heuristic:
   could a sonnet agent implement this in a single commit without clarifying
   questions?

2. **If yes:** emit the atom as-is. Record its inputs, outputs, invariants,
   test condition, complexity, and dependencies.

3. **If no:** split it. Identify the sub-pieces, define the interfaces between
   them, and recurse (up to `--max-depth`).

4. **No-code gate.** After each round, check the output for code blocks (```).
   If found, re-prompt: "You are scoping, not implementing. Describe what the
   code should do, not the code itself. Remove code blocks and replace with
   interface descriptions." This is a hard gate, not a suggestion.

5. **Depth limit.** If `--max-depth` is reached and a piece is still too large,
   escalate to opus for re-scoping — the piece needs a different decomposition
   strategy, not finer splitting. If `--model` is already opus, flag it:
   "NEEDS MANUAL SPLIT — exceeded max depth at opus tier." Don't force a bad split.

## Phase 3: Validation

After all atoms are produced:

1. **Coverage check.** Re-read the original spec. For each requirement, verify
   at least one atom addresses it. Flag any gaps: "COVERAGE GAP — {requirement}
   not addressed by any atom."

2. **Scope creep check.** For each atom, verify it traces back to something in
   the original spec. Flag any additions: "SCOPE CREEP — {atom} not in original
   spec."

3. **Dependency consistency.** For each atom's declared dependencies, verify
   the target atom exists. Flag broken links.

4. **Self-test (if `--self-test`).** For each atom, prompt a haiku-tier model
   with: "Implement this: {atom description}. Inputs: {inputs}. Outputs:
   {outputs}. Invariants: {invariants}." If the model asks a clarifying
   question instead of producing an implementation plan, the atom isn't sharp
   enough — flag it and suggest further splitting.

## Phase 4: Output

Produce `atoms.md` (or the `--output` file) as a structured DAG:

```markdown
# Atoms — {spec name}

Source: {spec file}
Generated: {timestamp}
Total atoms: {N}
Coverage: {covered}/{total} requirements

## Dependency graph

{atom-1} ──→ {atom-3}
{atom-2} ──→ {atom-3}
{atom-3} ──→ {atom-5}
{atom-4}  (parallel-safe, no dependencies)

## Atoms

### atom-1: {one-sentence description}

- **Complexity:** trivial | moderate | complex
- **Suggested model:** haiku | sonnet | opus
- **Inputs:** {what it receives}
- **Outputs:** {what it produces}
- **Invariants:** {what must remain true}
- **Test condition:** {executable command + success criteria for ratchet --test}
- **Dependencies:** none | {atom-ids that must complete first}
- **Parallel-safe:** yes | no

### atom-2: ...
```

Post a summary to the channel: "{N} atoms produced from {spec}. {gaps} coverage
gaps, {creep} scope creep flags, {needs_split} needing manual split."

## Composability

Scope-sharpen outputs are designed to feed directly into other skills:

- **ratchet:** each atom becomes a research direction in the scope file. the
  atom's test condition becomes the ratchet's `--test` command.
- **direct dispatch:** each atom is a self-contained agent prompt. spawn one
  agent per atom, respecting the dependency DAG.
- **review-fix-loop:** after atoms are implemented, review the aggregate.

The atoms ARE the program.md research directions. Scope-sharpen is the bridge
between human design and machine execution.

## Constraints

- The sharpener does NOT implement. It scopes. If it produces code, the no-code
  gate catches it and re-prompts. This is enforced, not just instructed.
- Atoms are a DAG, not a flat list. Dependencies and parallel-safety are
  explicit. A flat ordered list doesn't capture which atoms can run concurrently.
- Coverage validation is mandatory. Every requirement in the original spec must
  map to at least one atom. Gaps are flagged, not silently dropped.
- The done-when heuristic is testable: "could sonnet do this in one commit
  without questions?" With `--self-test`, this is verified, not assumed.
