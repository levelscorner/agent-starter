---
name: karpathy-coding
description: Use when writing, reviewing or refactoring code, before the first edit, to keep changes small, simple and checkable.
---

# Karpathy coding

Four habits that stop the most common mistakes an AI makes when it writes code. Adapted from [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills), which collects Andrej Karpathy's observations and is released under the MIT licence (declared in its README and plugin file). Its MIT notice is in this folder's `LICENSE`.

## 1. Think before coding

- Say what you assume. If you are not sure, ask one question before writing.
- If the request can be read two ways, show both readings and let the person pick.
- If a simpler way exists than the one asked for, say so before building the harder one.
- If something is confusing, stop and name what is confusing.

## 2. Simplicity first

- Write the least code that solves the problem. Nothing for later, nothing "just in case".
- No abstraction for code used once. No option nobody asked for. No error handling for things that cannot happen.
- Test: would a senior engineer call this overcomplicated? If yes, cut it down. If 200 lines could be 50, rewrite it.

## 3. Surgical changes

- Touch only what the request needs.
- Do not reformat, rename or "improve" nearby code. Match the existing style even if you would do it differently.
- If you see dead code that is not yours, mention it. Do not delete it.
- Remove only the imports, variables and functions your own change made unused.
- Every changed line should trace back to the request.

## 4. Goal-driven execution

Turn the task into something you can check, then loop until it passes:

| Task as asked | Task as a checkable goal |
|---|---|
| "Add validation" | Tests for bad input fail first, then pass |
| "Fix the bug" | A test reproduces the bug, then passes |
| "Refactor X" | The same tests pass before and after |

For work with several steps, write the plan as steps with a check each:

```
1. <step>  → check: <how you will know it worked>
2. <step>  → check: <...>
```

A clear check lets you keep going without asking. A vague goal ("make it work") means you will keep needing to ask.

## When to relax

For a one-line, obvious change, use judgment. These habits are for anything with a chance of going wrong.
