---
name: defrag
description: "Memory consolidation for memory-mcp instances. Scans for near-duplicate, overlapping, or stale memories and merges, prunes, or flags them. Use when asked to defragment, consolidate, or clean up memories."
model: haiku
---

# /defrag — Memory Consolidation

Replay, Evaluate, Merge. Scans a memory-mcp scope for near-duplicate, overlapping,
stale, or contradictory memories. Merges duplicates, prunes obsolete entries, strengthens
cross-links, and flags conflicts.

**Schedule:** weekly cron or on-demand. Not every session.

## Arguments

`$ARGUMENTS` is optional. Parse flags from the argument string:

| Flag | Default | Meaning |
|------|---------|---------|
| `--scope <scope>` | `all` | Memory scope to scan. `shared` = global only; `all` = all scopes |
| `--dry-run` | off | Show what WOULD happen without making changes |
| `--model <model>` | `haiku` | Model for this skill (cheap, mechanical work) |
| `--dup-threshold <float>` | `0.15` | Embedding distance below which two memories are near-duplicates |
| `--related-threshold <float>` | `0.30` | Distance below which two memories are related-but-distinct |
| `--auto-prune` | off | Auto-delete stale memories instead of flagging for review |

Parse with positional-aware flag extraction. Unrecognized tokens are ignored with a
warning. Example invocations:

```
/defrag                              # scan all scopes, flag only
/defrag --scope shared --dry-run     # preview global-scope consolidation
/defrag --auto-prune --dup-threshold 0.10   # aggressive merge + auto-prune
```

## Phase 1: Replay

Enumerate all memories in the target scope.

1. Call `list` with the appropriate scope parameter:
   - `--scope shared` -> `list` with no scope (global only)
   - `--scope all` -> `list` with `scope: "all"`
   - `--scope <name>` -> `list` with `scope: "<name>"`

2. Collect the returned list of memory names and descriptions. Store as the
   working set. Record the total count for the final report.

3. If the working set is empty, report "No memories found in scope" and exit.

4. If a scope has 5+ memories but no index memory, note this for the report
   (recommendation to create an index).

## Phase 2: Evaluate

Lazy evaluation: use pairwise `recall` to find candidates, then `read` only the
flagged pairs. Do NOT read every memory upfront.

### 2a. Pairwise duplicate detection

For each memory in the working set:

1. Call `recall` using the memory's name and key terms from its description
   as the query. Set `limit: 10`.

2. From the recall results, examine embedding distances for other memories in
   the working set (ignore self-matches):
   - **distance < dup-threshold**: flag as **near-duplicate** pair
   - **dup-threshold <= distance < related-threshold**: flag as **related** pair

3. Deduplicate flagged pairs (A,B is the same as B,A). Use the lower distance
   as the canonical score.

### 2b. Staleness detection

For each memory in the working set, check for staleness by reference type.
Extract references from the memory's description (defer full `read` until needed):

- **File references** (`/path/to/file`): test existence with `test -f <path>`.
  If the file doesn't exist, flag as potentially stale.
- **PR references** (`owner/repo#N` or GitHub PR URLs): check status with
  `gh pr view <number> --repo <owner/repo> --json state --jq '.state'`.
  If the PR is merged or closed and the memory describes it as open/pending,
  flag as stale.
- **Issue references** (`owner/repo#N` or GitHub issue URLs): check status with
  `gh issue view <number> --repo <owner/repo> --json state --jq '.state'`.
  If the issue is closed and the memory describes it as open/active, flag as stale.
  Disambiguate PR vs issue references by trying `gh pr view` first — if it 404s,
  fall back to `gh issue view`.
- **Person references**: check if an anchor memory exists in
  `person-<name>` scope via `list`. If no anchor memory exists, flag for
  review (the person reference may be orphaned or the person scope renamed).
- **Branch references** (`branch: <name>`): check with
  `git ls-remote --heads origin <branch> 2>/dev/null`. If the branch no longer
  exists on any relevant remote, flag as stale.
- **Scope references** (`[[scope-name/...]]` or explicit scope mentions): check
  whether the referenced scope still has any memories by calling `list` with that
  scope. If `list` returns empty, the scope is effectively dead — flag the
  reference as stale.

Only perform staleness checks that are practical in the current environment.
Skip checks that require repos not currently cloned.

### 2c. Conflict detection

When two memories are flagged as near-duplicates or related, note if their
descriptions suggest contradictory content. Examples:
- One says "use approach A" and the other says "use approach B"
- One marks something as complete, the other as in-progress
- Different values for the same configuration or threshold

Flag these separately as **conflicts** -- they need human judgment, not
mechanical merging.

### 2d. Cross-construct provenance

When scanning `--scope all`, memories from different scopes may have different
authors or constructs. Before flagging a cross-scope pair as duplicates:

1. Note the scope of each memory in the pair
2. If the scopes differ, mark the pair as **cross-construct** -- these require
   extra care and should never be auto-merged
3. Include author/scope provenance in the report

### 2e. Cross-instance dedup (shared vs private)

When `--scope all` is active, scan the `collective-conscious` (shared) scope
against each private scope for content stored in both places:

1. Call `list` with `scope: "collective-conscious"` to enumerate shared memories.
2. For each shared memory, call `recall` against each private scope using the
   shared memory's name and key terms. Use the same `dup-threshold`.
