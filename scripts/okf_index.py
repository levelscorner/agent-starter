#!/usr/bin/env python3
"""okf-index: keep a docs folder readable by agents, in Google's Open Knowledge Format v0.2.

Every doc starts with a header (YAML front matter) holding at least `type`,
`title` and `description`. Every folder gets an `index.md` that lists its docs,
one line each, grouped by type, plus its sub-folders. Agents read the index
first and open only the docs they need.

    python3 scripts/okf_index.py                 # write every index.md
    python3 scripts/okf_index.py --check         # exit 1 if a header is missing or an index is stale
    python3 scripts/okf_index.py --add-headers   # fill missing headers from the folder, first heading and first line

Settings live in `okf.toml` at the repo root (all optional):

    bundles = ["docs"]            # folders that hold docs ("." for the whole repo)
    skip = ["docs/archive/**"]    # paths left out of headers and indexes
    exempt = ["MEMORY.md"]        # file names that need no header and are not listed
    also_read_under = "metadata"  # only when a tool owns the header and nests extra keys there
    required = ["type", "description"]  # default: type, title, description; title then comes from the file name
    [types]                       # default `type` per folder, for --add-headers
    "docs/learn" = "Teaching Note"

Python 3.11 or newer, standard library only. Spec:
https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
Source of this file: https://github.com/levelscorner/agent-starter/blob/main/scripts/okf_index.py
"""
from __future__ import annotations

import argparse
import fnmatch
import pathlib
import re
import sys
import tomllib
from dataclasses import dataclass, field

OKF_VERSION = "0.2"
MARKER = "<!-- okf-index: written by scripts/okf_index.py from each doc's header. Edit the docs, not this file. -->"
RESERVED = {"index.md", "log.md"}
REQUIRED = ("type", "title", "description")
DEFAULT_TYPE = "Document"
MAX_DESCRIPTION = 200
KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$")
LABEL_LINE_RE = re.compile(r"^(\*\*[^*]{1,30}:?\*\*:?|[A-Z][\w-]*( [\w-]+)?:)\s")  # "**Status:** accepted", "Date: 2026-11-17"


# ---------- reading headers ----------

@dataclass
class Header:
    fields: dict[str, str]
    end: int  # index of the closing `---` line


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] == '"':
        return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(v) >= 2 and v[0] == v[-1] == "'":
        return v[1:-1].replace("''", "'")
    return v


