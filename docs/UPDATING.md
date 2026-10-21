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

The installers stay user-scoped. Each host home gets a `.architect-agent-superpowers.installed` list of the skill and agent paths this pack installed. Only those are replaced on update; the previous version is moved (never deleted) to `backups/architect-agent-superpowers-<timestamp>/` in that home.

If a skill or agent with the same name exists but is not on that list (another pack, a plugin-manager install, or an install made before 0.5.1), the installer changes nothing and exits with code 4, listing the paths. Check those paths first. To replace them anyway, re-run with `--force` (`-Force` on Windows); they are moved to the backup folder.

To restore an item, move it back from the backup folder over the installed copy.

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
