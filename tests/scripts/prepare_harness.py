#!/usr/bin/env python3
"""Copy the role to an external path with the basename expected by dispatch."""
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parents[2]
destination = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("/tmp/rustfs-role-harness/roles/rustfs")
if destination.exists():
    shutil.rmtree(destination)
destination.parent.mkdir(parents=True, exist_ok=True)
ignore = shutil.ignore_patterns(".git", "harness", "*.retry")
shutil.copytree(root, destination, ignore=ignore)
print(destination)
