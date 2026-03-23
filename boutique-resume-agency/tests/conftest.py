"""Centralized pytest configuration for boutique-resume-agency tests."""
import sys
import os

# Ensure scripts/ is importable regardless of where pytest is invoked from
_scripts_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_scripts_dir))
