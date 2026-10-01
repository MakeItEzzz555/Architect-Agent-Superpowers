# Updating Architect Agent Superpowers

## Clone-based install

Pull the latest version and reinstall only runtimes already present on the machine.

### macOS / Linux

```bash
git pull --ff-only
bash scripts/install-global.sh auto
```

### Windows PowerShell

```powershell
git pull --ff-only
powershell -ExecutionPolicy Bypass -File .\scripts\install-global.ps1 auto
```

The installers stay user-scoped and back up conflicting skill or agent folders before replacement.

## Claude Code plugin

```bash
claude plugin update architect-agent-superpowers@architect-agent-superpowers
```
## Gemini CLI extension

```bash
gemini extensions update architect-agent-superpowers
```

Restart the Gemini CLI session after an extension update so new components are loaded.

## Maintainer verification

```bash
python3 scripts/sync-provider-skills.py --check
python3 tests/check_repo.py
bash -n scripts/install-global.sh
```

If Claude Code is installed:

```bash
claude plugin validate --strict ./providers/claude
claude plugin validate --strict .
```
