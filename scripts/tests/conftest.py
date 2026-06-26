"""Pytest configuration — sets up PYTHONPATH for all tests."""
import sys
from pathlib import Path

# Ensure project root is on the path
ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
