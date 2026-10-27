# How to work in agent-starter

Read this first. It is a table of contents, not the whole book.

## Always follow

- [rules/how-we-talk.md](rules/how-we-talk.md): how to talk to people
- [rules/how-we-code.md](rules/how-we-code.md): how to write and change code
- [rules/how-we-research.md](rules/how-we-research.md): how to look things up and cite them
- [rules/git.md](rules/git.md): commits, pull requests, never deleting
- [rules/security.md](rules/security.md): secrets, input, public versus private

## Load when the task needs it

- [skills/](skills/): one folder per skill, each with a `SKILL.md`. Credits in [skills/CREDITS.md](skills/CREDITS.md).
- [knowledge/what-models-get-wrong.md](knowledge/what-models-get-wrong.md): dated corrections.

## Working in this repo

1. This repo is public. Nothing private goes in: no personal notes, no private repo names, no keys.
2. Run `bash scripts/check.sh` before every commit. It must print `PASS`.
3. A rule file stays at 120 lines or fewer. If it needs more, it is a skill.
4. A copied skill keeps its text. Our changes to it are listed in `skills/CHANGES.md`.
5. Templates in `templates/repo/` use `<fill: ...>` markers for the parts a new repo writes.
