# Architect Agent Superpowers

> Portable, token-efficient AI skills and specialist agents for architecture / AEC workflows.

Architect Agent Superpowers turns supported coding/agent CLIs into an architecture copilot without forcing architects to learn prompt engineering first.

**Targets:** OpenAI Codex, Claude Code, Gemini CLI, and other tools that understand the open Agent Skills format.

## Superpowers

| Capability | Purpose |
|---|---|
| `architecture-orchestrator` | Routes complex work to the smallest useful specialist set |
| `architecture-programming` | Briefs, room schedules, adjacency and area programs |
| `site-regulation-research` | Planning/zoning/code research with source traceability |
| `concept-design-review` | Design critique and option trade-offs |
| `cad-bim-automation` | Safe Revit/IFC/DWG/DXF/SVG/BIM automation planning |
| `drawing-qa` | Cross-sheet drawing-set QA and coordination |
| `area-quantity-audit` | Areas, counts, schedules and quantity reconciliation |
| `presentation-review` | Boards, narratives, diagrams and presentation flow |
| `architecture-red-team` | Independent final challenge before issue/submission |

Skills use progressive disclosure: lightweight metadata is visible first; detailed procedures load only when relevant.

## Easiest install — no technical knowledge required

1. Click **Code → Download ZIP** on GitHub.
2. Extract the ZIP.
3. Open Codex, Claude Code, Gemini CLI, or another filesystem-capable coding agent in the extracted folder.
4. Paste the prompt in [docs/ADOPT_WITH_YOUR_AGENT.md](docs/ADOPT_WITH_YOUR_AGENT.md).
5. Let your agent detect installed runtimes, install the supported capabilities globally for your user, and verify them.

## CLI install

### macOS / Linux
```bash
git clone https://github.com/MakeItEzzz555/Architect-Agent-Superpowers.git
cd Architect-Agent-Superpowers
bash scripts/install-global.sh all
```

### Windows PowerShell
```powershell
git clone https://github.com/MakeItEzzz555/Architect-Agent-Superpowers.git
cd Architect-Agent-Superpowers
powershell -ExecutionPolicy Bypass -File .\scripts\install-global.ps1 all
```

Replace `all` with `codex`, `claude`, or `gemini` to install one provider only.

## Native installs

### Gemini CLI extension
```bash
gemini extensions install https://github.com/MakeItEzzz555/Architect-Agent-Superpowers
```

### Claude Code plugin
```bash
claude plugin marketplace add MakeItEzzz555/Architect-Agent-Superpowers
claude plugin install architect-agent-superpowers@architect-agent-superpowers
```

### Codex
```bash
bash scripts/install-global.sh codex
```

## First architecture project

Copy [templates/ARCHITECTURE_PROJECT.md](templates/ARCHITECTURE_PROJECT.md) into the project root. Leave unknown values as `UNKNOWN`.

Then ask:

> Use architecture-orchestrator. Read ARCHITECTURE_PROJECT.md if present. Inspect only the files relevant to my request, use specialist skills or subagents only when they improve the result, and keep verified facts, assumptions, design options, and unresolved questions separate.

## Safety boundary

This project accelerates research, design analysis, documentation, QA, automation, and communication. It does **not** turn an AI model into a licensed architect, engineer, fire consultant, accessibility specialist, quantity surveyor, surveyor, lawyer, or local authority. Construction-critical and regulated conclusions require competent human review in the relevant jurisdiction.

## Philosophy

- Provider-neutral core skills first.
- Tiny always-loaded routing context.
- Specialist expertise on demand.
- Evidence over confident guessing.
- Reversible file operations.
- Source/version traceability for regulations.
- Human review for consequential decisions.
- Incremental improvement without prompt bloat.

See [ROADMAP.md](ROADMAP.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [docs/PROVIDERS.md](docs/PROVIDERS.md).

## License
MIT — see [LICENSE](LICENSE).
