# One-click agent install prompt

Paste the prompt below into **Codex, Claude Code, Gemini CLI, Cursor, OpenCode, Copilot, or another filesystem-capable coding agent**.

Copying this prompt does not itself install anything. The agent must have permission to inspect the official repository and change user-scoped skill/plugin files.

```text
Install Architect Agent Superpowers for my current user.
Official source: https://github.com/MakeItEzzz555/Architect-Agent-Superpowers

Goal:
Make the repository's architecture/AEC Agent Skills available to the AI-agent runtimes already installed on this machine, then verify the installation.

Do this:
1. Inspect the official repository README, INSTALL_PROMPT.md, skills/manifest.json, provider docs, and installer scripts first. Do not use unknown mirrors or third-party repackaging.
2. Detect the agent host(s) actually installed on this machine and their supported user/global Agent Skills locations.
3. Show me the detected hosts and the exact installation method before making changes.
4. Prefer the standard Agent Skills installer when supported:
   npx skills@latest add MakeItEzzz555/Architect-Agent-Superpowers --all -g
   If the host is not supported by that installer, use this repository's documented native Codex/Claude/Gemini installation or its reversible global installer.
5. Preserve existing skills and configuration. Back up conflicts before replacement. Do not use sudo/root, delete unrelated skills, enable telemetry beyond a tool's existing defaults, read credentials, modify my architecture projects, or install third-party MCP servers/plugins.
6. Install only Architect Agent Superpowers and its first-party provider adapters. Do not automatically install Revit/Rhino/AutoCAD/Archicad/Vectorworks/SketchUp/Blender/Bonsai MCP integrations; those require separate review and permission.
7. Verify the installed skill count against skills/manifest.json. For provider-native packages, use the host's documented list/validate command when available.
8. Report PASS/FAIL per detected host, the installed paths, backup paths, skill count, and how to uninstall/update.
9. Tell me to start a fresh session or reload skills/plugins if the host requires it.

Stop rather than guessing if a host, command, path, or permission model is unclear.
Do not claim successful installation until the filesystem/provider confirms it.
```

## Universal Agent Skills command

```bash
npx skills@latest add MakeItEzzz555/Architect-Agent-Superpowers --all -g
```

The community `skills` CLI supports many Agent Skills hosts. Its upstream CLI documents anonymous telemetry; set `DISABLE_TELEMETRY=1` before the command if you prefer to opt out.

## Repository-native fallback

macOS / Linux:

```bash
git clone https://github.com/MakeItEzzz555/Architect-Agent-Superpowers.git
cd Architect-Agent-Superpowers
bash scripts/install-global.sh auto
```

Windows PowerShell:

```powershell
git clone https://github.com/MakeItEzzz555/Architect-Agent-Superpowers.git
cd Architect-Agent-Superpowers
powershell -ExecutionPolicy Bypass -File .\scripts\install-global.ps1 auto
```
