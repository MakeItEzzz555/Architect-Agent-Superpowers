# Quickstart for Architects

You do not need to know prompt engineering.

## Download ZIP
1. Choose **Code → Download ZIP** on GitHub.
2. Extract it.
3. Open your AI coding/agent tool in the extracted folder.
4. Paste the prompt from `ADOPT_WITH_YOUR_AGENT.md`.
5. Let the agent install only the provider(s) it detects and verify the result.

## Terminal
macOS/Linux:
```bash
git clone https://github.com/MakeItEzzz555/Architect-Agent-Superpowers.git
cd Architect-Agent-Superpowers
bash scripts/install-global.sh auto
```

Windows:
```powershell
git clone https://github.com/MakeItEzzz555/Architect-Agent-Superpowers.git
cd Architect-Agent-Superpowers
powershell -ExecutionPolicy Bypass -File .\scripts\install-global.ps1 auto
```

## First project
Copy `templates/ARCHITECTURE_PROJECT.md` into your project and fill only what you know.

Then ask naturally:
- "Turn this client brief into a room program."
- "Audit these drawings before I issue them."
- "Research the planning constraints for this site and cite official sources."
- "Review this concept for circulation, daylight, structure and constructability."
- "Help me automate this repetitive Revit/IFC/DWG task safely."


`auto` installs only for supported CLI runtimes already present on the machine. Use `all` only if you deliberately want all provider directories.

## Native Codex plugin

```bash
codex plugin marketplace add MakeItEzzz555/Architect-Agent-Superpowers
codex plugin add architect-agent-superpowers@architect-agent-superpowers
```
