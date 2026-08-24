# Rust guidance

Repository-specific standards override this reference.

## Prefer

- borrowing and iterators over unnecessary cloning or eager collection;
- typed domain boundaries over raw strings and integers;
- `Result` propagation with contextual errors over swallowing or panicking;
- explicit ownership and RAII for resource cleanup;
- small public surfaces, with compatibility-conscious non-exhaustive types where appropriate; and
- property, integration, fault-injection, or bounded-proof tests at the altitude their claims require.

## Challenge

- `unwrap` or `expect` on reachable input and operational paths;
- `unsafe` without a documented invariant and focused verification;
- locks held across `.await`, unbounded channels, and missing cancellation behavior;
- raw secret strings outside the consumption boundary;
- speculative traits with one local implementation and no real seam; and
- vacuous, implementation-mirroring, or round-trip-only tests.

Typical verification is `cargo fmt -- --check`, `cargo clippy -- -D warnings`, repository-configured tests such as `cargo nextest run --workspace`, and the relevant build. Do not install missing tools or substitute commands without disclosing the change.
