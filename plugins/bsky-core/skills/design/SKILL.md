---
name: design
description: Structure evidence-grounded software design and produce proportionate problem, requirements, architecture, threat-model, test-plan, and handoff artifacts. Use before implementing a feature, migration, public interface, security-sensitive change, or risky refactor; when a defect needs design-level characterization; or when reviewing and revising an existing design.
---

# Design

Turn an uncertain change into a reviewable design whose requirements, risks, and verification remain traceable. Conversational design advice remains conversational unless the user asks to author or revise repository artifacts. For in-repository design work, keep artifacts under `docs/design/` or `docs/design/<component>/`.

## Preflight

1. Read repository instructions and existing design artifacts completely.
2. Load `$bsky-core:load-design-principles` when it is available and the work is principle-bound. Apply the resulting digest rather than merely citing it.
3. Recall relevant project or shared memory only when its MCP server is available. Mark recalled memories applied after use.
4. Inspect the current implementation when extending an existing system. Prefer `rg`, repository-native inspection, and read-only commands; do not assume unavailable symbolic tools.
5. Parse explicit modes such as `problem`, `requirements`, `architecture`, `threat-model`, `test-plan`, and `review`. Verify prerequisite artifacts before a phase-only request.

## Calibrate depth

Recommend a proportional path and explain the blast-radius evidence:

- Lightweight: small, understood, low-risk change; abbreviated problem and requirements, then verification.
- Standard: new component or moderate uncertainty; problem, requirements, architecture, threat-model decision, verification.
- Full: greenfield, public API, sensitive data, regulatory, or security-critical work; all phases.

Ask the user to confirm the depth when it materially changes scope or ceremony. Do not manufacture a gate for an already explicit, narrow request.

## Build the design

### 1. Problem

Capture who is affected, current failure or opportunity, trigger, inputs, outputs, transformations, boundaries, constraints, non-goals, success criteria, and failure signals. Write `problem.md` and present consequential assumptions for confirmation.

### 2. Requirements

Enumerate normal, abuse, and security use cases. Derive testable requirements with stable IDs and trace each to its source use cases. For relevant security requirements, use OWASP ASVS categories as prompts, not a mechanical checklist; record reviewed and inapplicable categories with short rationales.

Maintain an SRTM:

```markdown
| Req ID | Requirement | Source use case | ASVS | Test case |
|--------|-------------|-----------------|------|-----------|
```

Write `requirements.md`. Obtain explicit approval before architecture when requirements or scope remain negotiable.

### 3. Architecture

Define component responsibilities, data model, integration boundaries, protocols, technology choices, resource lifecycles, failure behavior, and concurrency. Make invariants structural where practical and keep conversions at boundaries. Prefer message passing for shared state; use locks deliberately where side effects require serialization.

At every meaningful architecture or topology level, surface the viable alternatives and compare their operational consequences rather than presenting the first workable shape as inevitable. Always include a materially cheaper viable alternative when one exists, even when recommending against it. Compare at least implementation cost, ongoing operating cost, failure domains, reversibility, migration burden, and which requirements each option leaves weaker. Record why the recommended option earns its extra complexity.

Produce readable Mermaid diagrams only when they clarify the design: system context, components, trust-boundary data flow, core schema, and the few critical sequences. The coordinator may draft these directly. For independent diagram generation, use `collaboration.spawn_agent` only when subagents are available and allowed; provide the agreed decisions and requirements, do not hard-code a model, and review every generated flow and trust boundary before accepting it.

Record significant decisions as proposed ADRs or in `architecture.md`, according to repository convention. Present the result and uncertainties for approval before threat modeling.

### 4. Threat model

Offer full STRIDE, lightweight review, defer, or skip based on exposed trust boundaries and impact. Wait for the user's choice when the phase would materially expand scope.

For each flow crossing a trust boundary, evaluate spoofing, tampering, repudiation, information disclosure, denial of service, and elevation of privilege. State concrete attack preconditions, likelihood, impact, and mitigation. Check input boundaries, authorization, sensitive logs/errors, resource exhaustion, and supply-chain privilege. Use a fresh subagent for independent enumeration when useful, then verify its claims against the architecture.

Feed accepted new requirements and architecture changes backward into the SRTM and diagrams. Write `threat-model.md` only when analysis was performed.

### 5. Verification plan

Replace every SRTM placeholder with a concrete unit, integration, system, property, proof, fault-injection, or manual test. State fixtures, oracles, boundaries, and whether each test is automated. Write `test-plan.md`, update the SRTM, and maintain `README.md` as the design index and phase-status record.

## Review mode

Compare `docs/design/` with current code, history, review findings, and tests. Report drift, stale assumptions, missing traceability, unused ceremony, and concrete revisions. Separate verified facts from inference.

Review requests are read-only by default. Report proposed revisions and edit design artifacts only when the user asks to revise or update them.

## Artifact rules

- Start each artifact with a `design-meta` comment containing status, last-updated date, and phase.
- Use relative cross-links and stable IDs.
- Draft for reasoning, not polish.
- Record skipped phases and why.
- Never silently overwrite user-authored design decisions. Use `apply_patch` for local edits and preserve unrelated work.
- End with implementation-ready acceptance criteria, open decisions, risks, and the next physical action.
