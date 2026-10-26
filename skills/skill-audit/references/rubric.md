# Rubric

Contents: Trigger (1-3), Content (4-10), Reliability (11-15), Portability (16-19), Proof (20-24).

Kinds: `auto` is tested by the script and is reliable. `heuristic` is a keyword test. Read the file and correct it. `judge` is scored by you from the files.

Weights live in `scripts/audit.py`. The JSON output shows them.

## Trigger

| # | Check | 2 | 1 | 0 |
|---|---|---|---|---|
| 1 | Description states triggers, not steps (heuristic) | Names the user phrases and contexts. The key word comes first. No step list. 60 to 1024 chars. | One flaw: thin, long, or one step narrated. | No trigger wording, or the description lists the workflow. |
| 2 | Name is valid and specific (auto) | Kebab-case, 64 chars or fewer, matches the folder, names the job. | Mismatch with the folder, or a generic name. | Invalid characters or missing. |
| 3 | Scope boundary is stated (heuristic) | The description says what the skill does not cover. | Only the body says it. | Nowhere. |

## Content

| # | Check | 2 | 1 | 0 |
|---|---|---|---|---|
| 4 | Teaches only what the model would not do by default (judge) | Every rule carries process, a trap, or a convention the model cannot guess. | A few lines restate default behavior. | Mostly generic advice. Delete test: removing a rule changes nothing. |
| 5 | Opens with the job, then ordered steps (judge) | The first section states the outcome. Numbered steps follow in run order. | Steps exist but background comes first. | No ordered path. |
| 6 | Steps end on checkable completion criteria (heuristic) | At least half the steps say how to tell done from not done. | One in five or more. | Steps name actions only. |
| 7 | Positive phrasing, reasons over shouting (heuristic) | Under 15% of prose lines are prohibitions. Two or fewer shouted words. | Under 30% and five or fewer shouted words. | Mostly prohibitions or capital-letter orders. |
| 8 | One clear example (heuristic) | One or two examples. | None, or three to four. | Five or more. |
| 9 | Short main file, detail behind pointers (auto) | Body of 100 lines or fewer. Every pointer resolves. Every reference is pointed to. | Up to 500 lines, or one pointer flaw. | Over 500 lines, or several pointer flaws. |
| 10 | One source of truth per fact (auto) | No prose line of 8 or more words repeats across files. | One to three repeats. | More than three. |

A pointer states what the material is and the case that opens it. Check the wording: a pointer with no "when" is a weak pointer.

## Reliability

| # | Check | 2 | 1 | 0 |
|---|---|---|---|---|
| 11 | Deterministic work lives in scripts (auto) | Scripts use the standard library, carry a usage docstring, and SKILL.md names them. | Scripts exist with one flaw. Or prose describes work that a script should do. | Several flaws. n/a when the skill does judgment work only. |
| 12 | Handles thin or missing input (heuristic) | Says what to do when facts are absent: ask, or mark assumptions. | Mentions it once. | Silent. The skill will invent. |
| 13 | Precedence for conflicts is defined (heuristic) | States an order, for example safety, accuracy, user request, style. | One mention. | Silent. |
| 14 | User context wins over skill defaults (heuristic) | Repo convention, user language, and requested format override the defaults. | One of them. | The skill forces its own style. |
| 15 | States what the skill never does (heuristic) | Names its side-effect limits, for example "writes text only". | n/a | Silent on side effects. |

## Portability

| # | Check | 2 | 1 | 0 |
|---|---|---|---|---|
| 16 | Portable frontmatter core (auto) | Only `name`, `description`, and spec keys (`license`, `compatibility`, `metadata`, `allowed-tools`). | One harness-specific or unknown key. | Two or more. |
| 17 | Names capabilities, not harness tools (heuristic) | "Read the file", "search the web". A fallback when a capability is missing. | One or two tool names. | Three or more. |
| 18 | Relative paths, no installs or network (auto) | No absolute paths, installs, downloads, or network imports. | One or two. | Three or more. |
| 19 | Works standalone (auto) | No reference to another skill. No link that leaves the folder. | One. | Two or more. |

## Proof

| # | Check | 2 | 1 | 0 |
|---|---|---|---|---|
| 20 | Evals exist with assertions (auto) | Three or more cases, each with a prompt and assertions. Cases include a thin-input case. | One or two cases, or cases without assertions. | None. |
| 21 | Trigger tests (auto) | `should_trigger` cases of both kinds, three or more each. | One kind only. | None. |
| 22 | Rules pruned by evidence (judge) | The changelog or evals show a rule removed or added because a run showed it. | Pruning is claimed, not shown. | No sign of pruning. |
| 23 | Checks and changelog (auto) | CI or a check script, plus a changelog. | One of the two. | Neither. |
| 24 | Re-tested in real hosts (judge) | A recorded run in at least two hosts after the last change. | One host. | Prompt tests only. |

## Reading the result

- A low Proof score on an installed skill is expected. Packaging drops `evals/`.
- Two readings of one check can both be fair. Score the reading that matches the author's stated style, and name it.
