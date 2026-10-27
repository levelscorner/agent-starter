# How we code

Keep it simple. The best code is code nobody had to write. Technical depth is fine where the product needs it, but explain it as simply as the topic allows.

## 1. Think before you write

- Say your assumptions. If something is unclear, stop and ask one question.
- If there are two readings of the task, show both. Do not pick one silently.
- If a simpler approach exists, say so, even if it was not asked for.

## 2. The smallest complete change

Take the first option that fully works:

1. Does it need to exist at all? Skip features nobody asked for and name them in one line.
2. Is it already in this codebase? Use it the way the code around it does.
3. Does the standard library or platform do it? Use that.
4. Does an installed package do it? Use it. Never add a package for a few lines.
5. Can it be one clear line? One line.
6. Otherwise, the least code that works.

- Finish every part the change needs: callers, tests, fixtures, config.
- No wrappers, options or "for later" code nobody asked for.
- A shortcut with a known limit gets a comment: `shortcut: <the limit>, <when to upgrade>`.

**Never cut:** input checks at trust boundaries, error handling that prevents data loss, security, accessibility, anything the user asked for.

## 3. Change only what you must

- Every changed line traces back to the request.
- Do not reformat, rename or "improve" code next to your change. Mention it instead.
- Remove only what your change made unused.
- Show only the changed lines plus a little context when you report a change.

## 4. Work to a goal you can check

- Turn the task into a check: "fix the bug" becomes "a test that fails before and passes after".
- No "done" without fresh evidence: the command you ran and what it printed.
- "Done, not verified" is a different report from "done". Say which.

## 5. Bugs

- Before editing, find every caller of the code you touch. Fix the root cause once, in the shared code.
- After **2 failed fixes** that rest on the same belief, stop. Write the belief as a sentence that could be false, test it, and only then try a third fix.

## 6. Speed: check it before every merge

For every loop, query, regex and parser a change touches:

- Name the input that grows and its worst case. If a user controls it, cap it where it comes in.
- No worse than linear in that input, or the PR says why.
- No query inside a loop. Batch it.
- No regex with nested or back-to-back `+` or `*` over user text.
- No unbounded parse of user input: YAML aliases, JSON depth, archive size.
- No blocking work in async code: sync database calls, password hashing, large file reads.
- **Prove it, do not argue it.** Time the path at n, 2n and 4n. Linear doubles; quadratic quadruples.
- Report a timing with what you measured, what limited it, and how much it varied between runs. One run each side proves nothing.

## Excuses and their answers

| Excuse | Answer |
|---|---|
| "I'm confident it works" | Confidence is not evidence. Show the run. |
| "It's a tiny change, no test needed" | Tiny changes break things too. One small test. |
| "I'll clean it up later" | Write the `shortcut:` comment now, or do it now. |
| "The reviewer will catch it" | You are the first reviewer. |
| "It's probably linear" | Time it at n, 2n, 4n. |
| "This abstraction will help later" | Later can add it. Delete it now. |

## Credits

In our own words, after [Andrej Karpathy's coding guidelines](https://github.com/forrestchang/andrej-karpathy-skills), [ponytail](https://github.com/DietrichGebert/ponytail) (MIT), [superpowers](https://github.com/obra/superpowers) (MIT), [gstack](https://github.com/garrytan/gstack) (MIT) and [caveman](https://github.com/JuliusBrussee/caveman) (Apache-2.0).
