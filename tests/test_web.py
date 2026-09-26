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
