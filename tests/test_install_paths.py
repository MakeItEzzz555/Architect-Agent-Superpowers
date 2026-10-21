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
LEDGER = ".architect-agent-superpowers.installed"


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

    def install(self, *args):
        env = {**os.environ, "HOME": str(self.home), "CODEX_HOME": str(self.home / ".codex")}
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
        backups = list((self.home / ".claude" / "backups").glob("architect-agent-superpowers-*/skills/drawing-qa"))
        self.assertEqual(len(backups), 1)

        # Restoring is moving the backup back.
        shutil.rmtree(foreign.parent)
        shutil.move(str(backups[0]), str(foreign.parent))
        self.assertEqual(foreign.read_text(), "someone else's skill\n")

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


if __name__ == "__main__":
    unittest.main()
