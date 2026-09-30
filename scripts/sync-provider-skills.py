#!/usr/bin/env python3
from pathlib import Path
import argparse, filecmp, shutil, sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "skills"
DST = ROOT / "providers" / "claude" / "skills"

parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()

names = sorted(p.name for p in SRC.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
drift = []
for name in names:
    s = SRC / name / "SKILL.md"
    d = DST / name / "SKILL.md"
    if not d.exists() or s.read_bytes() != d.read_bytes():
        drift.append(name)
        if not args.check:
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, d)

if args.check and drift:
    print("Provider skill drift:", ", ".join(drift))
    sys.exit(1)
print("Skills synchronized." if not args.check else "Provider skills match canonical skills.")
