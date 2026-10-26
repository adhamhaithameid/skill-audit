---
name: skill-improve-plan
description: Use when the user asks how to improve a skill, what to fix first, or for a step-by-step plan after an audit. Runs the audit itself and returns a ranked plan with replacement text and the points each fix earns. Not for grading alone, editing the skill, or writing a new skill.
---

# Skill improve plan

Turn an audit into an ordered plan the author can execute in one sitting.

## Run

1. Find the skill folder. Ask for the path only when none is in the conversation. Done when you can name the folder.
2. Reuse a pasted audit only when the skill's files have not changed since that audit. Otherwise run `python3 scripts/audit.py <folder> --json`. Done when you have current scores.
3. Run `python3 scripts/audit.py <folder> --profile` for the file tree, headings, and token estimate. Done when the profile JSON is in hand.
4. Ask one question: "Ship publicly or internal use?" Public weights Trigger and Portability higher. Done when the answer is recorded.
5. Build the plan. Rank each failing check by weight times gap divided by effort. Three tiers: today (under an hour), this week, later. Done when every failing check sits in a tier.
6. Write the plan with one item per check: check number and title, the current line quoted, the replacement text, effort (S, M, or L), points gained, and a command to verify. Done when each item has all six fields.
7. Offer to apply tier 1 after the user agrees. This skill never edits the skill on its own. Done when the offer is made or declined.

## Effort guide

- S: one line or one file edit, under 15 minutes.
- M: several files or a small script, under an hour.
- L: new tests, a port, or a host run, over an hour.

## Public vs internal

Public: double the weight of Trigger and Portability checks when ranking. Internal: use the rubric weights as printed.

## Thin input and conflicts

This skill is read-only: it writes the plan only. It matches the user's repo convention and requested format.

- No SKILL.md: say what is missing, ask for the path once, do not plan.
- A pasted audit that names a different folder or an older grade: re-run the audit.
- Precedence: the files first, then the audit output, then the rubric, then your taste.

## Files

- `scripts/audit.py`: the engine. Run it in steps 2 and 3.