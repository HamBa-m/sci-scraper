# tests/test_paths.py
import pytest
from pathlib import Path
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    PROJECT_ROOT as CFG_ROOT,
    RESULTS_DIR,
    LOG_DIR,
    SRC_DIR,
    get_config,
    get_keywords,
    get_venues,
    setup_logging
)

def test_project_root_resolution():
    assert CFG_ROOT.exists()
    assert (CFG_ROOT / "README.md").exists()
    assert (CFG_ROOT / "requirements.txt").exists()

def test_directories_creation():
    assert RESULTS_DIR.exists()
    assert LOG_DIR.exists()
    assert SRC_DIR.exists()

def test_json_configurations_loading():
    cfg = get_config()
    assert "start_year" in cfg
    assert "scholar_query" in cfg

    keywords = get_keywords()
    assert "adversarial" in keywords
    assert "marl" in keywords

    venues = get_venues()
    assert "AAMAS" in venues
    assert "ICML" in venues

def test_logging_setup():
    test_log = setup_logging("test_run.log")
    assert test_log.exists()
    assert test_log.parent == LOG_DIR
