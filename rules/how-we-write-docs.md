---
root: false
targets: ["*"]
description: "Every doc gets an agent header and an index line (OKF v0.2); every plan gets an HTML page"
globs: ["**/*.md"]
cursor:
  alwaysApply: true
---

# How we write docs

Every doc has two readers: an agent and the owner. The agent needs a short header and an index it can read in one step. The owner needs a visual page. This applies to every repo and every new or changed `.md` file in a docs folder: plans, designs, research, decisions, notes, teaching notes, memory notes.

The agent format is Google Cloud's Open Knowledge Format (OKF) v0.2: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md

## 1. Every doc starts with a header

```markdown
---
type: Plan
title: Never lose data
description: How every saved file gets a second copy within an hour, and how we prove it.
status: stable
---
# Never lose data
```

- `type`, `title` and `description` are required. `description` is one sentence: what the doc is, in plain words.
- `type` is a short noun people would use: Plan, Decision, Research, Design, Design Note, Teaching Note, Audit, Memory, Folder Guide. Use the type the folder already uses.
- `status` is `draft`, `stable` or `deprecated`. Leave it out for `stable`. Mark a replaced doc `deprecated`; do not delete it.
- The header keys must be at the top level. A `type` nested under another key does not count.
- Extra keys are allowed. Two we use:
  - `page:` the link to the owner's HTML page for this doc (section 3).
  - `verified: { by: human:<github-name>, at: 2026-11-17T12:00:00Z }` when the owner has read and approved it.

## 2. Every folder has an index.md

- `index.md` lists every doc in the folder as `* [Title](file.md) - description`, grouped by `type`, then the sub-folders. Agents read it first and open only what they need.
- Never edit `index.md` by hand. Run `python3 scripts/okf_index.py` after adding or changing a doc, and commit the index with the doc.
- `python3 scripts/okf_index.py --check` fails on a missing header or an out-of-date index. Every repo runs it in its checks and CI.
- `python3 scripts/okf_index.py --add-headers` fills missing headers from the folder, first heading and first line. Read what it wrote before you commit.
- A repo says which folders are docs in `okf.toml` (`bundles`, `skip`, `exempt`, `[types]`). `also_read_under = "metadata"` is only for folders whose header a tool rewrites (Claude Code's memory writer moves extra keys under `metadata:`); such a folder may also set `required = ["type", "description"]` so the title comes from the file name. The script is `scripts/okf_index.py` in agent-starter; copy it, do not fork it.
- `README.md` stays the human front page of a folder. `index.md` is the agent list. Both can exist.
- `AGENTS.md` points agents to the root `index.md`.

## 3. Every plan, idea and discussion gets an HTML page

- The `.md` is for agents and for the record. The owner reads the HTML page.
- A plan, design, research summary or decision also gets a visual page (a private Artifact or a kit page), linked in the doc's `page:` key and in its PR.
- A whole docs folder can be seen as one map: OKF's `visualize` command turns a folder into one HTML file with every doc and its links.

## 4. Done means

- The header is there, the index is current, `--check` passes.
- A plan, design or decision has its `page:` link.
- The PR description says which docs it added or changed.
