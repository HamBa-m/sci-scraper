#!/usr/bin/env python3
"""
Backwards-compatibility entrypoint for src/main.py.
Ensures repository root is on sys.path and delegates to root main.py.
"""
import sys
from pathlib import Path

# Ensure project root is at the front of sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import main, run_pipeline

if __name__ == '__main__':
    main()