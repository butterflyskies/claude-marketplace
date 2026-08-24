# Migration checklist

Use this for a dependency replacement, module rewrite, storage change, protocol migration, or provider swap.

## Characterize the old behavior

Inventory observable behavior before writing the replacement:

- success and error behavior;
- defaults, environment variables, paths, and configuration;
- bounds, timeouts, batching, queue or pool limits;
- caching and persistence locations;
- normalization and serialization contracts;
- concurrency, cancellation, and panic behavior; and
- deployment or operational assumptions.

Trace the production wiring so an existing but unreachable safety mechanism is not counted as behavior.

## Preserve or change deliberately

Map every inventoried behavior to `preserve`, `change`, or `remove`, with rationale and migration impact. Write a test that would fail if each preserved behavior disappeared. Use the public boundary and an oracle independent of either implementation.

Keep the old path until the replacement passes the behavioral matrix unless the migration plan explicitly requires a flag day. Verify the full input-to-output path, not only the new component.

## Finish

Update affected CI, images, manifests, configuration, and user documentation. State rollback prerequisites and any irreversible data transformation before external activation.
