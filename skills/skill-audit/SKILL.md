---
name: skill-audit
description: Use when the user asks to audit, review, grade, score, or lint an existing skill (a SKILL.md and its folder), or asks whether a skill is well built, portable, or likely to trigger. Not for writing a new skill from scratch, not for running a skill's own task, and not for planning fixes (use skill-improve-plan).
---

# Skill audit

Score one skill against 24 checks in five pillars: Trigger, Content, Reliability, Portability, Proof. Return a report the author can act on in one sitting.

## Run

1. Find the skill folder, the directory that holds SKILL.md. Ask for the path only when no folder is in the conversation or the workspace. Done when you can name the folder.
2. Run `python3 scripts/audit.py <folder> --json`. Add `--brief` when only the grade and top fixes are needed. Done when the output lists all 24 checks.
3. Read the audited SKILL.md and every file under its `references/`. Done when you can quote the line behind each finding.
4. Open `references/rubric.md`. Score the four judge checks (4, 5, 22, 24) with 0, 1, or 2. Check every `heuristic` result against your reading and correct a wrong one. Done when every check has a score or an n/a.
5. Run the script again with `--override '{"4":2,"5":1,"22":0,"24":0}'`, using your scores. Done when the SCORE line has no PROVISIONAL tag.
6. Write the report with `assets/report-template.md`. Done when each check below 2 has a fix that quotes the current line and gives the replacement text.

## Scoring

Each check scores 0 (fails), 1 (partial), or 2 (passes). The script weights the checks and prints a percent and a grade.

| Grade | Percent | Meaning |
|---|---|---|
| A | 90 and above | Ship it. |
| B | 80 to 89 | Solid. Fix the top three. |
| C | 65 to 79 | Usable with real gaps. |
| D | 50 to 64 | Rework the weak pillars. |
| F | below 50 | Rebuild from the trigger up. |

An installed skill usually has no `evals/` folder, because packaging drops it. The Proof pillar then reads low by design. Say so, and score the pillar from the source repository when the user can supply it.

## Report rules

- Lead with the grade, the pillar percents, and the three fixes of highest weight times gap.
- Credit what works in one line per pillar. Authors keep what they know is good.
- Write the fix as text: the current line, then the replacement line. Advice such as "tighten the description" does not count.
- Use the user's language and the user's requested format for the report. Match the author's level, and name each check by its number and its title.
- Judge a rule that clashes with the author's house style by its effect, and say which style it follows.
- This skill reads and reports. It never edits the audited skill unless the user asks for the edit.

Example fix for check 1:

> Current: `description: Helps with files. First read the file, then summarize it.`
> Replacement: `description: Use when the user asks to summarize a file or a folder of notes. Not for editing the file.`

## Thin input and conflicts

- No SKILL.md in the folder, an empty file, or no frontmatter: say what is missing, ask for the path once, and do not score.
- A pillar lacks evidence, for example Proof on an installed skill: score what exists, mark the pillar not assessed, and say what would unlock it.
- Assume nothing about host testing. A claim with no recorded run scores 0 on check 24.
- Precedence when sources disagree: the files first, then the script output, then the rubric text, then your taste.

## Judgment calls

- A skill passes check 1 with a "what it does" clause, when the clause names triggers and does not list steps. Pushy trigger wording passes.
- A skill with no scripts passes check 11 when its work is judgment work. The script marks this n/a.
- A skill with no side effects still states that in one line for check 15.
- Treat a heuristic hit as a lead. Quote the line before you score it 2.
- Two readings of the request are possible, for example "audit the repo" with eight skills: audit each skill, then add one summary table.

## Files

- `scripts/audit.py`: runs the mechanical checks and computes the score. Standard library only. Run it in step 2 and step 5.
- `references/rubric.md`: what 0, 1, and 2 mean for each of the 24 checks, and how the script tests it. Open it in step 4.
- `assets/report-template.md`: the report layout. Copy it in step 6.
