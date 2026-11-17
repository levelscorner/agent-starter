"""Tests for okf_index.py. Run: python3 scripts/okf_index_test.py"""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "okf_index.py"
spec = importlib.util.spec_from_file_location("okf_index", SCRIPT)
okf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(okf)


def doc(type_, title, desc, body="Body.\n", extra=""):
    return f"---\ntype: {type_}\ntitle: {title}\ndescription: \"{desc}\"\n{extra}---\n# {title}\n\n{body}"


class Repo:
    def __init__(self, files, config=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        if config is not None:
            (self.root / "okf.toml").write_text(textwrap.dedent(config))
        for rel, text in files.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)

    def read(self, rel):
        return (self.root / rel).read_text()

    def run(self, *args):
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def close(self):
        self.tmp.cleanup()


class WriteIndexes(unittest.TestCase):
    def setUp(self):
        self.repo = Repo({
            "docs/architecture.md": doc("Design Note", "Architecture", "The map of the packages."),
            "docs/errors.md": doc("Design Note", "Errors", "The error catalog: kinds and words."),
            "docs/old.md": doc("Design Note", "Old plan", "Replaced.", extra="status: deprecated\n"),
            "docs/learn/01-agent.md": doc("Teaching Note", "01 Agent", "Item 1 step by step."),
            "docs/learn/README.md": doc("Folder Guide", "Learn", "One teaching note per item."),
            "docs/.hidden/x.md": "no header\n",
            "docs/archive/y.md": "no header\n",
            "README.md": "# Not in the bundle\n",
        }, config='bundles = ["docs"]\nskip = ["docs/archive/**"]\n')

    def tearDown(self):
        self.repo.close()

    def test_root_index_groups_by_type_and_lists_folders(self):
        code, out = self.repo.run()
        self.assertEqual(code, 0, out)
        idx = self.repo.read("docs/index.md")
        self.assertTrue(idx.startswith('---\nokf_version: "0.2"\n---\n'), idx)
        self.assertIn("# Design Note\n\n* [Architecture](architecture.md) - The map of the packages.\n", idx)
        self.assertIn("* [Errors](errors.md) - The error catalog: kinds and words.\n", idx)
        self.assertIn("* [Old plan](old.md) - Replaced. (deprecated)\n", idx)
        self.assertIn("# Folders\n\n* [learn](learn/) - One teaching note per item.\n", idx)
        self.assertNotIn("archive", idx)
        self.assertNotIn(".hidden", idx)

    def test_sub_index_has_no_frontmatter(self):
        self.repo.run()
        sub = self.repo.read("docs/learn/index.md")
        self.assertFalse(sub.startswith("---"), sub)
        self.assertIn("* [01 Agent](01-agent.md) - Item 1 step by step.\n", sub)
        self.assertIn("* [Learn](README.md) - One teaching note per item.\n", sub)

    def test_files_outside_bundles_are_ignored(self):
        self.repo.run()
        self.assertFalse((self.repo.root / "index.md").exists())

    def test_check_passes_after_write_and_fails_when_a_description_changes(self):
        self.repo.run()
        code, out = self.repo.run("--check")
        self.assertEqual(code, 0, out)
        p = self.repo.root / "docs/errors.md"
        p.write_text(p.read_text().replace("The error catalog", "The catalog"))
        code, out = self.repo.run("--check")
        self.assertEqual(code, 1, out)
        self.assertIn("docs/index.md: out of date", out)

    def test_check_fails_when_an_index_is_missing(self):
        code, out = self.repo.run("--check")
        self.assertEqual(code, 1)
        self.assertIn("docs/learn/index.md: missing", out)

    def test_write_is_stable(self):
        self.repo.run()
        first = self.repo.read("docs/index.md")
        self.repo.run()
        self.assertEqual(first, self.repo.read("docs/index.md"))


