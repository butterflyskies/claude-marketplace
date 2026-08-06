# Architectural review dimensions

Use this compact pass only when a fuller review skill is unavailable.

## Contracts and compatibility

- Does behavior match the accepted requirements?
- Are public interfaces and serialized formats compatible or deliberately migrated?
- Are callers and sibling operations updated consistently?

## Architecture and completeness

- Do dependencies point toward stable domain boundaries?
- Are responsibilities, lifecycles, and state transitions explicit?
- Are all input shapes, branches, error paths, cancellation paths, and cleanup paths handled?
- Is the mechanism wired into the production entry and exit paths?

## Security and privacy

- Verify authentication, authorization, actor identity, input boundaries, secret handling, and fail-closed behavior.
- Separately examine collection, audience, retention, aggregation, provenance, deletion, and metadata leakage.

## Simplicity and tests

- Is complexity placed at the cheapest correct boundary?
- Are there dead paths, speculative abstractions, or duplicated procedures?
- Can each test fail for the behavior it claims, using an independent oracle?

Report only verified findings with severity, location, mechanism, impact, remedy, and evidence.
