#!/usr/bin/env python3
"""
create_repo_zip.py

Usage:
  python3 create_repo_zip.py [--no-submodules]

Produces minerepo.zip in the current directory, excluding .git and build directories.
Initializes submodules unless --no-submodules is passed.
"""
import os
import sys
import zipfile
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
ZIP_NAME = REPO_ROOT / "minerepo.zip"
EXCLUDE_PATTERNS = [
    ".git",
    os.path.join("pythonbridge", "build"),
    "build",
    "__pycache__",
    ".DS_Store",
    "*.zip"
]

def should_exclude(path: Path) -> bool:
    s = str(path.relative_to(REPO_ROOT))
    if s.startswith(".git"):
        return True
    for pat in EXCLUDE_PATTERNS:
        if pat.endswith("*"):
            if s.startswith(pat[:-1]):
                return True
        elif pat in s:
            return True
    return False

def init_submodules():
    if (REPO_ROOT / ".git").exists():
        try:
            subprocess.run(["git", "submodule", "update", "--init", "--recursive"], check=True)
        except Exception as e:
            print("Warning: git submodule update failed:", e)

def main():
    include_submodules = True
    if len(sys.argv) > 1 and sys.argv[1] == "--no-submodules":
        include_submodules = False

    if include_submodules:
        init_submodules()

    if ZIP_NAME.exists():
        ZIP_NAME.unlink()

    with zipfile.ZipFile(ZIP_NAME, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(REPO_ROOT):
            root_path = Path(root)
            # skip .git folders early
            if should_exclude(root_path):
                # prune dirs
                dirs[:] = []
                continue
            for f in files:
                fpath = root_path / f
                if should_exclude(fpath):
                    continue
                # write file with path relative to repo root
                arcname = str(fpath.relative_to(REPO_ROOT))
                zf.write(fpath, arcname)
    print(f"Created {ZIP_NAME}")

if __name__ == "__main__":
    main()
