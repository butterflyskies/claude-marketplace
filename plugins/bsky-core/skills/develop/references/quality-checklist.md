# Quality checklist

Use repository-native commands. The examples below are prompts for discovery, not permission to install tools or rewrite configuration.

## Automated checks

- Rust: formatter, Clippy with warnings denied, focused and workspace tests, release build when relevant.
- Python: formatter, linter, configured type checker, and repository test runner.
- TypeScript or JavaScript: formatter, linter, type checker, and test runner.
- Go: formatter/imports, vet, configured linter, and tests.

Run focused checks first, then broader checks proportional to risk. Never report an unavailable or unexecuted check as passed.

## Manual checks

- accidental scope, generated noise, secrets, and unrelated user changes;
- dead code, stale comments, and misleading documentation;
- swallowed errors and incomplete result handling;
- resource cleanup, timeouts, and externally triggered bounds;
- public API growth and backward compatibility;
- changed branches, state transitions, boundaries, and failure paths with no test; and
- tests whose oracle moves with the implementation.

Report exact commands, results, and residual gaps.
