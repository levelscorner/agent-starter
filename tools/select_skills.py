#!/usr/bin/env python3
"""Pick the few skills a task needs, in two passes, from skill-index/index.json.

Pass 1 (zero model tokens): a tag and keyword filter over the index narrows
every skill down to 20-30 candidates. Ties go to the higher precedence:
house drafts, then library copies, then other copies. Quarantined skills are
reference only and left out unless --include-reference.

Pass 2: print a short ranking prompt (candidate names and descriptions only)
for the calling agent's own model to pick the top 3-5, or with --local rank
them here with BM25. Either way, only the chosen skills' full files get loaded.

--sweep-misfiled is a second cheap pass: it re-reads the Unmapped skills and the
low-confidence category guesses with looser keyword matching and lists the ones
that look misfiled, with a suggested category.

Usage:
  python3 tools/select_skills.py "add a retry to the payment webhook"
  python3 tools/select_skills.py "..." --local --top 3 [--category 1] [--area backend]
  python3 tools/select_skills.py --sweep-misfiled
Standard library only.
"""
import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_INDEX = Path(__file__).resolve().parent.parent / "skill-index" / "index.json"
STOP = set("""a an and are as at be by can do for from has have how i in into is it its me my of on
or our so that the this to we what when with you your add make need needs want should please fix
new use using get""".split())
# Small synonym map so a plain problem statement reaches the tag words.
SYNONYMS = {
    "pr": ["pull", "request", "commit", "review"], "db": ["database", "postgres", "sql"],
    "postgres": ["database", "sql", "migration"], "ui": ["frontend", "design", "interface"],
    "screen": ["ui", "frontend"], "page": ["frontend", "web", "ui"], "money": ["payment", "billing", "charge"],
    "payment": ["billing", "charge", "money"], "charge": ["payment", "billing"],
    "deploy": ["release", "rollback", "ci"], "test": ["testing"], "tests": ["testing"],
    "bug": ["debug", "fix"], "slow": ["performance", "speed"], "auth": ["authentication", "security", "token"],
    "secret": ["secrets", "env", "security"], "post": ["publish", "social", "content"],
    "email": ["outreach", "send"], "llm": ["model", "ai", "prompt"], "animation": ["motion"],
    "go": ["golang"], "golang": ["go"], "a11y": ["accessibility", "wcag"],
}
CAT_SEEDS = {
    1: "code test testing debug deploy ci backend api database sql security git review refactor build server infra docker go python lint",
    2: "payment billing invoice finance legal contract privacy gdpr sales pricing money ledger tax compliance",
    3: "marketing seo content social campaign research competitor customer support growth newsletter brand",
    4: "meeting docs document planning plan slides deck notes calendar task project hiring knowledge memo",
    5: "ui frontend design css react animation motion mobile ios android image video audio voice accessibility",
}


def tokens(text):
    out = []
    for w in re.findall(r"[a-z0-9][a-z0-9+#]*", text.lower()):
        if w in STOP:
            continue
        out.append(stem(w))
    return out


def stem(w):
    for suf in ("ing", "ies", "es", "ed", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)] + ("y" if suf == "ies" else "")
    return w


def query_terms(problem):
    base = tokens(problem)
    terms = Counter(base)
    for w in base:
        for s in SYNONYMS.get(w, []):
            terms[stem(s)] += 0.5
    return terms


def load_index(path):
    data = json.loads(Path(path).read_text())
    return data["records"]


def record_fields(r):
    name = set(tokens(r["name"].replace("-", " ").replace(":", " ")))
    area = set(tokens(r.get("area") or "")) | set(tokens(r.get("category_name", "")))
    kw = set(r.get("keywords") or [])
    return name, area, kw


def pass1(records, problem, limit=25, category=None, area=None, include_reference=False, kind=None):
    """Zero-token filter. Returns up to `limit` candidates, best first, one per skill name."""
    q = query_terms(problem)
    scored = []
    for r in records:
        if "not-a-skill" in r["tags"]:
            continue
        if r["status"] == "quarantined" and not include_reference:
            continue
        if category and r["category"] != int(category):
            continue
        if area and area.lower() not in (r.get("area") or "").lower():
            continue
        if kind and r["kind"] != kind:
            continue
        name, ar, kw = record_fields(r)
        score = sum(w * (3 if t in name else 2 if t in ar else 1 if t in kw else 0) for t, w in q.items())
        if score > 0:
            scored.append((score, r))
    scored.sort(key=lambda x: (-x[0], x[1]["precedence"], x[1]["name"], x[1]["id"]))
    best, seen = [], set()
    for score, r in scored:
        if r["name"] in seen:  # the same skill from a lower-precedence source
            continue
        seen.add(r["name"])
        best.append(dict(r, score=round(score, 2)))
        if len(best) >= limit:
            break
    return best


def bm25(candidates, problem, all_records, k1=1.2, b=0.75):
    """Local fallback for pass 2. IDF comes from the whole index so scores are stable."""
    docs = [tokens(f'{r["name"].replace("-", " ")} {r["description"]} {" ".join(r.get("keywords") or [])}')
            for r in all_records]
    df = Counter(t for d in docs for t in set(d))
    n = len(docs) or 1
    avg = sum(len(d) for d in docs) / n
    q = query_terms(problem)
    out = []
    for r in candidates:
        d = tokens(f'{r["name"].replace("-", " ")} {r["description"]} {" ".join(r.get("keywords") or [])}')
        tf = Counter(d)
        s = 0.0
        for t, w in q.items():
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            s += w * idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avg))
        out.append((s, r))
    out.sort(key=lambda x: (-x[0], x[1]["precedence"], x[1]["name"]))
    return [dict(r, bm25=round(s, 3)) for s, r in out]