def read_header(text: str) -> Header | None:
    """Top-level scalar keys of the front matter, or None when there is none."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None
    fields: dict[str, str] = {}
    parent = ""
    i = 1
    while i < end:
        m = KEY_RE.match(lines[i])
        i += 1
        if not m:
            child = re.match(r"^\s+([A-Za-z_][\w-]*):\s+(\S.*)$", lines[i - 1])
            if parent and child:  # one level of nesting, kept as "parent.child"
                fields[f"{parent}.{child.group(1)}"] = _unquote(child.group(2))
            continue
        parent = ""
        key, val = m.group(1), (m.group(2) or "").strip()
        if val.startswith(("|", ">")) and len(val) <= 2:
            parts = []
            while i < end and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                parts.append(lines[i].strip())
                i += 1
            joiner = "\n" if val.startswith("|") else " "
            fields[key] = joiner.join(p for p in parts if p).strip()
        elif val and not val.startswith("#"):
            fields[key] = _unquote(val.split(" #")[0] if not val.startswith(("'", '"')) else val)
        else:
            fields[key] = ""  # a nested map or an empty value
            parent = key
    return Header(fields, end)


# ---------- settings and walking ----------

@dataclass
class Settings:
    root: pathlib.Path
    bundles: list[str] = field(default_factory=lambda: ["docs"])
    skip: list[str] = field(default_factory=list)
    exempt: list[str] = field(default_factory=list)
    types: dict[str, str] = field(default_factory=dict)
    required: tuple[str, ...] = REQUIRED
    nested: str = ""  # also read type/title/description under this key (a tool that owns the header nests them)


def load_settings(root: pathlib.Path) -> Settings:
    s = Settings(root)
    cfg = root / "okf.toml"
    if cfg.exists():
        data = tomllib.loads(cfg.read_text())
        s.bundles = list(data.get("bundles", s.bundles))
        s.skip = list(data.get("skip", []))
        s.exempt = list(data.get("exempt", []))
        s.types = dict(data.get("types", {}))
        s.nested = str(data.get("also_read_under", ""))
        s.required = tuple(data.get("required", REQUIRED))
        if "type" not in s.required:
            raise SystemExit("okf.toml: `required` must include type (OKF v0.2 needs it)")
    return s


def rel(s: Settings, p: pathlib.Path) -> str:
    return p.relative_to(s.root).as_posix() or "."


def skipped(s: Settings, r: str) -> bool:
    for pat in s.skip:
        base = pat[:-3] if pat.endswith("/**") else pat
        if fnmatch.fnmatch(r, pat) or r == base or r.startswith(base.rstrip("/") + "/"):
            return True
    return False


def is_doc(s: Settings, p: pathlib.Path) -> bool:
    return (p.is_file() and p.suffix == ".md" and p.name not in RESERVED
            and p.name not in s.exempt and not skipped(s, rel(s, p)))


def child_dirs(s: Settings, d: pathlib.Path) -> list[pathlib.Path]:
    return sorted(c for c in d.iterdir() if c.is_dir() and not c.name.startswith(".")
                  and c.name != "node_modules" and not skipped(s, rel(s, c)))


def docs_in(s: Settings, d: pathlib.Path) -> list[pathlib.Path]:
    return sorted(c for c in d.iterdir() if is_doc(s, c))


def walk(s: Settings):
    """Yield (folder, docs, sub-folders that hold docs) for every bundle, deepest first."""
    counts: dict[pathlib.Path, int] = {}

    def visit(d: pathlib.Path):
        subs = []
        for c in child_dirs(s, d):
            yield from visit(c)
            if counts.get(c, 0):
                subs.append(c)
        docs = docs_in(s, d)
        counts[d] = len(docs) + sum(counts[c] for c in subs)
        yield d, docs, subs, counts

    for b in s.bundles:
        d = (s.root / b).resolve()
        if d.is_dir():
            yield from visit(d)


# ---------- writing indexes ----------

def _one_line(v: str) -> str:
    return re.sub(r"\s+", " ", v or "").strip()


def entry(name: str, link: str, desc: str) -> str:
    return f"* [{name}]({link})" + (f" - {desc}" if desc else "") + "\n"


def value(s: Settings, h: Header | None, key: str) -> str:
    """A header value: top level first, then under `also_read_under` when set."""
    if h is None:
        return ""
    return h.fields.get(key) or (h.fields.get(f"{s.nested}.{key}", "") if s.nested else "")


def doc_title(s: Settings, p: pathlib.Path, h: Header | None, text: str) -> str:
    return _one_line(value(s, h, "title")) or guess_title(p, text)


def render_index(s: Settings, d: pathlib.Path, docs, subs, counts, bundle_root: bool) -> str:
    groups: dict[str, list[str]] = {}
    for p in docs:
        text = p.read_text(errors="replace")
        h = read_header(text)
        desc = _one_line(value(s, h, "description"))
        if value(s, h, "status") == "deprecated":
            desc = f"{desc} (deprecated)".strip()
        groups.setdefault(_one_line(value(s, h, "type")) or DEFAULT_TYPE, []).append(
            entry(doc_title(s, p, h, text), p.name, desc))
    out = []
    if bundle_root:
        out.append(f'---\nokf_version: "{OKF_VERSION}"\n---\n')
    out.append(MARKER + "\n")
    for t in sorted(groups, key=str.lower):
        out.append(f"\n# {t}\n\n" + "".join(groups[t]))
    if subs:
        lines = []
        for c in subs:
            readme = c / "README.md"
            h = read_header(readme.read_text(errors="replace")) if is_doc(s, readme) else None
            desc = _one_line(value(s, h, "description"))
            n = counts[c]
            lines.append(entry(c.name, c.name + "/", desc or f"{n} document{'s' if n != 1 else ''}"))
        out.append("\n# Folders\n\n" + "".join(lines))
    return "".join(out)


def plan_indexes(s: Settings) -> dict[pathlib.Path, str | None]:
    """Index path -> wanted text (None means a generated index that should go)."""
    roots = {(s.root / b).resolve() for b in s.bundles}
    plan: dict[pathlib.Path, str | None] = {}
    for d, docs, subs, counts in walk(s):
        target = d / "index.md"
        if docs or subs:
            plan[target] = render_index(s, d, docs, subs, counts, d in roots)
        elif target.exists():
            plan[target] = None
    return plan


def hand_written(p: pathlib.Path) -> bool:
    return p.exists() and MARKER not in p.read_text(errors="replace")


# ---------- checking headers ----------

def header_problems(s: Settings) -> list[str]:
    out = []
    for _, docs, _, _ in walk(s):
        for p in docs:
            h = read_header(p.read_text(errors="replace"))
            if h is None:
                out.append(f"{rel(s, p)}: no header (start the file with --- type, title, description ---)")
                continue
            where = f"top-level or under `{s.nested}`" if s.nested else "top-level"
            for k in s.required:
                if not value(s, h, k):
                    out.append(f"{rel(s, p)}: header has no {where} `{k}`")
    return out


# ---------- adding headers ----------

def _strip_md(line: str) -> str:
    line = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"[*_`]+", "", line)
    return _one_line(line.lstrip("#>-+ ").strip())


def _body(text: str) -> list[str]:
    h = read_header(text)
    lines = text.lstrip("﻿").splitlines()
    return lines[h.end + 1:] if h else lines


def guess_title(p: pathlib.Path, text: str) -> str:
    fence = False
    for line in _body(text):
        if line.startswith("```"):
            fence = not fence
        elif not fence and re.match(r"^#\s+\S", line):
            return _strip_md(line)
    name = re.sub(r"[-_]+", " ", p.stem).strip()
    return name[:1].upper() + name[1:]


SUMMARY_HEADING_RE = re.compile(r"^#{2,6}\s+\W*(decision|summary|tl;?dr|in one line|the answer)\b", re.I)


def _prose_lines(lines: list[str]):
    """Yield (raw line, is a summary heading) for lines outside code fences and comments."""
    fence = comment = False
    for raw in lines:
        line = raw.strip()
        if line.startswith(("```", "~~~")):
            fence = not fence
            continue
        if fence:
            continue
        if comment or line.startswith("<!--"):
            comment = "-->" not in line
            continue
        yield line


LIST_RE = re.compile(r"^([-*+]|\d+[.)])\s+")
NOT_PROSE = ("#", "|", "---", "===", "<", "![")


def _first_sentence(lines) -> str:
    lines = list(lines)
    for i, line in enumerate(lines):
        bare = LIST_RE.sub("", line)  # drop a list marker
        if (not bare or bare.startswith(NOT_PROSE) or LABEL_LINE_RE.match(bare)):
            continue
        for nxt in lines[i + 1:]:  # a hard-wrapped paragraph continues on the next lines
            if not nxt or nxt.startswith(NOT_PROSE) or LIST_RE.match(nxt):
                break
            bare += " " + nxt
        d = _strip_md(bare)
        if not d:
            continue
        m = re.search(r"[.!?](\s|$)", d)  # OKF: one sentence
        if m:
            d = d[:m.start() + 1]
        if len(d) > MAX_DESCRIPTION:
            d = d[:MAX_DESCRIPTION].rsplit(" ", 1)[0] + "..."
        return d
    return ""


def guess_description(text: str) -> str:
    """One sentence: from a Decision or Summary section if there is one, else the first prose line."""
    lines = list(_prose_lines(_body(text)))
    for i, line in enumerate(lines):
        if SUMMARY_HEADING_RE.match(line):
            section = []
            for nxt in lines[i + 1:]:
                if nxt.startswith("#"):
                    break
                section.append(nxt)
            d = _first_sentence(section)
            if d:
                return d
    return _first_sentence(lines)


def _yaml(v: str) -> str:
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'


def default_type(s: Settings, p: pathlib.Path) -> str:
    r = rel(s, p.parent)
    best = ""
    for folder in s.types:
        f = folder.strip("/")
        if (r == f or r.startswith(f + "/") or f == ".") and len(f) > len(best):
            best = f
    return s.types.get(best, s.types.get(best + "/", DEFAULT_TYPE)) if best else DEFAULT_TYPE


def add_header(s: Settings, p: pathlib.Path) -> bool:
    text = p.read_text(errors="replace")
    nl = "\r\n" if "\r\n" in text else "\n"
    h = read_header(text)
    have = {k: value(s, h, k) for k in REQUIRED}
    # a key that exists at the top level but is empty (a nested map) is not written twice
    taken = {k for k in REQUIRED if h is not None and k in h.fields and not h.fields[k]}
    new = []
    if not have.get("type"):
        new.append(f"type: {default_type(s, p)}")
    if not have.get("title"):
        new.append(f"title: {_yaml(guess_title(p, text))}")
    if not have.get("description"):
        new.append(f"description: {_yaml(guess_description(text) or guess_title(p, text))}")
    if not new:
        return False
    if h is None:
        text = nl.join(["---", *new, "---", ""]) + text.lstrip("﻿")
    else:
        lines = text.lstrip("﻿").split(nl)
        # a missing key goes right after the opening ---
        new = [n for n in new if n.split(":", 1)[0] not in taken]
        lines[1:1] = new
        text = nl.join(lines)
    p.write_text(text)
    return True


# ---------- main ----------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Write or check OKF v0.2 index.md files.")
    ap.add_argument("--root", default=".", help="repo root (default: here)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit 1 if a header is missing or an index is stale")
    mode.add_argument("--add-headers", action="store_true", help="fill missing headers, then stop")
    a = ap.parse_args(argv)
    s = load_settings(pathlib.Path(a.root).resolve())

    if a.add_headers:
        changed = [rel(s, p) for _, docs, _, _ in walk(s) for p in docs if add_header(s, p)]
        print(f"okf-index: added headers to {len(changed)} docs")
        for c in changed:
            print(f"  {c}")
        return 0

    problems = header_problems(s)
    plan = plan_indexes(s)
    written = 0
    for path, want in sorted(plan.items()):
        r = rel(s, path)
        if hand_written(path):
            problems.append(f"{r}: written by hand; move its text into README.md so okf-index can own index.md")
            continue
        have = path.read_text() if path.exists() else None
        if have == want:
            continue
        if a.check:
            problems.append(f"{r}: {'missing' if have is None else 'should be removed' if want is None else 'out of date'}"
                            " (run python3 scripts/okf_index.py)")
        elif want is None:
            path.unlink()
            written += 1
        else:
            path.write_text(want)
            written += 1

    for pr in problems:
        print(pr)
    if a.check:
        print(f"okf-index: {'FAIL' if problems else 'PASS'} ({len(plan)} indexes, {len(problems)} problems)")
        return 1 if problems else 0
    print(f"okf-index: wrote {written} of {len(plan)} indexes; {len(problems)} header problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
