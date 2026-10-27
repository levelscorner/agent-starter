# Git

## Commits

- Format: `<type>: <description>`. Types: feat, fix, refactor, docs, test, chore, perf, ci.
- Name the files you add. Never `git add -A` or `git add .`: they sweep in generated files and other people's work.
- One idea per commit. One change per pull request.

## Pull requests

- Say what changed, why, and how it was checked (the command and its result).
- A change that alters behaviour updates its document in the same PR.
- List what the change could make wrong in an `invalidates:` line: docs, public pages, other repos. Write `invalidates: none` after checking.
- Before merge, run the speed check in [how-we-code.md](how-we-code.md).

## Never delete

- Nothing is deleted. A retired file moves to `archive/` with a one-line note at the top saying where its content went.
- Git keeps every old version anyway. Moving keeps the history easy to find.
- Never force-push a shared branch. Never rewrite published history.

## Branches

- Work on a branch, never directly on the main or default branch.
- Keep a branch short-lived. Merge or close it.

## Tasks and handoffs

- A task lives in a GitHub issue. Take it by adding the label `in-progress` and a comment: `claimed by <tool> <session>`.
- Release it when the PR merges, or after 24 hours with no update anyone may take it.
- A handoff is a comment on that issue: what is done, what is left, what to watch out for.
