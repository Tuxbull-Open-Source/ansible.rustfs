#!/usr/bin/env python3
"""Install a real role directory under the basename expected by dispatch."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[2]
destination = root / "harness" / "roles" / "rustfs"
if destination.exists():
    shutil.rmtree(destination)
ignore = shutil.ignore_patterns(".git", "harness", "*.retry")
shutil.copytree(root, destination, ignore=ignore)
print(destination)
