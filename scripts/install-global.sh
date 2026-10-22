#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-auto}"
FORCE=0
case "${2:-}" in
  "") ;;
  --force) FORCE=1 ;;
  *) echo "Usage: $0 [auto|all|codex|claude|gemini] [--force]" >&2; exit 2 ;;
esac
# The PID keeps two runs in the same second from sharing a backup folder.
STAMP="$(date +%Y%m%d-%H%M%S)-$$"
# Lists every skill/agent path this pack installed into a host home; only these are replaced without --force.
LEDGER_NAME=".gridline.installed"
# Retain per-path ownership information from installations using the former brand.
LEGACY_LEDGER_NAME=".architect-agent-superpowers.installed"

SKILLS=()
for skill_dir in "$ROOT"/skills/*; do
  [ -f "$skill_dir/SKILL.md" ] && SKILLS+=("$(basename "$skill_dir")")
done

AGENTS=()
for agent_file in "$ROOT"/agents/*.md; do
  [ -f "$agent_file" ] && AGENTS+=("$(basename "$agent_file" .md)")
done

host_home() {
  case "$1" in
    codex) echo "${CODEX_HOME:-$HOME/.codex}" ;;
    claude) echo "$HOME/.claude" ;;
    gemini) echo "$HOME/.gemini" ;;
  esac
}

agent_source() {
  case "$1" in
    claude) echo "$ROOT/providers/claude/agents" ;;
    gemini) echo "$ROOT/agents" ;;
    *) echo "" ;;
  esac
}

# Prints "relative-destination<TAB>source" for everything a host receives.
entries() {
  local name src
  for name in "${SKILLS[@]}"; do printf 'skills/%s\t%s\n' "$name" "$ROOT/skills/$name"; done
  src="$(agent_source "$1")"
  if [ -n "$src" ]; then
    for name in "${AGENTS[@]}"; do printf 'agents/%s.md\t%s\n' "$name" "$src/$name.md"; done
  fi
}

owned() {
  local ledger="$1/$LEDGER_NAME"
  { [ -f "$ledger" ] && grep -Fxq "$2" "$ledger"; } || { [ -f "$1/$LEGACY_LEDGER_NAME" ] && grep -Fxq "$2" "$1/$LEGACY_LEDGER_NAME"; }
}

# Reports paths that exist but were not installed by this pack.
conflicts() {
  local home rel _src
  home="$(host_home "$1")"
  while IFS=$'\t' read -r rel _src; do
    if [ -e "$home/$rel" ] && ! owned "$home" "$rel"; then echo "$home/$rel"; fi
  done < <(entries "$1")
}

failed() {
  echo "$1: install stopped. $2 Items already replaced in this run stay updated and are listed in $3/$LEDGER_NAME; re-run to finish." >&2
  exit 1
}

# Each item is either its previous version or the new one, never missing: a failed step is undone before stopping.
install_host() {
  local host="$1" home backup rel src staged moved count=0 backed=0
  home="$(host_home "$host")"
  backup="$home/backups/gridline-$STAMP"
  while IFS=$'\t' read -r rel src; do
    mkdir -p "$(dirname "$home/$rel")"
    staged="$home/$rel.aas-new.$$"
    rm -rf "$staged"
    if ! cp -R "$src" "$staged"; then
      rm -rf "$staged"
      failed "$host" "Copying $rel failed; the installed $rel is unchanged." "$home"
    fi
    moved=0
    if [ -e "$home/$rel" ]; then
      mkdir -p "$(dirname "$backup/$rel")"
      if ! mv "$home/$rel" "$backup/$rel"; then
        rm -rf "$staged"
        failed "$host" "Backing up $rel failed; the installed $rel is unchanged." "$home"
      fi
      moved=1
    fi
    if ! mv "$staged" "$home/$rel"; then
      if [ "$moved" -eq 1 ]; then mv "$backup/$rel" "$home/$rel"; fi
      rm -rf "$staged"
      failed "$host" "Placing the new $rel failed; the previous $rel was put back." "$home"
    fi
    backed=$((backed + moved))
    echo "$rel" >> "$home/$LEDGER_NAME"
    count=$((count + 1))
  done < <(entries "$host")
  sort -u "$home/$LEDGER_NAME" > "$home/$LEDGER_NAME.tmp"
  mv "$home/$LEDGER_NAME.tmp" "$home/$LEDGER_NAME"
  echo "$host: installed $count items under $home"
  if [ "$backed" -gt 0 ]; then echo "$host: previous versions of $backed items moved to $backup"; fi
}

HOSTS=()
case "$TARGET" in
  auto)
    for host in codex claude gemini; do
      if command -v "$host" >/dev/null 2>&1; then HOSTS+=("$host"); else echo "$host: not installed, skipped"; fi
    done
    if [ "${#HOSTS[@]}" -eq 0 ]; then
      echo "No supported CLI runtime was detected. Install Codex, Claude Code, or Gemini CLI first, or choose an explicit target." >&2
      exit 3
    fi
    ;;
  codex|claude|gemini) HOSTS=("$TARGET") ;;
  all) HOSTS=(codex claude gemini) ;;
  *) echo "Usage: $0 [auto|all|codex|claude|gemini] [--force]" >&2; exit 2 ;;
esac

# Check every host before changing any of them.
FOUND=""
for host in "${HOSTS[@]}"; do FOUND+="$(conflicts "$host")"$'\n'; done
FOUND="$(printf '%s' "$FOUND" | sed '/^$/d')"
if [ -n "$FOUND" ] && [ "$FORCE" -ne 1 ]; then
  echo "These paths exist but were not installed by this installer, so nothing was changed:" >&2
  printf '%s\n' "$FOUND" | sed 's/^/  /' >&2
  echo "They may belong to another pack, or to an install made by a plugin manager or an installer older than 0.5.1." >&2
  echo "Re-run with --force to move them into a timestamped backup folder and replace them." >&2
  exit 4
fi

for host in "${HOSTS[@]}"; do install_host "$host"; done
echo "Installation complete. Start a fresh agent session (or use the provider's reload command) before verification."
