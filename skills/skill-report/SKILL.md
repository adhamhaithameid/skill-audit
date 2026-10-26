---
name: skill-report
description: Use when the user asks for a report, profile, or documentation page about a skill: its goal, usage, structure, checks, and grade. Matches the user's writing style and glossary. Not for scoring alone, improvement plans, or writing the skill.
---

# Skill report

Write a profile of one skill for reviewers and teammates.

## Run

1. Find the skill folder. Ask for the path only when none is in the conversation. Done when you can name the folder.
2. Run `python3 scripts/audit.py <folder> --json` and `python3 scripts/audit.py <folder> --profile`. Done when both outputs are in hand.
3. Read the skill in this order: frontmatter, SKILL.md, reference headings, script docstrings, evals, changelog. If the host can hand work to a separate agent, give it the profile JSON and the folder and ask for a structured summary where every claim cites a file. Done when the reading is complete.
4. Find the user's voice: the conversation first, then STYLE.md, GLOSSARY.md, CONTRIBUTING.md, README tone, and AGENTS.md or CLAUDE.md. If nothing is found, use plain style and say so. Glossary terms are used verbatim. Done when the voice is chosen.
5. Pick the output: a doc tool if the host has one, else a markdown file in the current folder, else chat. The user can override. Done when the destination is set.
6. Write the report from the layout below. Mark anything unknown, such as hosts tested, under "Not assessed". Never invent a fact. Done when every section is filled or marked not assessed.

## Report layout

- Title block: name, version, owner, date, grade badge, one-line summary.
- At a glance: goal, audience, top five triggers, "not for", hosts tested, size and tokens, five pillar scores.
- How to use: install command, three example prompts, what happens, sample output, runtime needed.
- How it's built: file tree with one line per file, when each reference loads.
- Checks and grade: all 24 checks with score and evidence; strengths; gaps.
- Proof: eval and trigger-test counts, host log, changelog highlights, known limits.
- Risks: files written, network, permissions.
- Glossary: terms used, in the user's wording.
- Appendix: audit excerpt, files read, generation date.

## Thin input and conflicts

This skill is read-only: it writes the report only. It matches the user's repo convention and requested format.

- No SKILL.md: say what is missing, ask for the path once, do not report.
- A pillar lacks evidence: score what exists, mark it not assessed, say what would unlock it.
- Precedence: the files first, then the audit output, then the profile, then your taste.

## Files

- `scripts/audit.py`: the engine. Run it in step 2.