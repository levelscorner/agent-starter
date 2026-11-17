---
root: false
targets: ["*"]
description: "How we look things up and cite them"
globs: ["**/*"]
cursor:
  alwaysApply: true
---

# How we research

For any answer that depends on looking something up: docs, prices, repos, papers, videos, competitors.

## The rules

1. **A failed source is "not checked", never "nothing found".** If a site was down, rate-limited or needed a login, say so. Silence from a broken source is not evidence.
2. **Every source shows its date.** The date it was published or last updated, and the date you read it. An old saved finding keeps its old date and is never presented as new.
3. **Never guess or rebuild a URL.** Cite only links you actually opened. If you lost the link, say "source not kept".
4. **Read a full source only to settle a specific doubt.** Summaries and search results are fine for orientation. Open the full text when a conclusion depends on one claim.
5. **Video claims carry a timestamp** as `MM:SS`. Sampling tools can miss fast cuts, so say how the video was read.
6. **Read what is already written before writing your own.** Before drafting a checklist, a standard, a design or advice, search the installed skills and the repo's docs for it. In Claude Code: `find ~/.claude/skills ~/.claude/plugins -name SKILL.md`, then read the ones whose description fits. Build from them and name each one you used. Where a skill disagrees with the repo's rules, say so; the repo wins. Do this at the start of a task and when the problem changes, not on every reply.
7. **Ask the question under an either/or.** Before offering "A or B?", write the need both options serve ("what must stay safe?"). If both can be true for different jobs, say that instead of making the reader pick.

## How to report

- Lead with the answer, then the evidence.
- Label each claim: measured, seen, research (link and date), guess, or not known. See [how-we-talk](https://github.com/levelscorner/agent-starter/blob/main/rules/how-we-talk.md).
- Prefer the primary source (the vendor's docs, the repo, the paper) over a blog about it.
- Numbers come with where they came from. A number without a source is a guess.
- If two sources disagree, show both and say which you trust and why.

## Tools change fast

- Before saying a tool "can" or "cannot" do something, check its current docs. Models carry stale facts.
- When you find a fact models keep getting wrong, add a dated line to [what-models-get-wrong.md](https://github.com/levelscorner/agent-starter/blob/main/knowledge/what-models-get-wrong.md) in agent-starter.

## Credits

In our own words, after [last30days](https://github.com/mvanhorn/last30days-skill) (MIT), the [Perplexity MCP server](https://github.com/perplexityai/modelcontextprotocol) (MIT), [Firecrawl's research skills](https://github.com/firecrawl/cli) and [Google's Gemini video docs](https://ai.google.dev/gemini-api/docs/video-understanding).
