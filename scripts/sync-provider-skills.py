#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil, sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "skills"
DST = ROOT / "providers" / "claude" / "skills"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def files(folder):
    """Relative path -> bytes for every shipped file in a skill folder."""
    if not folder.is_dir():
        return {}
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc" and p.name != ".DS_Store"}


def drift():
    names = sorted(p.name for p in SRC.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
    return [n for n in names if files(SRC / n) != files(DST / n)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = drift()
    if args.check:
        if stale:
            print("Provider skill drift:", ", ".join(stale))
            sys.exit(1)
        print("Provider skills match canonical skills.")
    else:
        for name in stale:
            shutil.rmtree(DST / name, ignore_errors=True)
            shutil.copytree(SRC / name, DST / name, ignore=IGNORE)
        print("Skills synchronized.")
