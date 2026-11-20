#!/usr/bin/env python3
"""Tests for build_skill_index.py and select_skills.py. Run: python3 tools/select_skills_test.py"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_skill_index as bsi  # noqa: E402
import select_skills as sel  # noqa: E402


def entry(name, source="library", status="library", cat=1, desc="", area="", conf="high", risk_class=None, path=None):
    return {"name": name, "source": source, "kind": "skill", "category": cat, "area": area,
            "description": desc, "status": status, "risk": "pushes on its own" if risk_class else None,
            "risk_class": risk_class, "confidence": conf, "path": path, "load": f"{name}/SKILL.md"}


CATALOG = [
    entry("postgres-migrations", desc="Forward-only Postgres schema migrations and backfills", area="backend/database"),
    entry("pr-review", source="house", status="house", desc="Review a pull request before merge", area="process"),
    entry("pr-review", source="claude-skills", status="other", desc="Review a pull request before merge", area="process"),
    entry("ship", source="claude-skills", status="other", desc="Commit, push and merge a pull request", area="process",
          risk_class="quarantine"),
    entry("motion-rules", cat=5, desc="UI animation timing and easing for screens", area="ui"),
    entry("social-posts", cat=3, desc="Draft social media posts for a launch campaign", area="marketing"),
    entry("invoice-chase", cat=6, conf="low", desc="Draft overdue invoice payment reminder emails for billing"),
]


def build(catalog=CATALOG):
    return [bsi.build_record(e, None) for e in catalog]


class FilterTest(unittest.TestCase):
    def test_finds_the_matching_skill_first(self):
        got = sel.pass1(build(), "add a postgres migration")
        self.assertEqual(got[0]["name"], "postgres-migrations")

    def test_quarantined_left_out_unless_reference(self):
        names = [r["name"] for r in sel.pass1(build(), "merge and push the pull request")]
        self.assertNotIn("ship", names)
        names = [r["name"] for r in sel.pass1(build(), "merge and push the pull request", include_reference=True)]
        self.assertIn("ship", names)

    def test_category_filter(self):
        got = sel.pass1(build(), "draft posts and reminder emails", category=3)
        self.assertEqual([r["name"] for r in got], ["social-posts"])

    def test_limit_caps_candidates(self):
        many = [entry(f"db-skill-{i}", desc="database work") for i in range(40)]
        self.assertEqual(len(sel.pass1(build(many), "database", limit=25)), 25)


class PrecedenceTest(unittest.TestCase):
    def test_house_copy_wins_a_tie(self):
        got = sel.pass1(build(), "review the pull request")
        top = [r for r in got if r["name"] == "pr-review"]
        self.assertEqual(len(top), 1, "one entry per skill name")
        self.assertEqual(top[0]["source"], "house")
        self.assertEqual(top[0]["precedence"], 2)

    def test_quarantine_sets_reference_rank(self):
        ship = [r for r in build() if r["name"] == "ship"][0]
        self.assertEqual((ship["status"], ship["precedence"]), ("quarantined", 5))


class RankingFallbackTest(unittest.TestCase):
    def test_bm25_puts_best_match_first(self):
        recs = build()
        cands = sel.pass1(recs, "ui animation easing on the screen")
        ranked = sel.bm25(cands, "ui animation easing on the screen", recs)
        self.assertEqual(ranked[0]["name"], "motion-rules")

    def test_prompt_has_names_and_descriptions_only(self):
        cands = sel.pass1(build(), "review the pull request")
        prompt = sel.ranking_prompt("review the pull request", cands, 3)
        self.assertIn("pr-review (p2): Review a pull request", prompt)
        self.assertNotIn("SKILL.md", prompt)


class SweepTest(unittest.TestCase):
    def test_flags_unmapped_finance_skill(self):
        rows = sel.sweep(build())
        hit = [r for r in rows if r["name"] == "invoice-chase"]
        self.assertTrue(hit)
        self.assertEqual(hit[0]["suggested"], 2)

    def test_leaves_confident_records_alone(self):
        self.assertNotIn("postgres-migrations", [r["name"] for r in sel.sweep(build())])


class RefreshTest(unittest.TestCase):
    def test_only_changed_records_are_rebuilt(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "a.md"
            f.write_text("one")
            cat = [entry("a", path=str(f)), entry("b")]
            out = Path(d) / "index.json"
            recs, added, changed, removed = bsi.refresh(cat, out)
            bsi.write_index(out, recs)
            self.assertEqual(len(added), 2)
            _, added, changed, removed = bsi.refresh(cat, out)
            self.assertEqual((added, changed, removed), ([], [], []))
            f.write_text("two")
            _, added, changed, removed = bsi.refresh(cat, out)
            self.assertEqual(changed, ["library:skill:a"])
            _, _, _, removed = bsi.refresh(cat[:1], out)
            self.assertEqual(removed, ["library:skill:b"])

    def test_refuses_private_paths(self):
        with self.assertRaises(SystemExit):
            bsi.build_record(entry("x", desc="see " + "/" + "home/someone/notes"), None)

    def test_index_file_parses(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "index.json"
            bsi.write_index(out, build())
            self.assertEqual(json.loads(out.read_text())["count"], len(CATALOG))


if __name__ == "__main__":
    unittest.main(verbosity=1)
