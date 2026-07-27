# No Dead Code

Delete code that nothing reaches: unused functions, unreferenced fields,
commented-out blocks, branches that can't execute, `TODO`-stubs wired to nothing.
Version control remembers what you remove — you don't need to keep a corpse in
the tree to get it back.

**Why:** dead code costs every reader who must decide whether it's live, every
refactor that must drag it along, every search that surfaces it as a false hit.
Commented-out code is worse than deleted code: it looks intentional, rots
silently, and misleads the next reader about what runs.

**How to apply:**
- Found an unused symbol? Delete it, don't `#[allow(dead_code)]` it — the
  annotation is a promise to reads-as-live that never pays out.
- Never comment out code "for later." Later is a git branch or a stash, not a
  block of `//` in main.
- Turn on the linter's dead-code detection and keep it at zero; a leak of one
  makes the next one invisible (see [fix-the-class](fix-the-class.md)).

**The one carve-out:** a genuinely-not-yet-wired public API or a
platform-conditional path can look dead to a local analysis. Mark those
explicitly with a reason, don't blanket-suppress.

Related: [no-historical-trivia](no-historical-trivia.md), [right-altitude](right-altitude.md), [dry](dry.md)
