# agent-starter

One set of rules and skills that every AI coding agent can follow: Claude Code, Codex, Cursor, Grok, Hermes, and the next one.

Write a rule once here. A sync tool (rulesync) turns it into each agent's own file. A new repo starts from the template, so every repo opens the same way for a person and for an agent.

## Who it is for

- People who use more than one AI agent and are tired of each one behaving differently.
- New teammates, human or AI, who need to know how to work in a repo on day one.

## Use it in 5 steps

1. Copy `templates/repo/` into your repo, or create a new repo from this template (see `NEW-REPO.md`).
2. Fill in `README.md`, `AGENTS.md` and `STATE.md` for your project.
3. Install rulesync: `npm install` in this repo (the version is pinned).
4. Run `npx rulesync generate` to write each agent's files (see "Sync your tools" below).
5. For cloud bots that read no files (Grok Bot, ChatGPT dots), add one standing instruction: "Before any job, read AGENTS.md in this repo."

## What is in here

| Folder | What it holds | When an agent reads it |
|---|---|---|
| `rules/` | Short house rules: how we talk, code, research, use git, stay safe | Every time |
| `skills/` | Longer guides that load when a task needs them | When the task matches |
| `templates/repo/` | The files every repo starts with | When a repo is created |
| `knowledge/` | Dated corrections agents keep getting wrong | When the topic comes up |
| `.rulesync/` | The sync tool's config | When you run the sync |
| `scripts/check.sh` | Checks this repo is complete and has nothing private in it | Before every commit |

## Sync your tools

```bash
npm install
npx rulesync generate
```

This writes `CLAUDE.md` and `.claude/skills/` for Claude Code, `AGENTS.md` and `.agents/skills/` for Codex, Cursor, Grok and Hermes, `.cursor/rules/` for Cursor and `.grok/` for Grok Build.

Never run rulesync with `--delete` in global mode. It removes every skill it did not create.

## Rules of this repo

- Plain words. Short sentences. No em dashes.
- Nothing private ever goes in. `scripts/check.sh` fails on private paths and secret patterns.
- Skills from other projects keep their licence and are listed in `skills/CREDITS.md`.

## Licence

MIT for our own text. Each copied skill keeps its own licence (see `skills/CREDITS.md`).
