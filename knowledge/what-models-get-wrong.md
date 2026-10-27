# What models get wrong

Facts AI agents keep getting wrong about their own tools. One dated line each, with how we know. Newest first.

- **2026-10-27** rulesync's `init` writes `"delete": true` into its config by default. With delete on, a global sync removes every skill it did not create. Our configs set it to false. (seen: rulesync 43.1.1 init)
- **2026-10-27** rulesync cannot write user-level rules for Cursor or Hermes; it skips them with a warning. Cursor gets rules per repo; Hermes reads the repo's AGENTS.md. (seen: rulesync 43.1.1 output)
- **2026-10-26** Claude Code does not load AGENTS.md when a CLAUDE.md exists, unless CLAUDE.md imports it with `@AGENTS.md`. (research: code.claude.com/docs/en/memory)
- **2026-10-26** Hermes Agent loads `HERMES.md` or `.hermes.md` first and then skips AGENTS.md. Only one project context file loads. (research: hermes-agent.nousresearch.com docs, context files)
- **2026-10-26** Cursor reads skills from `.cursor/skills`, `.agents/skills` and `.claude/skills`. Grok Build reads `.grok/skills` and `~/.agents/skills`. (research: cursor.com/docs, docs.x.ai/build)
- **2026-10-26** ChatGPT dots and Grok Bot read no instruction file. They take a standing instruction in their settings. (research: learn.chatgpt.com/docs/dots, docs.x.ai/grok-bot)
- **2026-10-26** GitHub's template button copies the whole repo. To start a project with only a few files, copy a folder instead. (research: GitHub docs)
