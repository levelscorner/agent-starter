#!/usr/bin/env bash
# Checks that agent-starter is complete and safe to publish.
# Exit 0 when every check passes; prints one line per failure otherwise.
set -u
cd "$(dirname "$0")/.."

fails=0
fail() { echo "FAIL: $*"; fails=$((fails + 1)); }

# Files we write ourselves (third-party skills keep their own text).
own_files() {
  ls README.md AGENTS.md NEW-REPO.md 2>/dev/null
  find rules templates knowledge -type f -name '*.md' 2>/dev/null
}

# --- Root files ---
for f in README.md AGENTS.md CLAUDE.md LICENSE .gitignore; do
  [ -f "$f" ] || fail "missing $f"
done
[ "$(cat CLAUDE.md 2>/dev/null)" = "@AGENTS.md" ] || fail "CLAUDE.md must be exactly @AGENTS.md"

# --- Rules: present, short, linked from AGENTS.md ---
for r in how-we-talk how-we-code how-we-research git security; do
  f="rules/$r.md"
  if [ ! -f "$f" ]; then fail "missing $f"; continue; fi
  lines=$(wc -l < "$f" | tr -d ' ')
  [ "$lines" -le 120 ] || fail "$f has $lines lines (max 120)"
  grep -q "($f)" AGENTS.md || fail "AGENTS.md does not link $f"
done

# --- Skills: front matter and a credit line each ---
for s in i-have-adhd antislop antislop-code antislop-copywriting antislop-human \
         antislop-layoutmobile antislop-ui karpathy-coding emil-design-eng break-ui find-skills \
         agent-starter-onboard agent-starter-status; do
  [ -d "skills/$s" ] || fail "missing skill folder skills/$s"
done
for d in skills/*/; do
  [ -d "$d" ] || continue
  s=$(basename "$d")
  f="$d/SKILL.md"
  if [ ! -f "$f" ]; then fail "missing $f"; continue; fi
  head -20 "$f" | grep -q '^name:' || fail "$f has no name: front matter"
  head -20 "$f" | grep -q '^description:' || fail "$f has no description: front matter"
  grep -q "| $s |" skills/CREDITS.md 2>/dev/null || fail "skills/CREDITS.md has no row for $s"
done
[ -f skills/CHANGES.md ] || fail "missing skills/CHANGES.md"

# --- Repo template and the one prompt ---
for f in README.md AGENTS.md CLAUDE.md STATE.md docs/architecture.md archive/README.md; do
  [ -f "templates/repo/$f" ] || fail "missing templates/repo/$f"
done
[ "$(cat templates/repo/CLAUDE.md 2>/dev/null)" = "@AGENTS.md" ] || fail "templates/repo/CLAUDE.md must be exactly @AGENTS.md"
grep -q 'agent-starter' templates/repo/AGENTS.md 2>/dev/null || fail "templates/repo/AGENTS.md must point to agent-starter rules"
[ -f NEW-REPO.md ] || fail "missing NEW-REPO.md"
grep -q 'gh repo create' NEW-REPO.md 2>/dev/null || fail "NEW-REPO.md must show the gh repo create command"
grep -q 'templates/repo' NEW-REPO.md 2>/dev/null || fail "NEW-REPO.md must copy templates/repo"

# --- Dated corrections: every entry starts with a date ---
k=knowledge/what-models-get-wrong.md
if [ -f "$k" ]; then
  undated=$(grep -E '^- ' "$k" | grep -v -E '^- \*\*[0-9]{4}-[0-9]{2}-[0-9]{2}\*\*' | head -1)
  [ -z "$undated" ] || fail "$k has an undated entry: $undated"
else
  fail "missing $k"
fi
[ -f scripts/status.sh ] || fail "missing scripts/status.sh"

# --- rulesync: pinned, never deletes, generates for every tool ---
grep -q '"rulesync": "[0-9]' package.json 2>/dev/null || fail "rulesync must be pinned to an exact version in package.json"
for c in rulesync.jsonc rulesync.cursor.jsonc; do
  grep -q '"delete": false' "$c" 2>/dev/null || fail "$c must set \"delete\": false"
done
if [ "${SKIP_SYNC:-0}" != "1" ] && [ -d node_modules/rulesync ]; then
  home=$(mktemp -d); repo=$(mktemp -d)
  printf 'keep me\n' > "$repo/AGENTS.md"
  HOME="$home" npx --no-install rulesync generate -s >/dev/null 2>&1 || fail "rulesync global generate failed"
  for p in .claude/CLAUDE.md .claude/rules/how-we-talk.md .claude/skills/i-have-adhd/SKILL.md \
           .codex/AGENTS.md .agents/skills/antislop/SKILL.md .grok/AGENTS.md .grok/skills/karpathy-coding/SKILL.md \
           .cursor/skills/find-skills/SKILL.md .hermes/skills/break-ui/SKILL.md; do
    [ -e "$home/$p" ] || fail "rulesync did not write ~/$p"
  done
  npx --no-install rulesync generate -s -c rulesync.cursor.jsonc -o "$repo" >/dev/null 2>&1 || fail "rulesync cursor generate failed"
  [ -f "$repo/.cursor/rules/how-we-talk.mdc" ] || fail "rulesync did not write .cursor/rules/how-we-talk.mdc"
  [ "$(cat "$repo/AGENTS.md")" = "keep me" ] || fail "rulesync cursor run changed the repo's AGENTS.md"
  # status.sh: up to date right after a sync, out of date after a source edit
  HOME="$home" bash scripts/status.sh >/dev/null 2>&1 || fail "status.sh says out of date right after a sync"
  printf '\n' >> "$home/.claude/skills/antislop/SKILL.md"
  HOME="$home" bash scripts/status.sh >/dev/null 2>&1 && fail "status.sh missed a changed skill"
  rm -rf "$home" "$repo"
elif [ "${SKIP_SYNC:-0}" != "1" ]; then
  fail "run npm install first (or SKIP_SYNC=1)"
fi

# --- No em dashes in our own writing ---
while IFS= read -r f; do
  grep -q $'\xe2\x80\x94' "$f" && fail "em dash in $f"
done < <(own_files)

# --- Nothing private or secret anywhere (public repo) ---
private_hits=$(grep -rIl -E '/Users/|~/ws/|mycdb|nvapi-|sk-[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}' \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.superpowers --exclude=check.sh . 2>/dev/null)
[ -z "$private_hits" ] || fail "private path or secret in: $(echo $private_hits)"

if [ "$fails" -eq 0 ]; then echo "PASS: all checks"; exit 0; fi
echo "$fails check(s) failed"; exit 1
