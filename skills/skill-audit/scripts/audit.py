#!/usr/bin/env python3
"""Score a skill folder against a 24-check rubric. Standard library only.

Usage:
  python3 audit.py <skill-folder-or-SKILL.md> [--json] [--override JSON|@file]

--override sets a score (0, 1, 2) for any check id, for example '{"4":2,"22":1}'.
Use it for the judge checks and to correct a heuristic check after reading.
The script never edits the audited skill. Exit code 2 means no SKILL.md was found.
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

try:
    STDLIB = frozenset(sys.stdlib_module_names)
except AttributeError:
    STDLIB = frozenset(('__future__', '_abc', '_aix_support', '_ast', '_asyncio', '_bisect', '_blake2', '_bootsubprocess', '_bz2', '_codecs', '_codecs_cn', '_codecs_hk', '_codecs_iso2022', '_codecs_jp', '_codecs_kr', '_codecs_tw', '_collections', '_collections_abc', '_compat_pickle', '_compression', '_contextvars', '_crypt', '_csv', '_ctypes', '_curses', '_curses_panel', '_datetime', '_dbm', '_decimal', '_elementtree', '_frozen_importlib', '_frozen_importlib_external', '_functools', '_gdbm', '_hashlib', '_heapq', '_imp', '_io', '_json', '_locale', '_lsprof', '_lzma', '_markupbase', '_md5', '_msi', '_multibytecodec', '_multiprocessing', '_opcode', '_operator', '_osx_support', '_overlapped', '_pickle', '_posixshmem', '_posixsubprocess', '_py_abc', '_pydecimal', '_pyio', '_queue', '_random', '_scproxy', '_sha1', '_sha256', '_sha3', '_sha512', '_signal', '_sitebuiltins', '_socket', '_sqlite3', '_sre', '_ssl', '_stat', '_statistics', '_string', '_strptime', '_struct', '_symtable', '_thread', '_threading_local', '_tkinter', '_tokenize', '_tracemalloc', '_typing', '_uuid', '_warnings', '_weakref', '_weakrefset', '_winapi', '_zoneinfo', 'abc', 'aifc', 'antigravity', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore', 'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'bisect', 'builtins', 'bz2', 'cProfile', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser', 'contextlib', 'contextvars', 'copy', 'copyreg', 'crypt', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis', 'distutils', 'doctest', 'email', 'encodings', 'ensurepip', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'fractions', 'ftplib', 'functools', 'gc', 'genericpath', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'idlelib', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'nt', 'ntpath', 'nturl2path', 'numbers', 'opcode', 'operator', 'optparse', 'os', 'ossaudiodev', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'pydoc_data', 'pyexpat', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'sre_compile', 'sre_constants', 'sre_parse', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'textwrap', 'this', 'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'tomllib', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib', 'zoneinfo'))


CHECKS = {
    1: ("Trigger", "Description states triggers, not steps", 3, "heuristic"),
    2: ("Trigger", "Name is valid and specific", 1, "auto"),
    3: ("Trigger", "Scope boundary is stated", 1, "heuristic"),
    4: ("Content", "Teaches only what the model would not do by default", 2, "judge"),
    5: ("Content", "Opens with the job, then ordered steps", 1, "judge"),
    6: ("Content", "Steps end on checkable completion criteria", 2, "heuristic"),
    7: ("Content", "Positive phrasing, reasons over shouting", 1, "heuristic"),
    8: ("Content", "One clear example, not a pile", 1, "heuristic"),
    9: ("Content", "Short main file, detail behind pointers", 2, "auto"),
    10: ("Content", "One source of truth per fact", 1, "auto"),
    11: ("Reliability", "Deterministic work lives in scripts", 1, "auto"),
    12: ("Reliability", "Handles thin or missing input", 2, "heuristic"),
    13: ("Reliability", "Precedence for conflicts is defined", 1, "heuristic"),
    14: ("Reliability", "User context wins over skill defaults", 1, "heuristic"),
    15: ("Reliability", "States what the skill never does", 1, "heuristic"),
    16: ("Portability", "Portable frontmatter core", 2, "auto"),
    17: ("Portability", "Names capabilities, not harness tools", 2, "heuristic"),
    18: ("Portability", "Relative paths, no installs or network", 1, "auto"),
    19: ("Portability", "Works standalone", 1, "auto"),
    20: ("Proof", "Evals exist with assertions", 3, "auto"),
    21: ("Proof", "Trigger tests: should and should-not fire", 2, "auto"),
    22: ("Proof", "Rules pruned by evidence", 1, "judge"),
    23: ("Proof", "Checks and changelog", 1, "auto"),
    24: ("Proof", "Re-tested in real hosts", 1, "judge"),
}
JUDGE_Q = {
    4: "Does each rule change behavior? Delete any line a strong model already obeys.",
    5: "Does the body open with the outcome, then numbered steps in run order?",
    22: "Do evals or the changelog show rules added or removed because of results?",
    24: "Is there evidence of a run in a real host, not only prompt tests?",
}
PILLARS = ["Trigger", "Content", "Reliability", "Portability", "Proof"]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
TEXT_EXT = {".md", ".txt", ".yaml", ".yml"}
SPEC_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
HARNESS_KEYS = {"disable-model-invocation", "user-invocable", "model", "context", "agent",
                "hooks", "argument-hint", "paths", "allowed_tools"}
# Built from pieces so this file does not flag itself.
ABS_PARTS = ["/Use" + "rs/", "/ho" + "me/", "/mn" + "t/"]
TOOL_RE = (r"(bash_tool|str_replace\w*|present_files|create_file|web_search|web_fetch|TodoWrite|"
           r"WebSearch|WebFetch|NotebookEdit|AskUserQuestion|(?:Bash|Read|Edit|Write) tool|mcp__\w+)")



def parse_frontmatter(text):
    m = re.match(r"\A---\s*\n(.*?)\n---\s*(\n|\Z)", text, re.S)
    if not m:
        return None, text
    lines, fm, i = m.group(1).split("\n"), {}, 0
    while i < len(lines):
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", lines[i])
        if km and not lines[i].startswith((" ", "\t")):
            key, val = km.group(1), km.group(2).strip()
            parts = [] if re.match(r"^[>|][+-]?$", val) else [val.strip("\"'")]
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                parts.append(lines[i].strip())
                i += 1
            fm[key] = " ".join(p for p in parts if p)
            continue
        i += 1
    return fm, text[m.end():]


def iter_files(root):
    for p in sorted(root.rglob("*")):
        if p.is_file() and not (set(p.relative_to(root).parts[:-1]) & SKIP_DIRS):
            yield p


def prose_lines(text):
    out, fence = [], False
    for ln in text.split("\n"):
        if ln.strip().startswith("```"):
            fence = not fence
            continue
        if not fence:
            out.append(ln)
    return out


def norm(line):
    line = re.sub(r"^[\s>#*\-\d.)]+", "", line)
    return re.sub(r"\s+", " ", re.sub(r"[`*_]", "", line)).strip().lower()


def find_repo(root):
    for d in [root.resolve(), *root.resolve().parents]:
        if (d / ".git").exists():
            return d
    return None


def load_evals(root):
    cases, err = [], None
    ej = root / "evals" / "evals.json"
    if ej.exists():
        try:
            data = json.loads(ej.read_text(encoding="utf-8"))
            for it in (data.get("evals", []) if isinstance(data, dict) else data):
                cases.append(bool(it.get("prompt") and (it.get("assertions") or it.get("expected_output"))))
        except (ValueError, AttributeError) as e:
            err = f"evals.json is not valid: {e}"
    ed = root / "evals"
    if ed.is_dir():
        for d in sorted(ed.iterdir()):
            if d.is_dir() and (d / "prompt.md").exists():
                g = d / "graders"
                cases.append((g.is_dir() and any(g.iterdir())) or (d / "case.yaml").exists())
    return cases, err


def trigger_cases(root):
    pos = neg = 0
    for p in iter_files(root):
        if p.suffix != ".json":
            continue
        try:
            stack = [json.loads(p.read_text(encoding="utf-8"))]
        except ValueError:
            continue
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                if "should_trigger" in x:
                    pos, neg = (pos + 1, neg) if x["should_trigger"] else (pos, neg + 1)
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    return pos, neg


def run(root):
    path = root / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"No SKILL.md in {root}")
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        raise ValueError(f"SKILL.md is not valid UTF-8: {e}")
    if not raw.strip():
        raise ValueError("SKILL.md is empty")
    text = raw
    fm, body = parse_frontmatter(text)
    if fm is None:
        raise ValueError("SKILL.md has no frontmatter")
    fm = fm or {}
    name, desc = fm.get("name", ""), fm.get("description", "")
    body_lines = body.split("\n")
    md = {}
    for p in iter_files(root):
        rel = p.relative_to(root)
        if p.suffix in TEXT_EXT and rel.parts[0] != "evals":
            md[str(rel)] = p.read_text(encoding="utf-8", errors="replace")
    all_md = "\n".join(md.values())
    scripts = [p for p in iter_files(root) if p.relative_to(root).parts[0] == "scripts"]
    res = {}

    def add(cid, score, notes=None, na=False):
        res[cid] = {"score": None if na else max(0, min(2, score)), "notes": notes or [], "na": na}

    # 1 description
    trig = re.compile(r"\b(use (this )?(when|for|whenever|if|on|any time)|when the (user|agent)|whenever|"
                      r"triggers?|asks? (to|for)|mentions?|invoke when|on (an )?explicit)\b", re.I)
    narr = re.compile(r"(\u2192|->|\bstep \d|\bfirst\b[^.]*\bthen\b|\bthen\b[^.]*\bthen\b|\bfollowed by\b)", re.I)
    if not desc:
        add(1, 0, ["description is missing"])
    else:
        s, n = 2, []
        if not trig.search(desc):
            s = 0
            n.append("no trigger phrase; start with 'Use when ...'")
        else:
            if narr.search(desc):
                s -= 1
                n.append("description narrates steps; state triggers only")
            if len(desc) > 1024:
                s -= 1
                n.append(f"{len(desc)} chars; the limit is 1024")
            elif len(desc) < 60:
                s -= 1
                n.append(f"{len(desc)} chars; too thin to trigger reliably")
        if "<" in desc or ">" in desc:
            s -= 1
            n.append("angle brackets in description are rejected by validators")
        n.append(f"{len(desc.split())} words. Confirm the key word comes first.")
        add(1, s, n)

    # 2 name
    if not name:
        add(2, 0, ["name is missing"])
    else:
        s, n = 2, []
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name) or len(name) > 64:
            s = 0
            n.append("name must be kebab-case, 64 chars or fewer")
        elif name != root.resolve().name:
            s = 1
            n.append(f"name '{name}' differs from folder '{root.resolve().name}'")
        if name in {"helper", "utils", "tool", "skill", "assistant", "general", "misc"}:
            s = min(s, 1)
            n.append("name is generic; name the job")
        add(2, s, n)

    # 3 scope boundary
    scope = re.compile(r"\b(not for|do not use|don't use|out of scope|skip (this )?when|does not (cover|handle)|"
                       r"only for|never (use|run|open|write|edit|delete))\b", re.I)
    if scope.search(desc):
        add(3, 2, ["boundary is in the description"])
    elif scope.search(body) or re.search(r"^#+\s*(scope|boundar|non-goals|out of scope)", body, re.I | re.M):
        add(3, 1, ["boundary is in the body only; add it to the description"])
    else:
        add(3, 0, ["no statement of what the skill does not cover"])

    # 6 completion criteria
    steps = [l for l in prose_lines(body) if re.match(r"^\s*\d+[.)]\s", l)]
    done = re.compile(r"(done when|done:|until|\bevery\b|\beach\b.*\b(listed|covered|checked)|verify|confirm|"
                      r"check that|exit code|passes|complete when|finished when|ends? (on|with))", re.I)
    marked = [l for l in steps if done.search(l)]
    if not steps:
        add(6, 0, ["no numbered steps found"])
    else:
        r = len(marked) / len(steps)
        add(6, 2 if r >= 0.5 else 1 if r >= 0.2 else 0,
            [f"{len(marked)} of {len(steps)} steps carry a completion criterion"])

    # 7 positive phrasing
    prose = [l for l in prose_lines(body) if l.strip() and not l.startswith(("#", "|"))]
    neg = [l for l in prose if re.search(r"\b(do not|don't|never|avoid|must not|cannot|can't|won't)\b", l, re.I)]
    shout = re.findall(r"\b(MUST|ALWAYS|NEVER|CRITICAL|IMPORTANT)\b", body)
    ratio = len(neg) / max(1, len(prose))
    s = 2 if ratio <= 0.15 and len(shout) <= 2 else 1 if ratio <= 0.3 and len(shout) <= 5 else 0
    add(7, s, [f"{len(neg)} of {len(prose)} prose lines are prohibitions; {len(shout)} shouted words"])

    # 8 examples
    ex = len(re.findall(r"^\s*(#+\s*|\*\*)?examples?\b", body, re.I | re.M))
    add(8, 2 if 1 <= ex <= 2 else 1 if ex in (0, 3, 4) else 0,
        [f"{ex} example blocks" + ("; none found, fine for judgment skills" if ex == 0 else "")])

    # 9 short main file and pointers
    n = len(body_lines)
    s, notes = (2 if n <= 100 else 1 if n <= 500 else 0), [f"SKILL.md body is {n} lines"]
    ptrs = set(re.findall(r"(?<![\w/.-])((?:references|scripts|assets|agents)/[\w./-]*\w)", text))
    ptrs |= {m for m in re.findall(r"\]\(([^)#\s]+)\)", text) if not m.startswith(("http", "mailto"))}
    broken = sorted(p for p in ptrs if not (root / p).exists())
    refdir = root / "references"
    unref = sorted(str(p.relative_to(root)) for p in refdir.rglob("*.md")
                   if str(p.relative_to(root)) not in text) if refdir.is_dir() else []
    if broken:
        s -= 1
        notes.append("broken pointers: " + ", ".join(broken))
    if unref:
        s -= 1
        notes.append("references never pointed to: " + ", ".join(unref))
    for k, v in md.items():
        if k.startswith("references/") and len(v.split("\n")) > 300 and not re.search(r"(?i)^#+.*contents|toc", v, re.M):
            notes.append(f"{k} exceeds 300 lines without a table of contents")
            s -= 1
            break
    if n > 100 and not refdir.is_dir():
        notes.append("long file with no references/ folder; add a disclosure layer")
    add(9, s, notes)

    # 10 duplication
    seen = {}
    for k, v in md.items():
        for ln in prose_lines(v):
            if ln.lstrip().startswith("|") or "sync:" in ln:
                continue
            t = norm(ln)
            if len(t.split()) >= 8:
                seen.setdefault(t, []).append(k)
    dups = {t: f for t, f in seen.items() if len(f) >= 2}
    add(10, 2 if not dups else 1 if len(dups) <= 3 else 0,
        [f"{len(dups)} repeated lines"] + [f"'{t[:70]}' in {sorted(set(f))}" for t, f in list(dups.items())[:3]])

    # 11 scripts
    code = [p for p in scripts if p.suffix in {".py", ".sh", ".js", ".ts", ".mjs"} and p.name != "__init__.py"]
    if code:
        s, notes, unmentioned = 2, [f"{len(code)} script files"], []
        std = set(STDLIB)
        for p in code:
            rel = p.relative_to(root)
            anc = [str(a) for a in rel.parents if str(a) != "."]
            if not any(x in text for x in [str(rel), p.name, *anc]):
                unmentioned.append(str(rel))
            if p.suffix == ".py":
                try:
                    tree = ast.parse(p.read_text(encoding="utf-8"))
                except SyntaxError as e:
                    s = 0
                    notes.append(f"{rel} has a syntax error: {e}")
                    continue
                mods = {a.name.split(".")[0] for x in ast.walk(tree) if isinstance(x, ast.Import) for a in x.names}
                mods |= {x.module.split(".")[0] for x in ast.walk(tree)
                         if isinstance(x, ast.ImportFrom) and x.module and x.level == 0}
                local = {q.stem for q in code} | {q.parent.name for q in code}
                extra = sorted(m for m in mods if m not in std and m not in local)
                if extra:
                    s -= 1
                    notes.append(f"{rel} imports non-stdlib modules: {', '.join(extra)}")
                if not ast.get_docstring(tree):
                    s -= 1
                    notes.append(f"{rel} has no usage docstring")
        if unmentioned:
            s -= 1
            notes.append(f"{len(unmentioned)} scripts never mentioned in SKILL.md, for example: {', '.join(unmentioned[:3])}")
        add(11, s, notes[:6])
    else:
        words = len(re.findall(r"\b(validate|format|convert|parse|count|lint|generate|extract|rename|"
                               r"compute|calculate|resize|merge)\b", body, re.I))
        if words >= 4:
            add(11, 1, [f"no scripts/, but prose names deterministic work {words} times; consider a script"])
        else:
            add(11, 0, na=True, notes=["no scripts and no deterministic work in prose"])

    # 12 thin input
    phr = ["missing", "thin", "vague", "unclear", "ambiguous", "incomplete", "not given", "not provided",
           "unknown", "assum", "ask", "clarif", "cannot find", "no input"]
    hit = [p for p in phr if re.search(r"\b" + p, body, re.I)]
    add(12, 2 if len(hit) >= 3 else 1 if hit else 0, ["signals found: " + (", ".join(hit) or "none")])

    # 13 precedence
    pr = re.findall(r"(precedence|priority|order of (?:strength|importance)|takes? priority|\bwins\b|overrides?|conflict)",
                    body, re.I)
    add(13, 2 if len(pr) >= 2 else 1 if pr else 0, [f"{len(pr)} precedence signals"])

    # 14 user context wins
    uc = re.findall(r"(match(?:es)? (?:the )?(?:existing|repo|project|user|their)|"
                    r"(?:repo|project|user)'?s? (?:convention|style|format|language|preference)|"
                    r"existing (?:style|convention|format)|house style|user.s (?:format|style|language))", body, re.I)
    add(14, 2 if len(uc) >= 2 else 1 if uc else 0, [f"{len(uc)} user-context signals"])

    # 15 never-does
    nv = re.findall(r"(never (?:run|open|merge|delete|edit|write|send|push|commit|modify|post|execute|install)|"
                    r"read-only|text only|does not (?:run|open|edit|delete|send|push|modify|write)|"
                    r"do not (?:run|open|edit|delete|send|push|modify|write|install|execute))", body, re.I)
    add(15, 2 if nv else 0, [f"{len(nv)} side-effect limits stated"])

    # 16 portable frontmatter
    keys = set(fm)
    harness = sorted(keys & HARNESS_KEYS)
    other = sorted(keys - SPEC_KEYS - HARNESS_KEYS)
    notes = ["keys: " + ", ".join(sorted(keys))]
    if harness:
        notes.append("harness-specific keys: " + ", ".join(harness))
    if other:
        notes.append("unknown keys: " + ", ".join(other))
    if (root / "agents").is_dir():
        notes.append("agents/ sidecar present: good place for per-harness settings")
    bad = len(harness) + len(other)
    add(16, 0 if not fm else 2 if bad == 0 else 1 if bad == 1 else 0, notes)

    # 17 capabilities not tools
    tools = set(re.findall(TOOL_RE, all_md))
    add(17, 2 if not tools else 1 if len(tools) <= 2 else 0,
        ["harness tool names: " + (", ".join(sorted(tools)) or "none")]
        + (["name the capability and give a fallback"] if tools else []))

    # 18 relative paths, no installs, no network
    py_src = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in scripts if p.suffix in {".py", ".sh"})
    corpus = all_md + "\n" + py_src
    finds = [f"absolute path {a}" for a in ABS_PARTS if a in corpus]
    finds += [f"install or download command: {m}" for m in
              sorted(set(re.findall(r"(pip3? install|npm (?:i|install)\b|\bcurl |\bwget |apt(?:-get)? install|brew[ ]install)", corpus)))]
    for p in scripts:
        if p.suffix == ".py":
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for x in ast.walk(tree):
                names = ([a.name for a in x.names] if isinstance(x, ast.Import)
                         else [x.module or ""] if isinstance(x, ast.ImportFrom) else [])
                finds += [f"{p.name} imports network module {m}" for m in names
                          if m.split(".")[0] in {"requests", "httpx", "aiohttp", "socket", "ftplib", "smtplib"}
                          or m in {"urllib.request", "http.client", "http.server"}]
    add(18, 2 if not finds else 1 if len(finds) <= 2 else 0, finds or ["none"])

    # 19 standalone
    stop = {"this", "the", "a", "an", "that", "your", "my", "another", "each", "any", "one", "which", "same",
            "new", "existing", "audited", "every", "whole", "target", "given", "user", "whole", "single"}
    sk = [m for m in re.findall(r"\b(?:use|invoke|call|load|run|see|requires?|depends on|needs?)\s+(?:the\s+)?"
                               r"[`\"']?([a-z0-9]+(?:-[a-z0-9]+)*)[`\"']?\s+skill\b", all_md, re.I)
          if m.lower() not in stop]
    esc = [p for p in ptrs if (root / p).exists()
           and root.resolve() not in (root / p).resolve().parents and (root / p).resolve() != root.resolve()]
    hits = sk + esc
    add(19, 2 if not hits else 1 if len(hits) == 1 else 0, [f"cross-skill references: {hits or 'none'}"])

    # 20 evals
    cases, err = load_evals(root)
    notes = [err] if err else []
    if not cases:
        notes.append("no evals/ cases found (a packaged .skill file drops evals/ by design)")
        add(20, 0, notes)
    else:
        good = sum(cases)
        notes.append(f"{len(cases)} cases, {good} with assertions or graders")
        add(20, 2 if len(cases) >= 3 and good == len(cases) else 1, notes)

    # 21 trigger tests
    pos, ng = trigger_cases(root)
    add(21, 2 if pos and ng else 1 if pos or ng else 0,
        [f"should_trigger true: {pos}, false: {ng}" + ("" if pos and ng else "; add both kinds, 3 or more each")])

    # 23 checks and changelog
    repo = find_repo(root)
    chg = any(p.name.lower().startswith("changelog") for p in root.iterdir()) or \
        (repo is not None and any(p.name.lower().startswith("changelog") for p in repo.iterdir()))
    if repo is None:
        add(23, 2 if chg else 0, ["no git repo found; CI not assessed", "changelog " + ("found" if chg else "missing")])
    else:
        ci = (repo / ".github" / "workflows").is_dir() or any(
            (repo / x).exists() for x in ("tools/check.py", "Makefile", "tests"))
        add(23, int(ci) + int(chg),
            ["CI or check script " + ("found" if ci else "missing"), "changelog " + ("found" if chg else "missing")])

    # judge checks
    for cid in (4, 5, 22, 24):
        res[cid] = {"score": None, "notes": [JUDGE_Q[cid]], "na": False}

    stats = {"skill_md_lines": n, "description_words": len(desc.split()),
             "files": len(list(iter_files(root))), "scripts": len(scripts)}
    return {"skill": name or root.name, "path": str(root), "stats": stats, "res": res}


def finish(data, override):
    res = data["res"]
    for k, v in override.items():
        try:
            cid, score = int(k), int(v)
        except (TypeError, ValueError):
            raise ValueError(f"override keys and values must be integers: {k!r}={v!r}")
        if cid not in res:
            raise ValueError(f"unknown check id in override: {cid}")
        if score not in (0, 1, 2):
            raise ValueError(f"override score must be 0, 1, or 2: {cid}={score}")
        res[cid]["score"], res[cid]["na"], res[cid]["overridden"] = score, False, True
    rows, pil = [], {p: [0, 0] for p in PILLARS}
    for cid, (pillar, title, w, kind) in CHECKS.items():
        r = res[cid]
        rows.append({"id": cid, "pillar": pillar, "name": title, "weight": w, "score": r["score"], "na": r["na"],
                     "kind": kind + ("+read" if r.get("overridden") else ""), "notes": r["notes"]})
        if r["score"] is not None and not r["na"]:
            pil[pillar][0] += w * r["score"]
            pil[pillar][1] += w * 2
    got, mx = sum(v[0] for v in pil.values()), sum(v[1] for v in pil.values())
    pct = round(100 * got / mx) if mx else 0
    unscored = [r["id"] for r in rows if r["score"] is None and not r["na"]]
    grade = "A" if pct >= 90 else "B" if pct >= 80 else "C" if pct >= 65 else "D" if pct >= 50 else "F"
    fixes = sorted((r for r in rows if r["score"] is not None and r["score"] < 2 and not r["na"]),
                   key=lambda r: -r["weight"] * (2 - r["score"]))[:3]
    data.update({"checks": rows,
                 "total": {"percent": pct, "grade": grade, "provisional": bool(unscored), "unscored": unscored},
                 "pillars": {p: (round(100 * v[0] / v[1]) if v[1] else None) for p, v in pil.items()},
                 "top_fixes": [{"id": f["id"], "name": f["name"], "score": f["score"]} for f in fixes]})
    del data["res"]
    return data


def render(d):
    out = [f"SKILL AUDIT  {d['skill']}", d["path"],
           "SKILL.md {skill_md_lines} lines | description {description_words} words | "
           "files {files} | scripts {scripts}".format(**d["stats"])]
    cur = None
    for r in d["checks"]:
        if r["pillar"] != cur:
            cur = r["pillar"]
            p = d["pillars"][cur]
            out += ["", f"{cur.upper()}  {'n/a' if p is None else str(p) + '%'}"]
        sc = "n/a" if r["na"] else "?" if r["score"] is None else str(r["score"])
        shown = "n/a" if r["na"] else f"{sc}/2"
        out.append(f" {r['id']:>2}  {shown:>3}  w{r['weight']}  {r['name']}  [{r['kind']}]")
        out += [f"       - {n}" for n in r["notes"]]
    t = d["total"]
    out += ["", f"SCORE {t['percent']}/100  GRADE {t['grade']}"
            + (f"  PROVISIONAL, unscored checks: {t['unscored']}" if t["provisional"] else "")]
    if d["top_fixes"]:
        out.append("TOP FIXES: " + "; ".join(f"#{f['id']} {f['name']} ({f['score']}/2)" for f in d["top_fixes"]))
    return "\n".join(out)


def build_profile(root, data):
    text = (root / "SKILL.md").read_text(encoding="utf-8-sig")
    fm, body = parse_frontmatter(text)
    fm = fm or {}
    headings = [ln.strip() for ln in body.split("\n") if ln.strip().startswith("#")]
    files = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
    scripts_info = []
    sdir = root / "scripts"
    if sdir.is_dir():
        for p in sorted(sdir.iterdir()):
            if p.suffix in {".py", ".sh", ".js"}:
                doc = ""
                try:
                    src = p.read_text(encoding="utf-8", errors="replace")
                    m = re.search(r'"""(.*?)"""', src, re.S)
                    if m:
                        doc = m.group(1).strip().split("\n")[0]
                except OSError:
                    pass
                scripts_info.append({"file": str(p.relative_to(root)), "docstring": doc})
    evals_count = 0
    tc = 0
    try:
        ej = root / "evals" / "evals.json"
        if ej.exists():
            ed = json.loads(ej.read_text(encoding="utf-8"))
            evals_count = len(ed.get("evals", []) if isinstance(ed, dict) else ed)
    except (ValueError, OSError):
        pass
    # trigger cases
    pos, neg = trigger_cases(root)
    tc = pos + neg
    tokens = len(text.split()) + sum(
        len((root / f).read_text(encoding="utf-8", errors="replace").split())
        for f in files if f != "SKILL.md" and (root / f).suffix in {".md", ".txt", ".py", ".sh", ".json"}
    )
    return {
        "name": fm.get("name"),
        "description": fm.get("description"),
        "headings": headings,
        "files": files,
        "scripts": scripts_info,
        "eval_count": evals_count,
        "trigger_test_count": tc,
        "token_estimate": tokens,
        "skill_md_lines": data["stats"]["skill_md_lines"],
        "grade": data["total"]["grade"],
        "percent": data["total"]["percent"],
    }


def render_brief(d):
    t = d["total"]
    lines = [f"{d['skill']}: {t['percent']}/100 GRADE {t['grade']}"
             + (f" PROVISIONAL {t['unscored']}" if t["provisional"] else "")]
    if d["top_fixes"]:
        lines.append("TOP FIXES: " + "; ".join(f"#{f['id']} {f['name']} ({f['score']}/2)" for f in d["top_fixes"]))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--brief", action="store_true")
    ap.add_argument("--override", default="{}")
    ap.add_argument("--whatif", default=None, help="Project the score after fixes, JSON like {\"1\":2}")
    ap.add_argument("--profile", action="store_true", help="Print a profile of the skill as JSON")
    a = ap.parse_args()
    p = Path(a.path)
    root = p.parent if p.is_file() else p
    if not (root / "SKILL.md").exists():
        print(f"No SKILL.md in {root}", file=sys.stderr)
        sys.exit(2)
    ov = a.override
    try:
        if ov.startswith("@"):
            ov = Path(ov[1:]).read_text(encoding="utf-8")
        override = json.loads(ov)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"Bad --override value: {e}", file=sys.stderr)
        sys.exit(2)
    try:
        data = finish(run(root), override)
    except (FileNotFoundError, ValueError, OSError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
    if a.profile:
        prof = build_profile(root, data)
        print(json.dumps(prof, indent=2))
        return
    if a.whatif:
        try:
            wif = json.loads(a.whatif)
        except json.JSONDecodeError as e:
            print(f"Bad --whatif value: {e}", file=sys.stderr)
            sys.exit(2)
        try:
            proj = finish(run(root), {**override, **{str(k): int(v) for k, v in wif.items()}})
        except (ValueError, TypeError) as e:
            print(str(e), file=sys.stderr)
            sys.exit(2)
        base_pct = data["total"]["percent"]
        print(f"Projected: {proj['total']['percent']}/100 GRADE {proj['total']['grade']} "
              f"(from {base_pct}/100, +{proj['total']['percent'] - base_pct})")
        return
    if a.json:
        print(json.dumps(data, indent=2))
    elif a.brief:
        print(render_brief(data))
    else:
        print(render(data))


if __name__ == "__main__":
    main()
