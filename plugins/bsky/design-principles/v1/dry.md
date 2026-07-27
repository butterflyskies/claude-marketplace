# Don't Repeat Yourself (DRY)

Abstract once, test once, fix once. The second copy is where the bug lives.

When you're about to duplicate a block — code, config, skill text, prompt boilerplate,
an incantation — stop and extract it into one named place, then reference it. Copies
drift: five copies of a loading block is five chances for four of them to be wrong
after a fix lands in the fifth.

**Applies beyond code:** skills are high-level code. Prompt blocks, SKILL.md
boilerplate, CI check strings, and canonical procedures all count. If two skills carry
the same paragraph, that paragraph wants to be a sub-skill.

**How to apply:**
- Second occurrence = extraction trigger. Don't wait for the third.
- The extracted thing gets a meaningful name (see [meaningful-identifiers](meaningful-identifiers.md))
  and one home; callers reference it.
- Checks then verify the *reference*, not the copied text — one call site, one
  correct implementation.

**The tension to respect:** extraction has a cost. A one-line convenience shared by
two callers may not earn a new module ([attractive-nuisance](attractive-nuisance.md) cuts both
ways — a premature abstraction is its own nuisance). DRY the things that encode
decisions or procedures; tolerate repetition of trivia.

Related: [fix-the-class](fix-the-class.md), [meaningful-identifiers](meaningful-identifiers.md), [attractive-nuisance](attractive-nuisance.md)
