#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ran=0

if command -v claude >/dev/null 2>&1; then
  echo "Claude Code: strict plugin + marketplace validation"
  claude plugin validate --strict "$ROOT/providers/claude"
  claude plugin validate --strict "$ROOT"
  ran=1
else
  echo "Claude Code: CLI not installed; native validation skipped"
fi

if command -v codex >/dev/null 2>&1; then
  echo "Codex: isolated local marketplace/plugin installation"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  mkdir -p "$tmp/codex"
  CODEX_HOME="$tmp/codex" codex plugin marketplace add "$ROOT" --json >/dev/null
  CODEX_HOME="$tmp/codex" codex plugin add architect-agent-superpowers@architect-agent-superpowers --json >/dev/null
  CODEX_HOME="$tmp/codex" codex plugin list | grep -q "architect-agent-superpowers@architect-agent-superpowers"
  ran=1
else
  echo "Codex: CLI not installed; native validation skipped"
fi

if command -v gemini >/dev/null 2>&1; then
  echo "Gemini CLI: extension validation"
  gemini extensions validate "$ROOT"
  ran=1
else
  echo "Gemini CLI: CLI not installed; native validation skipped"
fi

if [ "$ran" -eq 0 ]; then
  echo "No supported provider-native validator was available. Repository validation should still be run separately."
fi

