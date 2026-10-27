---
name: agent-starter-onboard
description: Use when setting up agent-starter on a new machine, in a new repo, or for a cloud bot that reads no files.
---

# Set up agent-starter

Pick the case that matches, and do only those steps.

## A new machine

1. Clone agent-starter and run `npm install` inside it.
2. Run `bash scripts/status.sh` to see what is missing or old.
3. Run `npx rulesync generate`. It writes the shared rules and skills into each tool's user folder and never deletes anything it did not make.
4. Run `bash scripts/status.sh` again. It must print `UP TO DATE`.

## A new repo

1. Follow `NEW-REPO.md`: create the repo, copy `templates/repo/`, fill every `<fill: ...>` marker.
2. For Cursor, run `npx rulesync generate -c rulesync.cursor.jsonc -o <path to the repo>` and commit `.cursor/rules/`.

## An existing repo

1. Read its current `AGENTS.md`, `CLAUDE.md` and any tool-specific file (for example `HERMES.md`).
2. Keep its content. If `CLAUDE.md` holds rules, move them into `AGENTS.md` and make `CLAUDE.md` the one line `@AGENTS.md`.
3. A `HERMES.md` or `.hermes.md` hides `AGENTS.md` from Hermes. Move it to `docs/agents/hermes-brief.md` and link it from `AGENTS.md`. Never delete it.
4. Add `STATE.md` and `docs/architecture.md` from `templates/repo/` if missing.

## A cloud bot that reads no files

Grok Bot, ChatGPT dots and similar take a standing instruction instead. Add this once, in the bot's settings:

> Before any job, read AGENTS.md in the repo you are working on, and follow the rules it links to.

## Done when

- `bash scripts/status.sh` prints `UP TO DATE`.
- Every repo opens with README.md, AGENTS.md, a one-line CLAUDE.md and STATE.md.
