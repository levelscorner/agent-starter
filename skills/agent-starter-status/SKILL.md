---
name: agent-starter-status
description: Use when asked whether this machine's agents have the current shared rules and skills, or after editing anything in agent-starter.
---

# Check agent-starter status

1. In the agent-starter folder, run `bash scripts/status.sh`.
2. Report the result in this shape:

```
ALLOW: up to date            (or)            BLOCK: <N> files out of date
- missing: ~/<path>
- changed: ~/<path>
Fix: bash scripts/sync.sh
```

3. Lead with ALLOW or BLOCK. List at most 5 files and say how many more.
4. If the script cannot run, say "not checked" and why. Never report "up to date" without running it.

The script changes nothing. It syncs into a scratch folder and compares that with the real home folder.
