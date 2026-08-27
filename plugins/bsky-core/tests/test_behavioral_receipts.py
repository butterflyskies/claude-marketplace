from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "tests" / "behavioral" / "syne-five-skill-receipts-20260806.json"
PORT_RECEIPT_PATH = ROOT / "tests" / "behavioral" / "ari-three-skill-independent-receipts-20260824.json"
SCOPE_GOVERNANCE_RECEIPT_PATH = ROOT / "tests" / "behavioral" / "ari-scope-governance-independent-receipt-20260827.json"
REVIEW_PATH = ROOT / "tests" / "behavioral" / "six-lens-review-20260806.json"
SOURCE_REVISION = "d29910dc302e8b7008df4b9fdc291a9cc9cad115"
EXPECTED_SKILLS = {
    "design",
    "develop",
    "keep-the-wheel-turning",
    "token-audit",
    "skill-forge",
}
PORT_SKILLS = {"briefing", "land", "scope-sharpen"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class BehavioralReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        cls.cases = {case["skill"]: case for case in cls.receipt["cases"]}
        cls.port_receipt = json.loads(PORT_RECEIPT_PATH.read_text(encoding="utf-8"))
        cls.historical_port_cases = {case["skill"]: case for case in cls.port_receipt["cases"]}
        cls.scope_governance_receipt = json.loads(SCOPE_GOVERNANCE_RECEIPT_PATH.read_text(encoding="utf-8"))
        cls.port_cases = dict(cls.historical_port_cases)
        cls.port_cases["scope-sharpen"] = cls.scope_governance_receipt["case"]

    def test_receipt_scope_and_executor_limit_are_explicit(self) -> None:
        self.assertEqual(SOURCE_REVISION, self.receipt["source_revision"])
        self.assertEqual(EXPECTED_SKILLS, set(self.cases))
        executor = self.receipt["executor"]
        self.assertFalse(executor["fresh_context"])
        self.assertFalse(executor["independent"])
        self.assertIn("not fresh-agent", executor["limitation"])

    def test_every_case_is_bound_to_the_exact_candidate(self) -> None:
        for name, case in self.cases.items():
            with self.subTest(skill=name):
                skill = ROOT / "skills" / name / "SKILL.md"
                self.assertEqual(digest(skill), case["skill_sha256"])
                self.assertTrue(case["prompt"].strip())
                self.assertEqual("PASS", case["verdict"])

    def test_design_exercises_traceability_and_real_alternatives(self) -> None:
        result = self.cases["design"]["result"]
        reqs = {item["id"]: item for item in result["requirements"]}
        self.assertEqual({"PAR-1", "PAR-2", "PAR-3", "PAR-4"}, set(reqs))
        self.assertTrue(all(item["test"] for item in reqs.values()))
        alternatives = result["alternatives"]
        self.assertGreaterEqual(len(alternatives), 2)
        self.assertTrue(any(item["materially_cheaper"] for item in alternatives))
        for item in alternatives:
            for key in (
                "implementation_cost",
                "operating_cost",
                "failure_domains",
                "reversibility",
                "migration_burden",
                "weaker_requirements",
            ):
                self.assertIn(key, item)
        self.assertIn(result["recommendation"], {item["name"] for item in alternatives})
        self.assertTrue(result["threats"])

    def test_develop_exercises_implementation_verification_and_gates(self) -> None:
        result = self.cases["develop"]["result"]
        self.assertGreaterEqual(len(result["implementation_atoms"]), 4)
        self.assertIn("plugins/bsky-core/tests/", result["changed_surfaces"])
        boundaries = result["preserved_boundaries"]
        self.assertEqual("butterflysky-syne", boundaries["actor_verified_before_github_write"])
        for key in ("installed", "activated", "merged", "deployed", "live_shared_name_changed"):
            self.assertFalse(boundaries[key])
        self.assertIn("token-audit live bound-session exercise", result["verification"])
        self.assertIn("not independent", result["review_limit"])

    def test_wheel_yields_and_degrades_to_one_read_only_selection(self) -> None:
        result = self.cases["keep-the-wheel-turning"]["result"]
        self.assertEqual("human freshness window", result["scanned"][0]["yield_reason"])
        self.assertEqual("CI in flight", result["scanned"][1]["yield_reason"])
        self.assertEqual("C", result["selected"])
        self.assertEqual("dry-run", result["mode"])
        self.assertEqual(0, result["advanced_items"])
        self.assertEqual([], result["writes"])
        self.assertTrue(result["stopped_after_one_selection"])
        self.assertIn("no standing authorization matrix", result["receipt"])
        self.assertIn("cannot provide atomic exclusion", result["reason"])

    def test_token_audit_is_bound_live_aggregate_only_evidence(self) -> None:
        case = self.cases["token-audit"]
        script = ROOT / "skills" / "token-audit" / "scripts" / "token_audit.py"
        self.assertEqual(digest(script), case["script_sha256"])
        result = case["result"]
        self.assertEqual(0, result["exit_code"])
        self.assertTrue(result["current_session_verified"])
        self.assertTrue(result["public_receipt_redacted"])
        self.assertEqual(
            {"context_window", "last_request", "session_totals", "rate_limits"},
            set(result["aggregate_fields_present"]),
        )
        self.assertFalse(result["prompt_content_emitted"])
        self.assertFalse(result["cost_or_burn_projection_emitted"])
        self.assertEqual("7/7 PASS", result["isolated_tests"])

    def test_skill_forge_exercises_staging_publication_and_activation_split(self) -> None:
        result = self.cases["skill-forge"]["result"]
        self.assertEqual("adapt then publish", result["classification"])
        self.assertFalse(result["live_skill_root"])
        self.assertTrue(result["system_skill_creator_used"])
        self.assertTrue(result["plugin_creator_contract_used"])
        self.assertTrue(result["publication_authorized_separately"])
        self.assertEqual("butterflysky-syne", result["github_actor"])
        self.assertTrue(result["draft_pr"].endswith("/pull/66"))
        for key in ("installed", "activated", "merged", "shared_name_overwritten"):
            self.assertFalse(result[key])

    def test_review_receipt_covers_exactly_six_lenses_and_discloses_degradation(self) -> None:
        review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            {"Safety", "Design", "Security", "Privacy", "Idiomacy", "Tests"},
            {item["lens"] for item in review["lens_results"]},
        )
        self.assertEqual("single-coordinator degraded", review["reviewer"]["mode"])
        self.assertFalse(review["reviewer"]["independent"])
        self.assertEqual("FIXED", review["verified_findings"][0]["disposition"])
        self.assertIn("GitHub Actions has not produced a run", " ".join(review["residual_limits"]))

    def test_port_receipt_evaluator_scope_is_exact(self) -> None:
        receipt = self.port_receipt
        self.assertEqual(SOURCE_REVISION, receipt["source_revision"])
        self.assertEqual("483b57b2f5e5e85cb4caa316a592fc3081601f24", receipt["candidate_base_head"])
        self.assertEqual(PORT_SKILLS, set(self.port_cases))
        evaluator = receipt["evaluator"]
        self.assertEqual("/root/port_bsky_missing/behavioral_evaluator", evaluator["canonical_task_path"])
        self.assertEqual("Codex", evaluator["provider"])
        self.assertTrue(evaluator["fresh_to_this_task"])
        self.assertTrue(evaluator["independent_from_authoring"])
        self.assertEqual("instruction evaluation only", evaluator["scope"])
        self.assertFalse(evaluator["execution_performed"])
        self.assertFalse(evaluator["files_edited"])
        self.assertFalse(evaluator["external_writes"])
        self.assertEqual(
            "Independent Codex subagent under the same coordinator/thread; not cross-provider.",
            evaluator["limitation"],
        )

    def test_port_prompt_result_and_skill_bindings_are_exact(self) -> None:
        for name, case in self.port_cases.items():
            with self.subTest(skill=name):
                self.assertEqual(digest(ROOT / "skills" / name / "SKILL.md"), case["skill_sha256"])
                self.assertEqual(hashlib.sha256(case["prompt"].encode()).hexdigest(), case["prompt_sha256"])
                self.assertEqual(json_digest(case["result"]), case["result_sha256"])
                expected_class = (
                    "independent_cross_provider_instruction_trace"
                    if name == "scope-sharpen"
                    else "independent_static_instruction_trace"
                )
                self.assertEqual(expected_class, case["evidence_class"])
                self.assertEqual("PASS", case["result"]["verdict"])

    def test_scope_governance_receipt_binds_both_provider_surfaces(self) -> None:
        receipt = self.scope_governance_receipt
        self.assertEqual("6bd7f0241c2072c1fd6eadbfe5fb10ed78bf8413", receipt["reviewed_head"])
        self.assertEqual("fcf116aa2d234e055c699ad8199c7c2f1bc9d77d", receipt["reviewed_base"])
        self.assertTrue(receipt["evaluator"]["independent_from_authoring"])
        self.assertTrue(receipt["evaluator"]["remote_ref_verified_at_start_and_finish"])
        self.assertEqual([], receipt["blocking_findings"])
        roots = {
            "claude": ROOT.parent / "bsky" / "skills",
            "codex": ROOT / "skills",
        }
        for provider, skills in roots.items():
            for name, expected in receipt["provider_skill_sha256"][provider].items():
                with self.subTest(provider=provider, skill=name):
                    self.assertEqual(expected, digest(skills / name / "SKILL.md"))

        result = receipt["case"]["result"]
        self.assertFalse(result["missing_packet"]["implementation_ready"])
        self.assertEqual([], result["missing_packet"]["implementation_or_external_writes"])
        self.assertTrue(result["approved_packet"]["per_atom_source_requirements_present"])
        self.assertTrue(result["approved_packet"]["per_atom_relevant_non_goals_present"])
        self.assertTrue(result["approved_packet"]["per_atom_change_control_disposition_present"])
        self.assertFalse(result["out_of_scope_surface"]["operator_tool_or_protocol_silently_added"])
        self.assertTrue(result["out_of_scope_surface"]["owner_approved_scope_revision_required"])

    def test_briefing_port_preserves_observation_and_authority(self) -> None:
        result = self.port_cases["briefing"]["result"]
        self.assertEqual("unchecked", result["notification_state"])
        self.assertFalse(result["notification_empty_claimed"])
        self.assertEqual(
            {"number": 66, "checks": "passing", "review": "changes_requested", "unresolved_review_surfaced": True},
            result["pr"],
        )
        self.assertEqual("unchecked", result["tracker_state"])
        self.assertFalse(result["tracker_fallback_used"])
        self.assertTrue(result["followup"]["due"])
        self.assertFalse(result["followup"]["stored_instruction_authorized_mutation"])
        self.assertFalse(result["followup"]["executed"])
        self.assertFalse(result["followup"]["last_checked_updated"])
        self.assertTrue(result["followup"]["blocked_check_disclosed"])
        self.assertEqual([], result["writes"])

    def test_land_port_separates_effects_and_skips_idempotently(self) -> None:
        result = self.port_cases["land"]["result"]
        self.assertEqual("read_only", result["inventory_mode"])
        self.assertEqual(
            {"memory", "files", "commit", "push", "pull_request", "tracker", "notification", "milestone", "flight_log"},
            set(result["effect_ledger_classes"]),
        )
        self.assertFalse(result["repo_a"]["committed"])
        self.assertFalse(result["repo_a"]["published"])
        self.assertTrue(result["repo_b"]["push_skipped_idempotently"])
        self.assertEqual([], result["remote_mutations"])
        self.assertEqual(["project-scoped handoff if complexity threshold is met"], result["memory_writes"])
        self.assertEqual({"pull_request", "tracker", "milestone", "flight_log"}, set(result["blocked_effects_disclosed"]))

    def test_scope_sharpen_port_covers_source_without_deciding_or_writing(self) -> None:
        result = self.port_cases["scope-sharpen"]["result"]
        self.assertEqual("NO GOVERNING SCOPE PACKET", result["missing_packet"]["reported"])
        self.assertFalse(result["missing_packet"]["implementation_ready"])
        self.assertEqual([], result["missing_packet"]["implementation_or_external_writes"])
        self.assertTrue(result["approved_packet"]["owner_and_approval_recorded"])
        self.assertTrue(result["approved_packet"]["requirements_and_non_goals_numbered"])
        self.assertTrue(result["approved_packet"]["per_atom_source_requirements_present"])
        self.assertTrue(result["approved_packet"]["per_atom_relevant_non_goals_present"])
        self.assertTrue(result["approved_packet"]["per_atom_change_control_disposition_present"])
        self.assertFalse(result["out_of_scope_surface"]["operator_tool_or_protocol_silently_added"])
        self.assertTrue(result["out_of_scope_surface"]["owner_approved_scope_revision_required"])
        self.assertEqual({"claude", "codex"}, set(result["provider_surfaces_traced"]))
        self.assertFalse(result["live_services_exercised"])
        self.assertTrue(result["limitations_disclosed"])


if __name__ == "__main__":
    unittest.main()
