# Public Core, House Overlay

Separate generally useful behavior from this group's specifics. The public core must stand alone for a stranger's team. House policy and adapters layer on top and never leak inward.

## Ownership

- Public core: neutral schemas, invariants, protocols, lifecycle, algorithms, extension points.
- House overlay: people/construct IDs, Discord channels, provider instances, consent/policy defaults, voice/lore/rituals, credentials, local routing.
- Dependencies point house -> core, never core -> house.
- Concrete tools/providers map to stable core concepts through adapters.

## Apply it

- Ask per module/file/sentence: "Would a stranger's team understand and want this without knowing us?" Yes -> core. Names a person, channel, house norm, or our infrastructure -> overlay.
- Enforce the seam: vocab-lint and packaging/fixture tests should fail when house terms, identifiers, secrets, or policy defaults leak into core.
- Put storage, transport, and framework details behind contracts with conformance tests (see [traits-at-boundaries](traits-at-boundaries.md), [dependency-direction](dependency-direction.md)).
- Prefer generating a public artifact from one source over maintaining a fork.
- A feature may remain private when separation would expose policy or create a false generalization. Make that explicit.

## Why

This enables sharing without leaking private relationships or policy, keeps improvements flowing to one core, and makes craft portable.

Related: [traits-at-boundaries](traits-at-boundaries.md), [dependency-direction](dependency-direction.md)
