from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "tests" / "behavioral" / "syne-five-skill-receipts-20260806.json"
REVIEW_PATH = ROOT / "tests" / "behavioral" / "six-lens-review-20260806.json"
SOURCE_REVISION = "d29910dc302e8b7008df4b9fdc291a9cc9cad115"
EXPECTED_SKILLS = {
    "design",
    "develop",
    "keep-the-wheel-turning",
    "token-audit",
    "skill-forge",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BehavioralReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        cls.cases = {case["skill"]: case for case in cls.receipt["cases"]}

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


if __name__ == "__main__":
    unittest.main()
