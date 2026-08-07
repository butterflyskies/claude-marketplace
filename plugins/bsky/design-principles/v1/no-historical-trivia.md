# Historical Trivia Belongs in Commit Messages, Not Code

Code and docs describe what IS. History — what a thing replaced, which bug
motivated it, who proposed which clause — lives in the commit message, the PR
thread, and memory. A comment narrating the past goes stale the moment the
past stops mattering, and it costs every future reader a detour.

**The redaction test:** when you kill a bad design, don't leave its obituary
in the code ("there is no X anymore", "this used to be a flag"). State the
current invariant positively. If the negative framing is doing real work —
warning against a likely wrong turn — that's a constraint, not trivia; keep
it and phrase it as the constraint.

**Extends to attribution:** "(so-and-so's criterion)" in code or canonical
docs is trivia too. Provenance lives in git blame, PR threads, and memory —
the artifact states the rule, not its genealogy.

**How to apply:**
- Writing a comment? Ask: does this describe the code as it stands, or how it
  got here? The latter moves to the commit message.
- Reviewing? Flag comments about replaced designs, past bugs, or authorship.
- Memories and fortune entries are the OPPOSITE case: there, provenance is
  the point. This principle governs code and canonical artifacts only.

Related: [meaningful-identifiers](meaningful-identifiers.md), [dry](dry.md)
