#!/usr/bin/env python3
from pathlib import Path
import json, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "architecture-orchestrator","architecture-programming","site-regulation-research",
    "concept-design-review","cad-bim-automation","drawing-qa",
    "area-quantity-audit","presentation-review","architecture-red-team"
}

errors = []
for path in [ROOT/"plugin.json", ROOT/".codex-plugin/plugin.json", ROOT/"gemini-extension.json", ROOT/".claude-plugin/marketplace.json", ROOT/"providers/claude/.claude-plugin/plugin.json"]:
    try: json.loads(path.read_text())
    except Exception as e: errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {e}")

found = set()
for skill in (ROOT/"skills").glob("*/SKILL.md"):
    text = skill.read_text()
    m = re.match(r"---\s*\n(.*?)\n---", text, re.S)
    if not m:
        errors.append(f"{skill.relative_to(ROOT)}: missing frontmatter"); continue
    n = re.search(r"^name:\s*(.+)$", m.group(1), re.M)
    d = re.search(r"^description:\s*(.+)$", m.group(1), re.M)
    if not n or not d: errors.append(f"{skill.relative_to(ROOT)}: name/description required")
    else: found.add(n.group(1).strip())

if found != EXPECTED:
    errors.append(f"canonical skill set mismatch: {sorted(found)}")

for name in EXPECTED:
    a=(ROOT/"skills"/name/"SKILL.md").read_bytes()
    b=ROOT/"providers/claude/skills"/name/"SKILL.md"
    if not b.exists() or a != b.read_bytes(): errors.append(f"Claude skill drift: {name}")

for folder in [ROOT/"agents", ROOT/"providers/claude/agents"]:
    if len(list(folder.glob("*.md"))) < 6: errors.append(f"{folder.relative_to(ROOT)}: expected at least 6 agents")

if errors:
    print("\n".join("ERROR: "+e for e in errors)); sys.exit(1)
print(f"PASS: {len(EXPECTED)} skills, provider sync, manifests, and agent packs validated.")
