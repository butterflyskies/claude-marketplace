# Implementation guide

Use this reference for a bounded implementation slice. Repository instructions and the accepted plan remain authoritative.

## Brief

Give the implementer:

- the intended behavior and observable acceptance criteria;
- owned files and explicit exclusions;
- applicable design decisions and principles;
- repository-native format, lint, test, and build commands;
- authority boundaries, especially external writes; and
- required receipts.

Do not prescribe a conclusion when discovery is part of the task. If the plan is wrong, stop or implement the safer in-scope alternative and report the divergence.

## Implementation checks

- Validate external input at the boundary and preserve rich error variants.
- Acquire resources only after checks that can make them unnecessary.
- Bind cleanup to every normal, error, cancellation, and early-return path.
- Apply new guards to sibling operations with the same trust boundary.
- Keep credentials wrapped or redacted until the consumption boundary.
- Minimize public API growth and preserve compatibility unless the task changes it.
- Write tests for changed behavior using an independent oracle.
- For migrations, read [migration-checklist.md](migration-checklist.md) first.

## Handoff

Report changed files, tests added, commands actually run, failures or environmental gaps, and plan divergences. Do not commit, push, publish, merge, deploy, or message externally unless that exact action is authorized.