3. For each hit below `dup-threshold`:
   - `read` both the shared and private memory
   - Determine which is richer (more detail, more cross-links, more recent edits)
   - Flag the pair with a recommendation:
     - If the shared version is richer or equivalent: recommend removing the
       private copy (it's redundant)
     - If the private version is richer: recommend promoting the private version
       to shared (edit the shared memory with the richer content, then remove
       the private copy)
     - If they've diverged meaningfully: flag as a **conflict** for human review
4. In `--auto-prune` mode, execute the recommendation for non-conflicting pairs.
   In normal mode, flag for review. In `--dry-run` mode, report only.

This phase prevents the same knowledge from accumulating in both shared and
private stores over time.

## Phase 3: Merge

Process flagged pairs. In `--dry-run` mode, describe each action without executing.

### 3a. Near-duplicates

For each near-duplicate pair:

1. `read` both memories to get full content
2. Compare content:
   - If one is a strict subset of the other, the superset is the survivor
   - If both have unique content, combine: use the richer version's structure
     as the base, weave in unique details from the other
   - For cross-construct pairs: **do not auto-merge**. Report with both
     contents and recommend human review. Note the author/scope of each.
3. If not `--dry-run` and not cross-construct:
   - `edit` the survivor with the merged content
   - `forget` the duplicate
   - Add `[[cross-ref]]` links if the merged content references other memories
4. Record the action: which memory survived, which was removed, what content
   was preserved

### 3b. Stale memories

For each stale memory:

1. `read` the memory to confirm staleness from full content
2. Classify:
   - **Fully stale**: all references are dead, content is obsolete
   - **Partially stale**: some references dead, but core content still valid
3. For fully stale memories:
   - If `--auto-prune`: `forget` the memory. Record the action.
   - Otherwise: flag for human review with a summary of why it's stale
4. For partially stale memories:
   - If `--auto-prune`: `edit` to remove dead references, add a note about
     what was cleaned. Do NOT delete the memory.
   - Otherwise: flag for human review with specific stale references listed

### 3c. Related memories (cross-link strengthening)

For related-but-distinct pairs that are NOT duplicates:

1. `read` both memories
2. Check if either already contains a `[[cross-ref]]` to the other
3. If not, and the relationship is meaningful (not just coincidental keyword overlap):
   - `edit` each to add a `[[other-name]]` cross-reference in a "See also" section
4. Record the cross-link addition

### 3d. Conflicts

Conflicts are **never auto-resolved**. For each conflict:

1. `read` both memories
2. Present both versions with the specific contradiction highlighted
3. Suggest resolution options:
   - Keep A, discard B
   - Keep B, discard A
   - Merge with specific resolution (state which version of the conflicting
     fact to keep)
4. In `--dry-run` mode or normal mode: report only, do not act
5. If the user is present and interactive: ask for resolution. Apply if given.

## Phase 4: Report

After all phases complete, output a structured summary.

### Report format

```
## Memory Defrag Report

**Scope:** <scope scanned>
**Mode:** <normal | dry-run>
**Thresholds:** dup < <dup-threshold>, related < <related-threshold>

### Summary

| Metric | Count |
|--------|-------|
| Memories scanned | N |
| Near-duplicates found | N |
| Duplicates merged | N |
| Stale memories found | N |
| Stale pruned/cleaned | N |
| Stale flagged for review | N |
| Cross-links added | N |
| Conflicts found | N |
| Cross-instance duplicates | N |
| Index recommendations | N |

### Actions Taken

#### Merged
- **survivor-name** absorbed **removed-name** (distance: 0.08)
  Kept: <brief description of what was preserved>

#### Pruned
- **memory-name** — stale: <reason>

#### Cross-links Added
- **memory-a** <-> **memory-b** (distance: 0.22)

### Flagged for Review

#### Stale (manual review needed)
- **memory-name** — <reason for staleness>
  References: <dead ref 1>, <dead ref 2>

#### Conflicts
- **memory-a** vs **memory-b** (distance: 0.12)
  Contradiction: <brief description>
  Suggestion: <recommended resolution>

#### Cross-construct Duplicates
- **scope-x/memory-a** vs **scope-y/memory-b** (distance: 0.09)
  Both scopes must agree before merging.

#### Cross-instance Duplicates (shared vs private)
- **collective-conscious/memory-a** vs **private-scope/memory-b** (distance: 0.07)
  Recommendation: <keep shared | promote private | conflict — diverged>

### Recommendations
- <scope> has N memories with no index — consider creating one
- <other actionable suggestions>
```

Omit empty sections. In `--dry-run` mode, prefix all action items with
"[DRY RUN]" and change "Actions Taken" to "Actions Proposed".

### Post-report

After generating the report:

1. Call `sync` to push any changes made during the merge phase
2. If conflicts were found and the user is interactive, offer to resolve them
   one at a time
3. Output report feeds into session-handoff if findings are significant

## Constraints

- **Never auto-delete without `--auto-prune`.** Default behavior is flag-only
  for stale memories. Near-duplicate merges (where the content is preserved in
  the survivor) proceed in normal mode but not in `--dry-run`.
- **Respect scope boundaries.** When `--scope` targets a specific scope, do not
  touch memories in other scopes even if recall surfaces them.
- **Cross-construct merges require human approval.** Memories from different
  scopes may belong to different authors or contexts. Flag but do not merge.
- **Preserve author provenance.** When merging, if the original memories have
  different authorship context, note both authors in the merged content.
- **Lazy evaluation.** The sequence is: `list` -> pairwise `recall` -> `read`
  only flagged pairs. Do not blow context by reading every memory upfront.
- **Idempotent.** Running defrag twice in a row should produce no new actions
  on the second run (all duplicates already merged, all cross-links already added).

## Model selection

This skill defaults to **haiku** (set in frontmatter). The work is mechanical:
listing, comparing distances, reading pairs, editing content. No judgment-heavy
analysis that would benefit from a larger model. Override with `--model` if needed.
