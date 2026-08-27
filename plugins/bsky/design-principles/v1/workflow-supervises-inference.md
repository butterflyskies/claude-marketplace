# Workflow Supervises Inference

Use models for their range, conversation, design, and implementation ability. Do not rely on inference to supervise its own process consistently.

The external workflow layer owns sequencing, durable state, work leases, artifact and instruction versions, verification receipts, review gates, findings, revision invalidation, and eligibility for merge. A model may perform each transition's work, but it cannot assert the next privileged state without the required machine-checkable receipt.

A review receipt is bound to the exact artifact digest and instruction/policy version it examined. Any change to the artifact or governing instructions invalidates that receipt and returns the work to review-required.

This preserves what people value in conversation while structurally containing substrate-specific process failures.
