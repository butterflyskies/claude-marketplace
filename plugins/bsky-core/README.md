# Bsky Core for Codex

Codex-native adaptations of selected `bsky` workflows from
`butterflyskies/claude-marketplace@d29910dc302e8b7008df4b9fdc291a9cc9cad115`.

## Included skills

- `design`
- `develop`
- `elbow-grease`
- `keep-the-wheel-turning`
- `load-design-principles`
- `multimodel-elbow-grease`
- `review-fix-loop`
- `skill-forge`
- `token-audit`

The skills preserve portable workflow intent while replacing Claude-only model,
team, hook, statusline, and publication assumptions with Codex-native provider
and authority boundaries. `elbow-grease` freezes the generic contract at six
independent lenses: Safety, Design, Security, Privacy, Idiomacy, and Tests.

`multimodel-elbow-grease` and `review-fix-loop` were transferred through a
hash-bound Callisto handoff. Their exact skill digests and the acceptance
fixture digest are asserted by the package tests.

## Verification

```bash
python -m unittest discover -s plugins/bsky-core/tests -v
python -m unittest discover -s plugins/bsky-core/skills/token-audit/tests -v
```

Exact same-coordinator behavioral receipts and their executable oracle live in
[`tests/behavioral/`](tests/behavioral/). They disclose their independence
limit and keep private live-session counters out of the public package.

The system `plugin-creator` validator and `skill-creator` validator are also run
before publication when those tools are available. Structural validation does
not substitute for fresh-agent behavioral evidence.

Installing this plugin is a separate action from adding it to the marketplace.
Nothing in the package authorizes shared-name activation, external publication,
merge, or deployment by itself.
