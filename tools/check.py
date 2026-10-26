#!/usr/bin/env python3
"""Tier 1 checks for the skill-audit repo. Standard library only.

Run:  python3 tools/check.py
Exit code 0 means all checks pass. Exit code 1 means at least one check failed.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

class Failure:
    def __init__(self, check, path, line, message):
        self.check, self.path, self.line, self.message = check, path, line, message
    def __str__(self):
        where = f"{self.path}:{self.line}" if self.line else f"{self.path}"
        return f"FAIL [{self.check}] {where} {self.message}"

def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None

def skill_dirs(repo):
    root = repo / "skills"
    if not root.is_dir():
        return []
    return sorted(d for d in root.iterdir() if d.is_dir())

def parse_frontmatter(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, "file does not start with ---"
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "frontmatter is not closed"
    data, key = {}, None
    for raw in lines[1:end]:
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            data[key] = "" if val in (">", "|", ">-", "|-") else val
        elif key and raw.startswith((" ", "\t")):
            data[key] = (data[key] + " " + raw.strip()).strip()
    return data, None

def check_structure(repo, fails):
    if not skill_dirs(repo):
        fails.append(Failure("structure", "skills/", 0, "no skill folders found"))
    for d in skill_dirs(repo):
        if not (d / "SKILL.md").exists():
            fails.append(Failure("structure", d.relative_to(repo), 0, "SKILL.md is missing"))
    # No nested SKILL.md: a stray one ships as a decoy skill.
    for f in repo.rglob("SKILL.md"):
        rel = f.relative_to(repo)
        if len(rel.parts) != 3 or rel.parts[0] != "skills" or rel.parts[2] != "SKILL.md":
            fails.append(Failure("structure", rel, 0, "nested SKILL.md would ship as a decoy skill"))

def check_frontmatter(repo, fails):
    for d in skill_dirs(repo):
        f = d / "SKILL.md"
        if not f.exists():
            continue
        data, err = parse_frontmatter(read_text(f) or "")
        rel = f.relative_to(repo)
        if err:
            fails.append(Failure("frontmatter", rel, 1, err))
            continue
        if data.get("name") != d.name:
            fails.append(Failure("frontmatter", rel, 2, f"name '{data.get('name')}' must equal folder '{d.name}'"))
        if not data.get("description"):
            fails.append(Failure("frontmatter", rel, 0, "description is empty"))

def check_links(repo, fails):
    for d in skill_dirs(repo):
        for f in d.rglob("*.md"):
            text = read_text(f)
            if text is None:
                continue
            in_fence = False
            for n, line in enumerate(text.split("\n"), 1):
                if line.strip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                targets = re.findall(r"\]\(([^)\s]+)\)", line)
                targets += re.findall(r"`((?:references|scripts|assets)/[\w./-]+)`", line)
                for t in targets:
                    if re.match(r"^(https?:|mailto:|#)", t):
                        continue
                    t = t.split("#")[0]
                    if not t:
                        continue
                    base = d if t.startswith(("references/", "scripts/", "assets/")) and f.name == "SKILL.md" else f.parent
                    if not (base / t).exists() and not (d / t).exists():
                        fails.append(Failure("links", f.relative_to(repo), n, f"target does not exist: {t}"))

def check_size(repo, fails):
    for d in skill_dirs(repo):
        f = d / "SKILL.md"
        if not f.exists():
            continue
        count = len((read_text(f) or "").split("\n"))
        if count > 500:
            fails.append(Failure("size", f.relative_to(repo), 0, f"{count} lines; the limit is 500"))

def check_readme(repo, fails):
    readme = repo / "README.md"
    if not readme.exists():
        fails.append(Failure("readme", "README.md", 0, "file is missing"))
        return
    text = read_text(readme) or ""
    for d in skill_dirs(repo):
        if d.name not in text:
            fails.append(Failure("readme", "README.md", 0, f"skill not listed: {d.name}"))

def check_audit_smoke(repo, fails):
    canonical = repo / "skills" / "skill-audit" / "scripts" / "audit.py"
    # synced copies must match the canonical engine
    for target in ("skill-improve-plan", "skill-report"):
        copy = repo / "skills" / target / "scripts" / "audit.py"
        if copy.exists() and canonical.exists() and copy.read_bytes() != canonical.read_bytes():
            fails.append(Failure("audit-sync", copy.relative_to(repo), 0,
                                 "differs from canonical audit.py; run tools/sync_audit.py"))
    # run the skill's own audit script as a smoke test
    for d in skill_dirs(repo):
        script = d / "scripts" / "audit.py"
        if not script.exists():
            continue
        try:
            r = subprocess.run([sys.executable, str(script), str(d)], capture_output=True, text=True, timeout=60)
        except Exception as e:
            fails.append(Failure("audit", str(d.relative_to(repo)), 0, f"audit script failed to run: {e}"))
            continue
        if r.returncode != 0:
            fails.append(Failure("audit", str(d.relative_to(repo)), 0, f"audit script exited {r.returncode}: {r.stderr.strip()[:200]}"))

def run_checks(repo):
    repo = Path(repo)
    fails = []
    check_structure(repo, fails)
    check_frontmatter(repo, fails)
    check_links(repo, fails)
    check_size(repo, fails)
    check_readme(repo, fails)
    check_audit_smoke(repo, fails)
    return fails

def main(argv):
    repo = Path(__file__).resolve().parent.parent
    fails = run_checks(repo)
    for f in fails:
        print(f)
    print(f"\n{len(fails)} failure(s)." if fails else "All checks passed.")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
