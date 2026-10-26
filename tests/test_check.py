import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check", HERE.parent / "tools" / "check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def make_repo(tmp, name="skill-audit"):
    repo = Path(tmp)
    (repo / "skills" / name).mkdir(parents=True)
    (repo / "skills" / name / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Use when the user asks to audit a skill.\n---\n# {name}\n\nShort body.\n",
        encoding="utf-8")
    (repo / "README.md").write_text(f"{name}\n", encoding="utf-8")
    # audit script stub
    (repo / "skills" / name / "scripts").mkdir()
    (repo / "skills" / name / "scripts" / "audit.py").write_text(
        "import sys\nprint('ok')\nsys.exit(0)\n", encoding="utf-8")
    return repo


def fails_for(repo):
    return [str(f) for f in check.run_checks(repo)]


class RepoTests(unittest.TestCase):
    def test_good_repo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(fails_for(make_repo(tmp)), [])

    def test_name_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            f = repo / "skills" / "skill-audit" / "SKILL.md"
            f.write_text(f.read_text().replace("name: skill-audit", "name: other"), encoding="utf-8")
            self.assertTrue(any("[frontmatter]" in x for x in fails_for(repo)))

    def test_missing_readme_skill_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            (repo / "README.md").write_text("nothing here\n", encoding="utf-8")
            self.assertTrue(any("[readme]" in x for x in fails_for(repo)))

    def test_broken_link_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            f = repo / "skills" / "skill-audit" / "SKILL.md"
            f.write_text(f.read_text() + "\nSee [x](references/missing.md).\n", encoding="utf-8")
            self.assertTrue(any("[links]" in x for x in fails_for(repo)))


if __name__ == "__main__":
    unittest.main()