---
name: load-design-principles
category: operations
description: "Load every design principle from collective-conscious. Invoked by principle-bound skills before they start work. Tag-as-index: list + filter, never semantic recall."
---

# /load-design-principles — The Canonical Principle Load

Load the complete set of design principles from collective-conscious. This skill
exists so principle-bound skills share one loading procedure instead of each
carrying a copy that can drift.

## Procedure

1. **List the shared scope:**
   ```
   list scope: "shared"
   ```
2. **Filter to principles:** keep every memory whose `tags` include `principle`.
   Tag-as-index: list + filter, never semantic recall — recall returns the top-N
   most similar memories, not the full set. A new principle added yesterday must
   load today without anyone updating an index.
3. **Phantom-set guard:** if zero memories carry the tag, STOP and flag it loudly —
   the principle set has gone phantom (renamed tag or lost scope). Do not proceed
   as if the set were legitimately empty.
4. **Read each principle memory** and hold the contents as working context.

## Output

Return the loaded principles as a digest the calling skill can inject into
sub-agent prompts: one section per principle, name + core rule + how-to-apply.

## Callers

Principle-bound skills (category: design, development, code-review, or pipeline)
invoke this before starting work and pass the digest to every sub-agent they
dispatch — the sub-agent boundary is where instruction dies, so the caller
carries it across.
