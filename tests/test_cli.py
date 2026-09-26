# tests/test_cli.py
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_cli_help():
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py"), "--help"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "--filter" in result.stdout

def test_cli_mode_none():
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py"), "--mode", "none"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    assert result.returncode == 0

def test_cli_invalid_mode():
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py"), "--mode", "unknown_mode"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    assert result.returncode != 0
    assert "invalid choice" in result.stderr or "error" in result.stderr
