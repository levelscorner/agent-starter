# Start a new repo

## The one prompt

Give this to any agent:

> Create a private GitHub repo named `<name>`. Copy everything in agent-starter's `templates/repo/` into it. Then fill in README.md, AGENTS.md, STATE.md and docs/architecture.md for this project: `<one line on what it does>`. Replace every `<fill: ...>` marker. Commit as `chore: start from agent-starter template`.

## What the agent runs

```bash
gh repo create <name> --private --clone
cp -R agent-starter/templates/repo/. <name>/
cd <name>
# fill the files, then:
git add README.md AGENTS.md CLAUDE.md STATE.md docs/architecture.md archive/README.md
git commit -m "chore: start from agent-starter template"
git push -u origin main
```

## Why not GitHub's template button

GitHub's template feature copies the whole agent-starter repo, rules and skills included. A project only needs the small set of files in `templates/repo/`, and it reads the shared rules from agent-starter by link.

## After it exists

- Add the repo to your list of repos, with a link to its STATE.md.
- For cloud bots that read no files, add one standing instruction: "Before any job, read AGENTS.md in this repo."
