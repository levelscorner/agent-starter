#!/usr/bin/env bash
# Says whether this machine has the current agent-starter rules and skills.
# It syncs into a scratch folder and compares that with your real home folder.
# Prints UP TO DATE or OUT OF DATE, then one line per file that differs. Changes nothing.
set -u
cd "$(dirname "$0")/.."

real_home="$HOME"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

if ! HOME="$scratch" npx --no-install rulesync generate -s >/dev/null 2>&1; then
  echo "OUT OF DATE: could not run rulesync here (run npm install first)"
  exit 2
fi

stale=0
while IFS= read -r f; do
  rel="${f#"$scratch"/}"
  if [ ! -f "$real_home/$rel" ]; then
    echo "missing:  ~/$rel"; stale=$((stale + 1))
  elif ! cmp -s "$f" "$real_home/$rel"; then
    echo "changed:  ~/$rel"; stale=$((stale + 1))
  fi
done < <(cd "$scratch" && find .claude .codex .agents .cursor .grok .hermes -type f 2>/dev/null | sed "s#^#$scratch/#")

if [ "$stale" -eq 0 ]; then
  echo "UP TO DATE: every tool has the current rules and skills"
  exit 0
fi
echo "OUT OF DATE: $stale file(s). Run: bash scripts/sync.sh"
exit 1
