# Changelog

## 0.1.1

- Python 3.9 compatibility: stdlib module set is now a real fallback, not empty.
- Refuse bad input: empty file, missing frontmatter, non-UTF-8 text, and invalid override keys or scores now exit 2.
- Added --brief mode and an npm bin wrapper with a Python-missing message.
- Removed the decoy SKILL.md from evals/fixtures; fixture renamed to fixture.md.
- Description no longer claims "improve"; improvement planning belongs to skill-improve-plan.

## 0.1.0

- First release. 24 checks in five pillars. The script scores 20 checks by file reading and keyword tests. The agent scores 4 judge checks and verifies the heuristic ones.
- Rubric derived from the write-skills repository evals: process rules separate a skill from the base model, format rules do not. Pruning note: checks 4, 6, 9, 12, 16, 17, and 21 carry the weight, based on those evals.
- Host testing: not yet recorded.
