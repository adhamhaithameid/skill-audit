import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent / "skills" / "skill-audit" / "scripts" / "audit.py"
spec = importlib.util.spec_from_file_location("audit", AUDIT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def make_skill(tmp, body="---\nname: demo\ndescription: Use when the user asks to audit a skill folder.\n---\n# demo\n\n1. Do the thing. Done when it passes.\n"):
    root = Path(tmp)
    (root / "SKILL.md").write_text(body, encoding="utf-8")
    return root


class ParseTests(unittest.TestCase):
    def test_valid_frontmatter(self):
        fm, body = audit.parse_frontmatter("---\nname: a\ndescription: b\n---\nbody\n")
        self.assertEqual(fm, {"name": "a", "description": "b"})
        self.assertEqual(body.strip(), "body")

    def test_missing_frontmatter(self):
        fm, body = audit.parse_frontmatter("no frontmatter")
        self.assertIsNone(fm)

    def test_bom_stripped(self):
        # run() uses utf-8-sig; parse_frontmatter on raw with BOM would fail, so test run()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SKILL.md").write_text("\ufeff---\nname: demo\ndescription: Use when auditing.\n---\nbody\n", encoding="utf-8")
            data = audit.run(Path(tmp))
            self.assertEqual(data["skill"], "demo")


class InputTests(unittest.TestCase):
    def test_empty_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SKILL.md").write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                audit.run(Path(tmp))

    def test_non_utf8_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SKILL.md").write_bytes(b"\xff\xfe not utf8")
            with self.assertRaises((ValueError, UnicodeDecodeError)):
                audit.run(Path(tmp))

    def test_missing_skill_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                audit.run(Path(tmp))


class EvalsTests(unittest.TestCase):
    def test_load_evals_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            cases, err = audit.load_evals(Path(tmp))
            self.assertEqual(cases, [])

    def test_trigger_cases_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "t.json").write_text(json.dumps([
                {"should_trigger": True},
                {"should_trigger": False},
                {"should_trigger": True},
            ]), encoding="utf-8")
            pos, neg = audit.trigger_cases(root)
            self.assertEqual((pos, neg), (2, 1))


class RunTests(unittest.TestCase):
    def test_run_scores_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_skill(tmp)
            data = audit.run(root)
            self.assertIn("res", data)
            self.assertIn("skill", data)

    def test_finish_no_provisional_with_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_skill(tmp)
            data = audit.finish(audit.run(root), {"4": 2, "5": 2, "22": 0, "24": 0})
            self.assertFalse(data["total"]["provisional"])


class CliTests(unittest.TestCase):
    def test_main_missing_skill_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, str(AUDIT), tmp], capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)

    def test_main_empty_file_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SKILL.md").write_text("", encoding="utf-8")
            r = subprocess.run([sys.executable, str(AUDIT), tmp], capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)

    def test_main_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp)
            r = subprocess.run([sys.executable, str(AUDIT), tmp, "--brief"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            self.assertIn("GRADE", r.stdout)

    def test_main_bad_override_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp)
            r = subprocess.run([sys.executable, str(AUDIT), tmp, "--override", "{bad"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)

    def test_main_bom_parses(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SKILL.md").write_text("\ufeff---\nname: demo\ndescription: Use when auditing.\n---\nbody\n", encoding="utf-8")
            r = subprocess.run([sys.executable, str(AUDIT), tmp], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()