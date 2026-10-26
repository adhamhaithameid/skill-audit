# skill-audit

A skill that audits other skills. It scores a skill folder against 24 checks in five pillars: Trigger, Content, Reliability, Portability, Proof. It returns a graded report the author can act on in one sitting.

## Use

Point the skill at a skill folder. It runs `scripts/audit.py`, reads the audited files, scores the judge checks, and writes a report from `assets/report-template.md`.

```text
Audit the skill in ./my-skill and tell me what to fix first.
```

## Checks

The checks live in `references/rubric.md`. Weights and scoring logic live in `scripts/audit.py`. Total weight is 35, maximum score is 70. Percent = sum / 70 * 100.

Grades: A is 90 and above, B is 80 to 89, C is 65 to 79, D is 50 to 64, F is below 50.

## CLI

```text
npx skill-audit ./my-skill
python3 skills/skill-audit/scripts/audit.py ./my-skill --brief
```

## Repo checks

Run from the repo root:

```text
python3 tools/check.py
python3 -m unittest discover -s tests
```

## Layout

- `skills/skill-audit/`: the skill.
- `tools/`: repo-level checks.
- `tests/`: unit tests for the checks.
- `.github/workflows/`: CI.

## License

MIT.