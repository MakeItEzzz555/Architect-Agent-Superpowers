import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-global.sh"
DRAWING = Path("architectural-drawing-generation")
LEDGER = ".gridline.installed"


def run_drawing_engine(skills_dir):
    """Run the bundled engine exactly as an agent would after install: from the installed skill folder."""
    skill = Path(skills_dir) / DRAWING
    return subprocess.run(
        [sys.executable, "-I", str(skill / "scripts" / "aec_draw.py"),
         str(skill / "references" / "concept-plan.drawing.json"), "--validate-only"],
        capture_output=True, text=True)


@unittest.skipIf(shutil.which("bash") is None, "bash installer needs bash")
class InstallPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def install(self, *args, fail=None, frozen_clock=False):
        env = {**os.environ, "HOME": str(self.home), "CODEX_HOME": str(self.home / ".codex")}
        shims = Path(self.tmp.name) / "shims"
        shims.mkdir(exist_ok=True)
        env["PATH"] = f"{shims}{os.pathsep}{env['PATH']}"
        if frozen_clock:
            (shims / "date").write_text("#!/bin/bash\necho 20261021-120000\n")
            (shims / "date").chmod(0o755)
        if fail:
            # Put a cp/mv on PATH that fails while staging or placing drawing-qa, like a full disk would.
            for tool in ("cp", "mv"):
                shim = shims / tool
                shim.write_text(
                    "#!/bin/bash\n"
                    f'case "$*" in *drawing-qa.aas-new.*) if [ "{tool}" = "$AAS_FAIL" ]; then '
                    f'[ "{tool}" = cp ] && /bin/cp "$@"; exit 1; fi ;; esac\n'
                    f'exec /bin/{tool} "$@"\n')
                shim.chmod(0o755)
            env["AAS_FAIL"] = fail
        return subprocess.run(["bash", str(INSTALLER), *args], capture_output=True, text=True, env=env)

    def test_every_install_path_ships_a_runnable_drawing_engine(self):
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        for host in (".codex", ".claude", ".gemini"):
            with self.subTest(host=host):
                ran = run_drawing_engine(self.home / host / "skills")
                self.assertEqual(ran.returncode, 0, ran.stderr)
                self.assertIn("VALID", ran.stdout)
        # Claude plugin marketplace source is ./providers/claude; copy it alone to prove it is self-contained.
        plugin = Path(self.tmp.name) / "plugin"
        shutil.copytree(ROOT / "providers" / "claude", plugin)
        ran = run_drawing_engine(plugin / "skills")
        self.assertEqual(ran.returncode, 0, ran.stderr)

    def test_foreign_skill_blocks_install_until_forced_and_backup_restores_it(self):
        foreign = self.home / ".claude" / "skills" / "drawing-qa" / "SKILL.md"
        foreign.parent.mkdir(parents=True)
        foreign.write_text("someone else's skill\n")

        refused = self.install("claude")
        self.assertEqual(refused.returncode, 4)
        self.assertIn(str(foreign.parent), refused.stderr)
        self.assertEqual(foreign.read_text(), "someone else's skill\n")
        self.assertEqual(sorted(p.name for p in (self.home / ".claude" / "skills").iterdir()), ["drawing-qa"])
        self.assertFalse((self.home / ".claude" / LEDGER).exists())

        forced = self.install("claude", "--force")
        self.assertEqual(forced.returncode, 0, forced.stderr)
        self.assertNotEqual(foreign.read_text(), "someone else's skill\n")
        backups = list((self.home / ".claude" / "backups").glob("gridline-*/skills/drawing-qa"))
        self.assertEqual(len(backups), 1)

        # Restoring is moving the backup back.
        shutil.rmtree(foreign.parent)
        shutil.move(str(backups[0]), str(foreign.parent))
        self.assertEqual(foreign.read_text(), "someone else's skill\n")

    def test_old_ownership_ledger_updates_without_force(self):
        # A Gridline update recognizes only the explicitly recorded paths
        # from the prior brand, leaving unrelated foreign items protected.
        self.assertEqual(self.install("gemini").returncode, 0)
        home = self.home / ".gemini"
        legacy = home / ".architect-agent-superpowers.installed"
        (home / LEDGER).rename(legacy)
        installed = home / "skills" / "drawing-qa" / "SKILL.md"
        installed.write_text("old installed version\\n")
        upgraded = self.install("gemini")
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr)
        self.assertEqual(installed.read_bytes(), (ROOT / "skills" / "drawing-qa" / "SKILL.md").read_bytes())
        self.assertIn("skills/drawing-qa", (home / LEDGER).read_text())
        self.assertTrue(legacy.is_file())

    def test_reinstall_updates_owned_items_without_force(self):
        self.assertEqual(self.install("gemini").returncode, 0)
        installed = self.home / ".gemini" / "skills" / "drawing-qa" / "SKILL.md"
        installed.write_text("older version\n")

        again = self.install("gemini")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(installed.read_bytes(), (ROOT / "skills" / "drawing-qa" / "SKILL.md").read_bytes())
        previous = list((self.home / ".gemini" / "backups").glob("*/skills/drawing-qa/SKILL.md"))
        self.assertEqual([p.read_text() for p in previous], ["older version\n"])
        ledger = (self.home / ".gemini" / LEDGER).read_text().split()
        self.assertIn("skills/drawing-qa", ledger)
        self.assertIn("agents/drawing-reviewer.md", ledger)
        self.assertEqual(list(self.home.glob(".gemini/**/*.aas-new.*")), [])

    def test_interrupted_upgrade_keeps_the_previous_version(self):
        self.assertEqual(self.install("gemini").returncode, 0)
        installed = self.home / ".gemini" / "skills" / "drawing-qa" / "SKILL.md"
        for step in ("cp", "mv"):
            with self.subTest(failing=step):
                installed.write_text("working older version\n")
                result = self.install("gemini", fail=step)
                self.assertEqual(result.returncode, 1)
                self.assertIn("install stopped", result.stderr)
                self.assertEqual(installed.read_text(), "working older version\n")
                self.assertEqual(list(self.home.glob(".gemini/**/*.aas-new.*")), [])
                self.assertIn("skills/drawing-qa", (self.home / ".gemini" / LEDGER).read_text().split())
        # The next normal run finishes the upgrade.
        self.assertEqual(self.install("gemini").returncode, 0)
        self.assertEqual(installed.read_bytes(), (ROOT / "skills" / "drawing-qa" / "SKILL.md").read_bytes())

    def test_runs_in_the_same_second_get_separate_backups(self):
        for _ in range(3):
            self.assertEqual(self.install("codex", frozen_clock=True).returncode, 0)
        backups = list((self.home / ".codex" / "backups").iterdir())
        self.assertEqual(len(backups), 2)
        for folder in backups:
            self.assertTrue((folder / "skills" / "drawing-qa" / "SKILL.md").is_file())
            self.assertFalse((folder / "skills" / "drawing-qa" / "drawing-qa").exists())


if __name__ == "__main__":
    unittest.main()