def ranking_prompt(problem, candidates, top):
    lines = [f"Task: {problem.strip()}",
             f"Pick the {top} skills below that most help with this task. Reply with their names only, best first, one per line.",
             "If two say the same thing, prefer the lower precedence number (house 2, library 3, other 4).", ""]
    for i, r in enumerate(candidates, 1):
        lines.append(f'{i}. {r["name"]} (p{r["precedence"]}): {r["description"][:160]}')
    return "\n".join(lines)


def where(r, roots):
    base = roots.get(r["source"])
    if base and r.get("load"):
        return str(Path(base) / r["load"])
    return f'{r["source"]}:{r.get("load") or r["name"]}'


def sweep(records, limit=50):
    """Second cheap pass: looser matching (prefixes, seeds plus confident records) for misfiled skills."""
    lex = defaultdict(Counter)
    for c, seed in CAT_SEEDS.items():
        for t in tokens(seed):
            lex[c][t[:5]] += 3
    for r in records:
        if r["confidence"] == "high" and r["category"] in CAT_SEEDS:
            for t in tokens(f'{r["name"].replace("-", " ")} {r.get("area") or ""}'):
                lex[r["category"]][t[:5]] += 1
    totals = {c: sum(v.values()) or 1 for c, v in lex.items()}
    out = []
    for r in records:
        if "not-a-skill" in r["tags"] or not (r["category"] == 6 or r["confidence"] == "low"):
            continue
        pre = [t[:5] for t in tokens(f'{r["name"].replace("-", " ")} {r["description"]} {r.get("area") or ""}')]
        scores = {c: sum(1000 * lex[c][p] / totals[c] for p in pre) for c in lex}
        best = max(scores, key=scores.get)
        cur = scores.get(r["category"], 0.0)
        if best != r["category"] and scores[best] > 0 and scores[best] >= 1.5 * cur:
            out.append({"id": r["id"], "name": r["name"], "category": r["category"],
                        "suggested": best, "confidence": r["confidence"],
                        "score": round(scores[best], 1), "current_score": round(cur, 1)})
    out.sort(key=lambda x: -x["score"])
    return out[:limit]


def parse_roots(items):
    roots = {}
    for it in items or []:
        label, _, path = it.partition("=")
        roots[label] = os.path.expanduser(path)
    return roots


def main(argv=None):
    ap = argparse.ArgumentParser(description="Two-pass skill selector")
    ap.add_argument("problem", nargs="?", default="")
    ap.add_argument("--index", default=str(DEFAULT_INDEX))
    ap.add_argument("--category", type=int)
    ap.add_argument("--area")
    ap.add_argument("--kind", choices=["skill", "command"])
    ap.add_argument("--max", type=int, default=25, help="pass-1 candidates (20-30)")
    ap.add_argument("--top", type=int, default=3, help="skills to load (3-5)")
    ap.add_argument("--local", action="store_true", help="rank here with BM25 instead of printing a prompt")
    ap.add_argument("--include-reference", action="store_true", help="also show quarantined skills")
    ap.add_argument("--root", action="append", help="LABEL=DIR so load paths resolve, e.g. house=~/skills")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sweep-misfiled", action="store_true")
    a = ap.parse_args(argv)
    records = load_index(a.index)
    if a.sweep_misfiled:
        rows = sweep(records)
        if a.json:
            print(json.dumps(rows, indent=1))
        else:
            print(f"{len(rows)} likely misfiled (of Unmapped and low-confidence items):")
            for x in rows:
                print(f'  {x["name"]} [{x["id"].split(":")[0]}]: {x["category"]} -> {x["suggested"]} (score {x["score"]} vs {x["current_score"]})')
        return 0
    if not a.problem.strip():
        ap.error("give a problem statement, or --sweep-misfiled")
    cands = pass1(records, a.problem, max(1, min(a.max, 30)), a.category, a.area, a.include_reference, a.kind)
    top = max(1, min(a.top, 5))
    roots = parse_roots(a.root)
    if not a.local:
        prompt = ranking_prompt(a.problem, cands, top)
        if a.json:
            print(json.dumps({"prompt": prompt, "prompt_tokens_est": len(prompt) // 4,
                              "candidates": [{"name": r["name"], "load": where(r, roots)} for r in cands]}, indent=1))
        else:
            print(prompt)
            print("\n# load the picked ones from:")
            for r in cands:
                print(f'#   {r["name"]}: {where(r, roots)}')
        return 0
    ranked = bm25(cands, a.problem, records)[:top]
    rows = [{"name": r["name"], "status": r["status"], "precedence": r["precedence"],
             "load": where(r, roots), "bm25": r["bm25"]} for r in ranked]
    if a.json:
        print(json.dumps(rows, indent=1))
    else:
        print(f"{len(cands)} candidates after pass 1; top {len(rows)}:")
        for x in rows:
            print(f'  {x["name"]} ({x["status"]}, p{x["precedence"]}): {x["load"]}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
