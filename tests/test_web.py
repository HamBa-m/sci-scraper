# tests/test_web.py
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from web.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_web_index_get(client):
    response = client.get("/")
    assert response.status_code == 200
    html_text = response.get_data(as_text=True)
    assert "Scholar Scraper" in html_text
    assert "Search Query" in html_text
    assert "Number of Pages" in html_text

def test_web_static_assets_exist():
    css_file = PROJECT_ROOT / "web" / "static" / "css" / "styles.css"
    js_file = PROJECT_ROOT / "web" / "static" / "js" / "script.js"
    template_file = PROJECT_ROOT / "web" / "templates" / "index.html"

    assert css_file.exists()
    assert js_file.exists()
    assert template_file.exists()

def test_web_production_data_statistics_parsing():
    """Verify that production ScholarScraper output (capitalized columns) parses through web stats without KeyError."""
    import pandas as pd
    from web.app import parse_stats_text
    from src.data_handler import DataHandler

    handler = DataHandler()
    prod_results = pd.DataFrame([
        {"Title": "Adversarial MARL", "URL": "https://example.com/1", "Abstract": "Paper abstract", "Source": "IEEE", "Year": 2024},
        {"Title": "Dec-POMDP Robustness", "URL": "https://example.com/2", "Abstract": None, "Source": "ACM", "Year": 2023},
    ])
    stats_text = handler.calculate_statistics(prod_results)
    stats_data = parse_stats_text(stats_text)

    assert stats_data["total_papers"] == 2
    assert stats_data["papers_with_abstracts"] == 1
    assert stats_data["abstract_success_rate"] == 50.0
    assert len(stats_data["source_stats"]) == 2

