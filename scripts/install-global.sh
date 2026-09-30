#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-all}"
STAMP="$(date +%Y%m%d-%H%M%S)"
SKILLS=(architecture-orchestrator architecture-programming site-regulation-research concept-design-review cad-bim-automation drawing-qa area-quantity-audit presentation-review architecture-red-team)
AGENTS=(architect-lead site-code-researcher design-critic bim-automation-specialist drawing-reviewer quantity-auditor)

copy_skills() {
  local dest="$1" backup="$2"
  mkdir -p "$dest" "$backup"
  for name in "${SKILLS[@]}"; do
    if [ -e "$dest/$name" ]; then cp -R "$dest/$name" "$backup/$name"; rm -rf "$dest/$name"; fi
    cp -R "$ROOT/skills/$name" "$dest/$name"
  done
}

copy_agents() {
  local src="$1" dest="$2" backup="$3"
  mkdir -p "$dest" "$backup"
  for name in "${AGENTS[@]}"; do
    if [ -e "$dest/$name.md" ]; then cp "$dest/$name.md" "$backup/$name.md"; fi
    cp "$src/$name.md" "$dest/$name.md"
  done
}

install_codex() {
  local home="${CODEX_HOME:-$HOME/.codex}"
  copy_skills "$home/skills" "$home/backups/architect-agent-superpowers-$STAMP/skills"
  echo "Codex: installed ${#SKILLS[@]} skills to $home/skills"
}

install_claude() {
  local home="$HOME/.claude"
  copy_skills "$home/skills" "$home/backups/architect-agent-superpowers-$STAMP/skills"
  copy_agents "$ROOT/providers/claude/agents" "$home/agents" "$home/backups/architect-agent-superpowers-$STAMP/agents"
  echo "Claude Code: installed skills + agents under $home"
}

install_gemini() {
  local home="$HOME/.gemini"
  copy_skills "$home/skills" "$home/backups/architect-agent-superpowers-$STAMP/skills"
  copy_agents "$ROOT/agents" "$home/agents" "$home/backups/architect-agent-superpowers-$STAMP/agents"
  echo "Gemini CLI: installed skills + agents under $home"
}

case "$TARGET" in
  codex) install_codex ;;
  claude) install_claude ;;
  gemini) install_gemini ;;
  all) install_codex; install_claude; install_gemini ;;
  *) echo "Usage: $0 [all|codex|claude|gemini]" >&2; exit 2 ;;
esac

echo "Installation complete. Start a fresh agent session (or use the provider's reload command) before verification."
