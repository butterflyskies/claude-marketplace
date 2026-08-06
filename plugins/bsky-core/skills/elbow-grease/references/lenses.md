# Six review lenses

Run these as independent passes. Overlap is allowed; silently omitting a lens is not.

## Safety

- Panics, crashes, undefined behavior, deadlocks, livelocks, races, and unsafe code.
- Resource exhaustion, unbounded work, missing timeouts, leaks, and cleanup on every error path.
- Partial failure, retry, cancellation, idempotency, and inconsistent state transitions.
- Operational failure modes: startup, shutdown, migration, rollback, degraded dependencies, and observability.

## Design

- Alignment with requirements, architecture, invariants, and public contracts.
- Responsibility boundaries, coupling, duplication, unnecessary API growth, and dead paths.
- Wiring from entry point through configuration and callers to consumers; code that exists but is never active.
- Correct abstraction altitude, lifecycle ownership, state modeling, and backward compatibility.

## Security

- Authentication, authorization, confused deputy paths, privilege boundaries, and actor identity.
- Input validation, injection, path traversal, SSRF, deserialization, supply-chain trust, and secret handling.
- Cryptographic misuse, unsafe defaults, fail-open behavior, and error/log disclosure that enables attack.
- Abuse cases across every external boundary, including sibling operations.

## Privacy

- Collection, inference, retention, replication, logging, export, and deletion of personal or sensitive data.
- Audience and consent mismatches, cross-tenant or cross-channel disclosure, and metadata leakage.
- Data minimization, purpose limitation, redaction, provenance, access trails, and recovery copies.
- Treat privacy separately from security: authorized access can still violate purpose, audience, or consent.

## Idiomacy

- Repository and language conventions, standard library choices, error/result handling, and naming.
- Type-system leverage, ownership patterns, API ergonomics, and maintainable control flow.
- Needless cleverness, brittle parsing, platform assumptions, version compatibility, and generated-file discipline.
- Comment and documentation accuracy where incorrect guidance can produce defects.

## Tests

- Coverage of requirements, branches, boundaries, state transitions, failures, and regressions.
- Test oracles that assert behavior rather than merely execute code; reject vacuous or self-fulfilling tests.
- Determinism, isolation, cleanup, fixtures, concurrency, timing, and false-positive/negative risks.
- Correct test altitude: unit for pure logic, integration for wiring/I/O, fault injection for failure behavior, and proofs only for suitable finite invariants.
