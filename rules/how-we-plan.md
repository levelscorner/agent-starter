---
root: false
targets: ["*"]
description: "Every new feature gets the six documents and one checklist, before code"
globs: ["**/*"]
cursor:
  alwaysApply: true
---

# How we plan a feature

This applies to every new feature, in every repo and every session. It applies whether the owner or the agent suggests the feature.

## 1. The block, in order

1. **Triage.** Read the six documents that already exist for this area first. Then decide priority, size, what it depends on, and the code it touches. Check the code; do not guess.
2. **The six documents.** Write or update each one (section 2).
3. **The checklist.** Write the tasks, with details (section 3).
4. **Code.** Start only after the owner approves the documents.

Every later triage of the same feature starts again at step 1: read the documents, then update them.

## 2. The six documents

| # | Document | What it answers |
|---|---|---|
| 1 | Product requirements | What the user gets and why. What is out of scope. |
| 2 | Technical design (HLD + LLD) | High level: the parts and how they talk. Low level: modules, files, functions, data types, how the code is structured. Decisions that outlive the feature become an ADR. |
| 3 | App flow | Each screen and step the user goes through, including errors. |
| 4 | Design brief | How it looks: layout, states, copy. |
| 5 | Backend schema | What is stored, where, its shape, and the migration. |
| 6 | Implementation plan | The PRs in order, the tests, and the speed check for each PR. |

- Every feature lists all six. If one does not change, write one line saying "no change" and why. Never skip one silently.
- Put the six in one folder per feature, named `plans/<date>-<feature>/`, in the repo that holds the project's docs. If the project has no docs repo yet, ask where.
- The folder's `README.md` holds the triage table: each document, its state before, and what changed.

## 3. The checklist: one place

- The checklist lives in that feature's `README.md`. It is the only list for the feature. Do not copy it into issues, chat or other files; link to it.
- Each item says what to do, which file or document it touches, and how we know it is done.
- When a task is added, removed or changes, edit the checklist first, then do the work.
- Tick items as they finish, so progress is visible.

## 4. Keep them true

- A PR that changes behaviour names the documents it changes in its `invalidates:` line, and updates them in the same PR.
- When the feature ships, mark the folder shipped. Do not leave a plan that says "to do" for work that is done.

## 5. Names

Name every feature, module and tool in plain English that says what it does (for example "Upload guard", not a coined or non-English word).
