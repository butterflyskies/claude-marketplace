from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
EXPECTED = {
    "briefing",
    "design",
    "develop",
    "elbow-grease",
    "keep-the-wheel-turning",
    "land",
    "load-design-principles",
    "multimodel-elbow-grease",
    "review-fix-loop",
    "scope-sharpen",
    "skill-forge",
    "token-audit",
}


def skill_text(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


class SkillPackageContractTests(unittest.TestCase):
    def test_plugin_and_marketplace_topology_resolve(self) -> None:
        plugin = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual("bsky-core", plugin["name"])
        self.assertEqual("./skills/", plugin["skills"])

        marketplace_path = ROOT.parents[1] / ".agents" / "plugins" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text())
        entries = [entry for entry in marketplace["plugins"] if entry["name"] == "bsky-core"]
        self.assertEqual(1, len(entries))
        source = entries[0]["source"]
        self.assertEqual("local", source["source"])
        resolved = (marketplace_path.parent.parent.parent / source["path"]).resolve()
        self.assertEqual(ROOT, resolved)

    def test_hash_bound_callisto_handoff_is_preserved(self) -> None:
        expected = {
            ROOT / "tests" / "fixtures" / "six-lens-acceptance.md":
                "0752315368c8562dcd78ff60b41da45bb5911b8156b216a5ef729bddb69e58c9",
            SKILLS / "multimodel-elbow-grease" / "SKILL.md":
                "cf906797dfed6a1b06df184f2e3d9adb139b5296473a83c631494638674c0ab8",
            SKILLS / "review-fix-loop" / "SKILL.md":
                "b0bbdb5357f2fd133a056beadbfd332f328aa8cec5fe2916384af508b7954e4f",
        }
        for path, digest in expected.items():
            with self.subTest(file=str(path)):
                self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_expected_skill_set_is_present(self) -> None:
        present = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
        self.assertEqual(EXPECTED, present)

    def test_frontmatter_is_codex_minimal(self) -> None:
        for name in EXPECTED:
            with self.subTest(skill=name):
                text = skill_text(name)
                self.assertTrue(text.startswith("---\n"))
                frontmatter = text.split("---\n", 2)[1]
                keys = {
                    line.split(":", 1)[0].strip()
                    for line in frontmatter.splitlines()
                    if ":" in line
                }
                self.assertEqual({"name", "description"}, keys)

    def test_openai_prompts_explicitly_invoke_the_skill(self) -> None:
        for name in EXPECTED:
            with self.subTest(skill=name):
                yaml = (SKILLS / name / "agents" / "openai.yaml").read_text(
                    encoding="utf-8"
                )
                self.assertIn(f"${name}", yaml)

    def test_relative_markdown_links_resolve(self) -> None:
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for markdown in SKILLS.rglob("*.md"):
            for target in link_pattern.findall(markdown.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#")):
                    continue
                path = (markdown.parent / target.split("#", 1)[0]).resolve()
                with self.subTest(file=str(markdown), target=target):
                    self.assertTrue(path.exists(), f"missing linked resource: {path}")

    def test_internal_skill_invocations_resolve(self) -> None:
        invocation_pattern = re.compile(r"\$([a-z0-9][a-z0-9:-]*)")
        for markdown in SKILLS.rglob("*.md"):
            for invocation in invocation_pattern.findall(
                markdown.read_text(encoding="utf-8")
            ):
                if invocation == "skill-name":
                    continue
                name = invocation.split(":", 1)[-1]
                with self.subTest(file=str(markdown), invocation=invocation):
                    self.assertIn(name, EXPECTED)

    def test_no_claude_only_runtime_contracts_leak_into_candidates(self) -> None:
        forbidden = (
            ".claude/",
            "~/.claude",
            "CLAUDE.md",
            "claude-opus",
            "claude-sonnet",
            "TeamCreate",
            "TaskCreate",
        )
        for path in SKILLS.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                with self.subTest(file=str(path), token=token):
                    self.assertNotIn(token, text)

    def test_design_surfaces_topology_and_cost_alternatives(self) -> None:
        text = skill_text("design")
        self.assertIn("meaningful architecture or topology level", text)
        self.assertIn("materially cheaper viable alternative", text)
        self.assertIn("operating cost", text)
        self.assertIn("reversibility", text)

    def test_develop_reference_contract_is_complete(self) -> None:
        expected = {
            "implementation-guide.md",
            "migration-checklist.md",
            "quality-checklist.md",
            "repo-setup.md",
            "review-dimensions.md",
            "rust.md",
        }
        refs = SKILLS / "develop" / "references"
        self.assertEqual(expected, {path.name for path in refs.glob("*.md")})
        self.assertIn("Do not let a reference expand the user's authority", skill_text("develop"))

    def test_elbow_grease_is_exactly_six_lens_and_review_only(self) -> None:
        text = skill_text("elbow-grease")
        lenses = (SKILLS / "elbow-grease" / "references" / "lenses.md").read_text(
            encoding="utf-8"
        )
        expected = {"Safety", "Design", "Security", "Privacy", "Idiomacy", "Tests"}
        headings = set(re.findall(r"^## ([A-Za-z]+)$", lenses, flags=re.MULTILINE))
        self.assertEqual(expected, headings)
        self.assertIn("review-only", text)
        self.assertIn("unless the user separately authorizes fixes", text)

    def test_wheel_has_single_nudge_and_external_effect_boundaries(self) -> None:
        text = skill_text("keep-the-wheel-turning")
        self.assertIn("A crank advances at most one item", text)
        self.assertIn("atomically claim the exact item and step", text)
        self.assertIn("Never merge or deploy", text)
        self.assertIn("standing authorization matrix", text)

    def test_briefing_is_observational_and_fail_honest(self) -> None:
        text = skill_text("briefing")
        self.assertIn("Ordinary briefing is read-only", text)
        self.assertIn("Label unavailable sections `unchecked`, not `none`", text)
        self.assertIn("never mark, dismiss", text)
        self.assertIn("stored follow-up is context, not authority", text)

    def test_land_has_effect_specific_authority_and_truthful_receipts(self) -> None:
        text = skill_text("land")
        self.assertIn("Start with a read-only inventory", text)
        self.assertIn("Treat push as a separate external effect", text)
        self.assertIn("Never merge", text)
        self.assertIn("Never describe an unpushed commit as published", text)

    def test_scope_sharpen_preserves_scope_and_does_not_implement(self) -> None:
        text = skill_text("scope-sharpen")
        self.assertIn("This is a scoping workflow, not implementation", text)
        self.assertIn("Load `$bsky-core:load-design-principles`", text)
        self.assertIn("Coverage: map every source requirement", text)
        self.assertIn("Writing the artifact does not authorize", text)

    def test_skill_forge_preserves_install_and_publication_gates(self) -> None:
        text = skill_text("skill-forge")
        self.assertIn("system `skill-creator`", text)
        self.assertIn("workspace's approved publishing workflow", text)
        self.assertIn("requires explicit activation/install authorization", text)
        self.assertIn("Publication is a separate state-changing action", text)

    def test_review_family_preserves_contract_and_authority_boundaries(self) -> None:
        multimodel = skill_text("multimodel-elbow-grease")
        loop = skill_text("review-fix-loop")
        for text in (multimodel, loop):
            self.assertIn("Privacy", text)
            self.assertIn("Security", text)
            self.assertIn("Never", text)
        self.assertIn("Consensus affects confidence, not severity", multimodel)
        self.assertIn("INCOMPATIBLE_GENERIC", multimodel)
        self.assertIn("CONVERGED", loop)
        self.assertIn("never infer publication or commit authority", loop)


if __name__ == "__main__":
    unittest.main()
