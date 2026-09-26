# tests/test_cli.py
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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

def test_src_main_shim_help():
    """Verify that legacy python src/main.py --help executes without relative import errors."""
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "src" / "main.py"), "--help"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "--filter" in result.stdout

def test_pipeline_filter_uses_scraped_df():
    """Verify that running --filter with mode='scholar' consumes newly scraped DataFrame directly."""
    from unittest.mock import patch
    import pandas as pd
    from main import run_pipeline

    fake_df = pd.DataFrame([{"Title": "Scraped Paper", "Abstract": "Scraped abstract", "Source": "IEEE"}])
    with patch("main.ScholarScraper") as mock_scholar_cls, \
         patch("main.AgentLLM") as mock_llm_cls:
        mock_scholar = mock_scholar_cls.return_value
        mock_scholar.scrape.return_value = fake_df

        mock_llm = mock_llm_cls.return_value
        mock_llm.filter_papers.return_value = fake_df

        ret = run_pipeline(mode="scholar", filter_papers=True)
        assert ret == 0
        mock_llm.filter_papers.assert_called_once_with(fake_df)
        mock_llm.save_results.assert_called_once_with(fake_df)


