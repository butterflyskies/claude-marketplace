# Attractive Nuisance Principle

A system that accepts correct-looking input in the wrong place — and does the wrong thing — is an attractive nuisance. Liability falls on the system, not the person who put things there.

The failure mode: someone does the right thing in the wrong place. No error, no warning, no redirect. The action looks like it worked. The damage surfaces later, somewhere else, disconnected from its cause.

**The rule:** if a system has a place where reasonable input is accepted but produces wrong behavior, fence it or fill it in.

- **Fence it:** refuse the write, warn visibly, or redirect to the right place
- **Fill it in:** eliminate the duplicate. one canonical location, no alternatives

**Test:** do the right thing in the wrong place. if the system doesn't stop you, you have an attractive nuisance.

## Known instances

- **Duplicate config files** — edits to the wrong one silently succeed, harness reads the other
- **Shadowed ENV vars** — set at one layer, overridden at another, no warning
- **Dead API endpoints** — accept requests, return 200, route to nothing
- **Overlapping memory scopes** — edit global when you meant project, both accept the write
- **Silent pattern matches** — matcher fires but no action is configured (no emoji, no reason text)
- **Stale re-exports** — look canonical, compile fine, point to old code
- **Zombie migrations** — still parse, no longer apply, no error on run

Related: [fix-the-class](fix-the-class.md)
