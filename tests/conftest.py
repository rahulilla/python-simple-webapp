"""
Make the repo root importable so `from app import ...` works in tests.

The app is a single top-level `app.py` at the repo root (no package wrapper),
so pytest needs the repo root on sys.path to find it.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
