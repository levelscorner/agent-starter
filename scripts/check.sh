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
