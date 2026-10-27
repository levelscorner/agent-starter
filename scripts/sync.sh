#!/usr/bin/env bash
# Writes the shared rules and skills into each tool's user folder.
# It never overwrites a file silently: it lists what would change and stops.
# Run again with --yes to back up those files to ~/.agent-starter-backup/<time>/ and sync.
set -u
cd "$(dirname "$0")/.."

real_home="$HOME"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

HOME="$scratch" npx --no-install rulesync generate -s >/dev/null 2>&1 \
  || { echo "Could not run rulesync (run npm install first)"; exit 2; }

changed=()
while IFS= read -r rel; do
  [ -f "$real_home/$rel" ] && ! cmp -s "$scratch/$rel" "$real_home/$rel" && changed+=("$rel")
done < <(cd "$scratch" && find .claude .codex .agents .cursor .grok .hermes -type f 2>/dev/null)

if [ "${#changed[@]}" -gt 0 ] && [ "${1:-}" != "--yes" ]; then
  echo "STOPPED: the sync would overwrite ${#changed[@]} file(s) you already have:"
  printf '  ~/%s\n' "${changed[@]:0:5}"
  [ "${#changed[@]}" -gt 5 ] && echo "  ...and $(( ${#changed[@]} - 5 )) more"
  echo "Move anything you want to keep into agent-starter's rules first."
  echo "Then run: bash scripts/sync.sh --yes  (backs them up before overwriting)"
  exit 1
fi

if [ "${#changed[@]}" -gt 0 ]; then
  backup="$real_home/.agent-starter-backup/$(date +%Y%m%d-%H%M%S)"
  for rel in "${changed[@]}"; do
    mkdir -p "$backup/$(dirname "$rel")"
    cp -p "$real_home/$rel" "$backup/$rel"
  done
  echo "Backed up ${#changed[@]} file(s) to $backup"
fi

npx --no-install rulesync generate -s && echo "Synced. Check with: bash scripts/status.sh"
