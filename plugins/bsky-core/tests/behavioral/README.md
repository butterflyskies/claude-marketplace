# Behavioral receipts

These fixtures preserve exact prompt/result receipts for the five Syne-owned
Codex adaptations at source revision
`d29910dc302e8b7008df4b9fdc291a9cc9cad115`.

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

Run the oracle with:

```bash
python -m unittest plugins/bsky-core/tests/test_behavioral_receipts.py
```

The oracle binds each result to the exact skill digest and checks the
skill-specific behavioral invariants. It does not install or activate the
plugin and does not authorize merge, deployment, or a shared-name overwrite.
