---
name: token-audit
description: Inspect the current Codex session's recorded token counts, context-window pressure, cache usage, and rate-limit state from its local rollout log. Use when asked about Codex token usage, context consumption, cached input, or current subscription limits. Do not use it to estimate API cost or future burn without an authoritative pricing and billing source.
---

# Token Audit

Run `scripts/token_audit.py` to read the latest `token_count` event for the current `CODEX_THREAD_ID` from Codex's local rollout logs.

## Workflow

1. Confirm `CODEX_THREAD_ID` is present. If it is absent, ask for an explicit rollout path or report that the current session cannot be identified.
2. Run the script relative to this skill directory:

   ```bash
   python scripts/token_audit.py full
   ```

   Use `snapshot` to omit warnings or `json` when structured output is needed.
3. Relay the output with its timestamp. Describe it as the latest recorded event, not a live billing query.
   If an explicit rollout was used while `CODEX_THREAD_ID` was unavailable, disclose that the file was not verified as the current session.
4. If the script reports an unsupported schema, stop. Do not guess field meanings or substitute Claude statusline data.

## Evidence boundary

This adaptation is version-bounded to the rollout event shape observed in Codex CLI 0.145.0:

- `payload.info.total_token_usage`
- `payload.info.last_token_usage`
- `payload.info.model_context_window`
- `payload.rate_limits`

The script fails closed when these fields are absent or malformed. It calculates only ratios whose operands are present in the event: last-request input as a percentage of the model context window and cached input as a percentage of last-request input.

Codex's rollout event does not expose authoritative API-equivalent cost, subscription value, or elapsed-session burn rate. Omit cost, monthly multipliers, and time-to-exhaustion projections unless the user supplies an authoritative source for every required input and explicitly asks for that separate calculation.

## Safety

- Treat rollout logs as local session records; do not publish raw logs.
- Report aggregate counters only. Never echo prompts, messages, tool arguments, or credentials from the JSONL.
- Keep this workflow read-only.
