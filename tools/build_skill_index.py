#!/usr/bin/env python3
"""Build or refresh skill-index/index.json from a catalog of skills.

The index is plain data: code filters it with zero model tokens. A record is
rebuilt only when its source file hash or its catalog entry changes; everything
else is kept byte for byte. The run prints what changed.

Catalog: a JSON list. Each entry has name, source (a label such as `library`,
`claude-skills`, `claude-plugin:<name>`, `house`), kind (skill or command),
category (1-6), area, description, status (house, library or other), risk,
risk_class (quarantine, cost or null), confidence (high, medium or low) and,
optionally, not_skill (true for stray files), path (a local file, read only to hash it, never written) and load
(where the full file sits under its source).

Usage: python3 tools/build_skill_index.py --catalog catalog.json [--check]
Standard library only.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

CATEGORIES = {1: "Engineering spine", 2: "Money path", 3: "Growth layer",
              4: "Glue", 5: "Product and UI", 6: "Unmapped / other"}
PRECEDENCE = {"owner-rule": 1, "house": 2, "library": 3, "other": 4, "quarantined": 5}
# Private repo names never go into this public repo. Replaced in descriptions.
SCRUB = [(re.compile(r"\bchotu-docs\b", re.I), "the docs repo"),
         (re.compile(r"\bclotho\b", re.I), "the pipeline service")]
# Built from parts so this file does not trip the repo's own leak check.
LEAK = re.compile("|".join(["/" + "Users/", "/" + "home/[a-z]", "~/" + "ws/", "@" + r"gmail\.com",
                            "sk" + "-[A-Za-z0-9_-]{20,}", "gh" + "[pousr]_[A-Za-z0-9]{20,}",
                            "github" + "_pat_", "AK" + "IA[0-9A-Z]{16}", "PRIVATE" + " KEY"]))
STOP = set("""a an and are as at be by can do for from has have how in into is it its of on or
that the this to use used uses using when with without you your any all every each not no
before after also only one more most other than then them they their what which who will
skill skills command commands run runs help helps make makes work works trigger""".split())
DEV = re.compile(r"\b(code|coding|test|tests|testing|debug|deploy|ci|cd|git|pr|api|backend|"
                 r"database|sql|postgres|docker|kubernetes|infra|security|refactor|lint|build|"
                 r"go|golang|python|rust|java|typescript|javascript|react|swift|kotlin|"
                 r"migration|migrations|server|cli|sdk|frontend|css|mobile)\b")
TECH = re.compile(r"\b(data|analytics|seo|model|llm|pipeline|ai|agent|agents|workflow|"
                  r"automation|spreadsheet|query|schema|ui|design|animation|accessibility|"
                  r"wcag|video|audio|image|cloudflare|performance)\b")


def words(text):
    return [w for w in re.findall(r"[a-z0-9][a-z0-9+#.]*[a-z0-9+#]|[a-z0-9]", text.lower())]


def stem(w):
    for suf in ("ing", "ies", "es", "ed", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)] + ("y" if suf == "ies" else "")
    return w


def keywords(name, area, desc, cap=14):
    seen, out = set(), []
    for w in words(name.replace("-", " ").replace(":", " ")) + words(area) + words(desc):
        k = stem(w)
        if len(k) < 2 or k in STOP or k.isdigit() or k in seen:
            continue
        seen.add(k)
        out.append(k)
        if len(out) >= cap:
            break
    return out


def scrub(text):
    for pat, rep in SCRUB:
        text = pat.sub(rep, text)
    text = re.sub(r"\s+", " ", text.replace("\\n", " ")).strip()
    return text if len(text) <= 200 else text[:197].rstrip() + "..."


def file_hash(path):
    if not path:
        return None
    p = Path(path)
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.is_file() else None


def entry_hash(e):
    keep = {k: e.get(k) for k in ("name", "source", "kind", "category", "area", "description",
                                  "status", "risk", "risk_class", "confidence", "load", "not_skill")}
    return hashlib.sha256(json.dumps(keep, sort_keys=True).encode()).hexdigest()[:12]


def build_record(e, fhash):
    name, area = e["name"], e.get("area") or ""
    desc = scrub(e.get("description") or "")
    text = f"{name} {area} {desc}".lower()
    dev = int(e["category"]) == 1 or bool(DEV.search(text))
    tech = dev or bool(TECH.search(text))
    status = e.get("status", "other")
    reason = None
    if e.get("risk_class") == "quarantine":
        status, reason = "quarantined", e.get("risk")
    rec = {
        "id": f'{e["source"]}:{e["kind"]}:{name}',
        "name": name, "source": e["source"], "kind": e["kind"],
        "category": int(e["category"]), "category_name": CATEGORIES[int(e["category"])],
        "area": area, "confidence": e.get("confidence", "low"),
        "tags": ["dev" if dev else "non-dev", "technical" if tech else "non-technical"]
                + (["cost-flagged"] if e.get("risk_class") == "cost" else [])
                + (["not-a-skill"] if e.get("not_skill") else []),
        "keywords": keywords(name, area, desc),
        "status": status, "status_reason": reason, "precedence": PRECEDENCE[status],
        "description": desc, "load": e.get("load"),
        "hash": fhash, "entry_hash": entry_hash(e),
    }
    if e.get("risk_class") == "cost":
        rec["note"] = scrub(e.get("risk") or "")
    blob = json.dumps(rec)
    if LEAK.search(blob):
        raise SystemExit(f"refusing to write a private path or secret in {rec['id']}")
    return rec


def load_index(path):
    if not path.is_file():
        return {}
    data = json.loads(path.read_text())
    return {r["id"]: r for r in data.get("records", [])}


def write_index(path, records):
    head = {"version": 1, "categories": CATEGORIES, "precedence": PRECEDENCE,
            "count": len(records)}
    lines = json.dumps(head, sort_keys=True)[:-1] + ', "records": [\n'
    lines += ",\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(lines + "\n]}\n")


def refresh(catalog, out_path):
    """Return (records, added, changed, removed). Unchanged records are reused as is."""
    old = load_index(out_path)
    records, added, changed, seen = [], [], [], set()
    for e in catalog:
        rid = f'{e["source"]}:{e["kind"]}:{e["name"]}'
        if rid in seen:
            continue
        seen.add(rid)
        fh = file_hash(e.get("path"))
        prev = old.get(rid)
        if prev and prev.get("hash") == fh and prev.get("entry_hash") == entry_hash(e):
            records.append(prev)
            continue
        records.append(build_record(e, fh))
        (changed if prev else added).append(rid)
    removed = sorted(set(old) - seen)
    records.sort(key=lambda r: r["id"])
    return records, added, changed, removed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "skill-index" / "index.json"))
    ap.add_argument("--check", action="store_true", help="exit 1 if the index is out of date; write nothing")
    a = ap.parse_args(argv)
    catalog = json.loads(Path(a.catalog).read_text())
    out = Path(a.out)
    records, added, changed, removed = refresh(catalog, out)
    for label, ids in (("added", added), ("changed", changed), ("removed", removed)):
        for rid in ids[:50]:
            print(f"{label}: {rid}")
        if len(ids) > 50:
            print(f"{label}: ... and {len(ids) - 50} more")
    total = len(added) + len(changed) + len(removed)
    print(f"{len(records)} records; {len(added)} added, {len(changed)} changed, {len(removed)} removed")
    if a.check:
        return 1 if total else 0
    if total or not out.is_file():
        write_index(out, records)
    return 0


if __name__ == "__main__":
    sys.exit(main())
