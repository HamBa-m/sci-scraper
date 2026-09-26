# tests/test_modules.py
from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_handler import DataHandler
from src.config import get_config, get_keywords, get_venues, SRC_DIR, RESULTS_DIR

def test_data_handler_init_and_stats():
    handler = DataHandler()
    assert handler.results_dir == RESULTS_DIR

    sample_data = [
        {"title": "Paper A", "source": "IEEE", "abstract": "Valid abstract text", "year": 2023},
        {"title": "Paper B", "source": "ACM", "abstract": None, "year": 2024},
    ]
    stats = handler.calculate_statistics(sample_data)
    assert "Total papers found: 2" in stats
    assert "Total papers with abstracts: 1" in stats
    assert "50.0%" in stats

def test_data_handler_production_schema():
    """Verify calculate_statistics accepts production ScholarScraper DataFrame output with Title/Abstract/Source/Year/URL."""
    handler = DataHandler()
    prod_df = pd.DataFrame([
        {"Title": "Paper 1", "URL": "https://ieee.org/1", "Abstract": "Real abstract", "Source": "IEEE", "Year": 2023},
        {"Title": "Paper 2", "URL": "https://acm.org/2", "Abstract": None, "Source": "ACM", "Year": 2024},
        {"Title": "Paper 3", "URL": "https://other.org/3", "Abstract": "Another abstract", "Source": "Other (arXiv)", "Year": 2022},
    ])
    stats = handler.calculate_statistics(prod_df)
    assert "Total papers found: 3" in stats
    assert "Total papers with abstracts: 2" in stats
    assert "66.7%" in stats
    assert "IEEE" in stats
    assert "Other (arXiv)" in stats

def test_config_subfolder_migration():
    config_dir = SRC_DIR / "config"
    assert config_dir.is_dir()
    assert (config_dir / "config.json").exists()
    assert (config_dir / "keywords.json").exists()
    assert (config_dir / "venues.json").exists()

    cfg = get_config()
    assert cfg["start_year"] == 2018
    assert "scholar_query" in cfg

    kw = get_keywords()
    assert len(kw["adversarial"]) > 0

    venues = get_venues()
    assert "AAMAS" in venues

def test_root_init_removed():
    root_init = PROJECT_ROOT / "__init__.py"
    assert not root_init.exists()
