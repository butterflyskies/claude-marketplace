# Construct-Owned Workspaces and Review Handoffs

Constructs sharing a host should maintain separate construct-owned repo clones/workspaces. Collaborate through pushed origin refs when available.

For pre-push review, the author creates an immutable snapshot or copied handoff artifact plus a canonical manifest of exact file hashes. Name the snapshot by content: `snapshot_id = digest(canonical_manifest)`. The reviewer copies that snapshot into their own workspace and returns a receipt bound to the snapshot ID. Reviewers do not tail a mutable author working tree.

If a shared writable directory is deliberately used, split coordination across explicit phases: intent, confirmation, action, receipt. Account for delivery and inference lag; do not assume conversational ordering makes concurrent filesystem mutation safe.