class Headers(unittest.TestCase):
    def test_check_names_each_missing_field(self):
        repo = Repo({
            "docs/a.md": "# A\n\nNo header.\n",
            "docs/b.md": "---\ntitle: B\ndescription: x\n---\n",
            # the type nested under metadata: OKF needs it at the top level
            "docs/c.md": "---\nname: c\ndescription: x\nmetadata:\n  type: feedback\n---\n",
        })
        try:
            repo.run()
            code, out = repo.run("--check")
            self.assertEqual(code, 1)
            self.assertIn("docs/a.md: no header", out)
            self.assertIn("docs/b.md: header has no top-level `type`", out)
            self.assertIn("docs/c.md: header has no top-level `type`", out)
            self.assertIn("docs/c.md: header has no top-level `title`", out)
        finally:
            repo.close()

    def test_block_scalar_and_quoted_values_are_read(self):
        h = okf.read_header('---\ntype: Plan\ntitle: \'It\'\'s\'\ndescription: >\n  One line\n  and more.\n---\nx\n')
        self.assertEqual(h.fields["type"], "Plan")
        self.assertEqual(h.fields["title"], "It's")
        self.assertEqual(h.fields["description"], "One line and more.")

    def test_exempt_files_need_no_header(self):
        repo = Repo({"MEMORY.md": "- [a](a.md) - x\n",
                     "a.md": doc("Memory", "A", "x")},
                    config='bundles = ["."]\nexempt = ["MEMORY.md"]\n')
        try:
            repo.run()
            code, out = repo.run("--check")
            self.assertEqual(code, 0, out)
            self.assertNotIn("MEMORY", repo.read("index.md"))
        finally:
            repo.close()

    def test_also_read_under_reads_a_tool_owned_header(self):
        # Claude Code's memory writer moves extra keys under metadata:
        note = "---\nname: a\ndescription: x\nmetadata:\n  type: feedback\n  title: A note\n---\nBody.\n"
        repo = Repo({"m/a.md": note}, config='bundles = ["m"]\nalso_read_under = "metadata"\n')
        try:
            repo.run()
            code, out = repo.run("--check")
            self.assertEqual(code, 0, out)
            self.assertIn("# feedback\n\n* [A note](a.md) - x\n", repo.read("m/index.md"))
            repo.run("--add-headers")
            self.assertEqual(repo.read("m/a.md"), note)  # nothing added: the values are there
        finally:
            repo.close()

    def test_hand_written_index_is_kept_and_reported(self):
        repo = Repo({"docs/index.md": "# My own list\n", "docs/a.md": doc("Plan", "A", "x")})
        try:
            code, out = repo.run()
            self.assertEqual(repo.read("docs/index.md"), "# My own list\n")
            self.assertIn("docs/index.md: written by hand", out)
            code, out = repo.run("--check")
            self.assertEqual(code, 1)
        finally:
            repo.close()


class AddHeaders(unittest.TestCase):
    def test_fills_type_title_and_description(self):
        repo = Repo({
            "docs/adr/0001-split.md": "# ADR-0001: Split the repos\n\n**Status:** accepted\n\nWe split the app: front and back. More text here.\n",
            "docs/plain.md": "Just a [linked](x.md) line with `code`.\n",
            "docs/kept.md": "---\nname: kept\ndescription: Already here\n---\n# Kept\n",
        }, config='bundles = ["docs"]\n[types]\n"docs/adr" = "Decision"\n')
        try:
            code, out = repo.run("--add-headers")
            self.assertEqual(code, 0, out)
            adr = okf.read_header(repo.read("docs/adr/0001-split.md")).fields
            self.assertEqual(adr["type"], "Decision")
            self.assertEqual(adr["title"], "ADR-0001: Split the repos")
            # "**Status:** accepted" is a label line, not a summary, so it is skipped
            self.assertEqual(adr["description"], "We split the app: front and back.")
            plain = okf.read_header(repo.read("docs/plain.md")).fields
            self.assertEqual(plain["type"], "Document")
            self.assertEqual(plain["title"], "Plain")
            self.assertEqual(plain["description"], "Just a linked line with code.")
            kept_text = repo.read("docs/kept.md")
            kept = okf.read_header(kept_text).fields
            self.assertEqual(kept["description"], "Already here")
            self.assertEqual(kept["name"], "kept")
            self.assertEqual(kept["title"], "Kept")
            self.assertTrue(kept_text.rstrip().endswith("# Kept"))
            # running again changes nothing
            before = {p: repo.read(p) for p in ["docs/adr/0001-split.md", "docs/plain.md", "docs/kept.md"]}
            repo.run("--add-headers")
            self.assertEqual(before, {p: repo.read(p) for p in before})
            repo.run()
            code, out = repo.run("--check")
            self.assertEqual(code, 0, out)
        finally:
            repo.close()

    def test_description_skips_tables_code_and_comments(self):
        text = "# T\n\n<!-- note -->\n| a | b |\n|---|---|\n```\ncode\n```\n> Quoted reason here.\n"
        self.assertEqual(okf.guess_description(text), "Quoted reason here.")

    def test_label_lines_in_a_list_are_skipped(self):
        text = "# ADR-5: Keep a monolith\n\n- **Status:** accepted\n- **Date:** 2026-06-12\n\n## Context\n\nSplitting buys little. More.\n"
        self.assertEqual(okf.guess_description(text), "Splitting buys little.")

    def test_a_decision_or_summary_section_wins(self):
        text = "# ADR-5\n\n## Context\n\nLong story here.\n\n## Decision\n\nKeep one app. Why below.\n"
        self.assertEqual(okf.guess_description(text), "Keep one app.")
        text = "# Plan\n\nIntro line.\n\n## TL;DR\n\n- Ship it on Friday.\n"
        self.assertEqual(okf.guess_description(text), "Ship it on Friday.")

    def test_a_wrapped_paragraph_is_joined(self):
        text = "# T\n\nThe first sentence runs\nonto a second line. Then more.\n"
        self.assertEqual(okf.guess_description(text), "The first sentence runs onto a second line.")

    def test_long_description_is_cut_at_a_sentence(self):
        long = "# T\n\n" + "First sentence is here. " + "word " * 80 + "\n"
        self.assertEqual(okf.guess_description(long), "First sentence is here.")


if __name__ == "__main__":
    unittest.main()
