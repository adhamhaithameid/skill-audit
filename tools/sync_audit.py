#!/usr/bin/env python3
"""Copy the canonical audit.py into every skill that bundles it.

Run: python3 tools/sync_audit.py
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "skills" / "skill-audit" / "scripts" / "audit.py"
TARGETS = [
    ROOT / "skills" / "skill-improve-plan" / "scripts" / "audit.py",
    ROOT / "skills" / "skill-report" / "scripts" / "audit.py",
]

def main():
    if not CANONICAL.exists():
        raise SystemExit(f"canonical not found: {CANONICAL}")
    for t in TARGETS:
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(CANONICAL, t)
        print(f"synced {t.relative_to(ROOT)}")

if __name__ == "__main__":
    main()