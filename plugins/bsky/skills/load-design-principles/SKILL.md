---
name: load-design-principles
category: operations
description: "Load every design principle from bundled files. Invoked by principle-bound skills before they start work. Reads from repo files; CC overlay is optional."
---

# /load-design-principles — The Canonical Principle Load

Load the complete set of design principles. This skill exists so principle-bound
skills share one loading procedure instead of each carrying a copy that can drift.

## Procedure

1. **Read the bundled principles:** read every `.md` file in
   `plugins/bsky/design-principles/v1/` (excluding `index.md`). These are the
   canonical baseline — they work standalone with no external dependencies.

2. **Phantom-set guard:** if the directory is empty or missing, STOP and flag it
   loudly — the principle set has gone phantom. Do not proceed as if the set
   were legitimately empty.

3. **Optional CC overlay:** if a `collective-conscious` MCP server is available,
   enrich the baseline with house-specific context:
   ```
   list scope: "shared"
   ```
   Filter to memories whose `tags` include `principle`. For each CC memory that
   matches a bundled principle by name, merge any house-specific worked examples,
   project-specific applications, or local amendments into the digest. CC entries
   that don't match a bundled principle are additional house-local principles —
   include them in the digest but mark them as house-specific.

   **This step is optional.** The bundled files are canonical and sufficient on
   their own. CC is an enrichment layer for teams that maintain one, not a
   requirement.

4. **Hold the contents** as working context for injection into sub-agent prompts.

## Output

Return the loaded principles as a digest the calling skill can inject into
sub-agent prompts: one section per principle, name + core rule + how-to-apply.

## Callers

Principle-bound skills — any skill whose category descends from
`principle-bound` in `plugins/SKILL-CATEGORIES.md` (e.g. design or
code-review skills) — invoke this before starting work and pass the digest
to every sub-agent they dispatch. The sub-agent boundary is where
instruction dies, so the caller carries it across.
