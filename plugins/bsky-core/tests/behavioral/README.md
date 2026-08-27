# Behavioral receipts

These fixtures preserve exact prompt/result receipts for the five Syne-owned
Codex adaptations at source revision
`d29910dc302e8b7008df4b9fdc291a9cc9cad115`.

`ari-three-skill-independent-receipts-20260824.json` separately covers the
later `briefing`, `land`, and `scope-sharpen` ports. Each immutable prompt and
structured result is hash-bound to the exact skill bytes. The evaluator was a
fresh independent Codex subagent under the same coordinator and thread, not a
cross-provider evaluator, and performed instruction tracing rather than live
service execution.

That file remains historical evidence for its exact August 24 bytes.
`ari-scope-governance-independent-receipt-20260827.json` supersedes only the
current `scope-sharpen` binding after the shared scope-governance change. It
records Ari's independent remote-SHA review and fresh instruction traces across
the Claude and Codex provider surfaces; it does not rewrite the older receipt.

The receipts distinguish three kinds of evidence:

- `real_workflow`: the candidate instructions were applied to the actual parity
  change and the cited repository/GitHub state can be checked independently;
- `live_script`: bundled executable behavior was run against the bound current
  Codex session and is also covered by isolated success/failure tests; and
- `synthetic_decision`: an exact scenario was evaluated through the workflow's
  decision rules without performing external writes.

The four instruction-only workflows were exercised by the same Codex
coordinator that authored the adaptation. They are exact forward receipts, but
they are not fresh-context or independent-model evidence. The receipt says so
instead of laundering that limitation into a green label. `token-audit` has the
stronger executable evidence described in its case.

The three later cases use a separate fresh subagent. Their oracle checks
structured decisions and receipt bindings rather than matching explanatory
phrases. It does not claim live notification, forge, tracker, memory,
repository, or collaboration effects.

Run the oracle with:

```bash
python -m unittest plugins/bsky-core/tests/test_behavioral_receipts.py
```

The oracle binds each result to the exact skill digest and checks the
skill-specific behavioral invariants. It does not install or activate the
plugin and does not authorize merge, deployment, or a shared-name overwrite.
