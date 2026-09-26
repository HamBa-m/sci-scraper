"""Smoke tests for analysis requirements and notebook documentation."""
from pathlib import Path


def test_requirements_analysis_exists():
    root = Path(__file__).resolve().parent.parent
    req_file = root / "requirements-analysis.txt"
    assert req_file.exists(), "requirements-analysis.txt must exist at repo root"
    content = req_file.read_text(encoding="utf-8")
    expected_pkgs = [
        "bertopic",
        "sentence-transformers",
        "umap-learn",
        "hdbscan",
        "matplotlib",
        "seaborn",
        "jupyter",
    ]
    for pkg in expected_pkgs:
        assert pkg in content, f"Missing required analysis package '{pkg}' in requirements-analysis.txt"


def test_notebooks_readme_exists():
    root = Path(__file__).resolve().parent.parent
    readme_file = root / "notebooks" / "README.md"
    assert readme_file.exists(), "notebooks/README.md must exist"
    content = readme_file.read_text(encoding="utf-8")
    assert "eda.ipynb" in content
    assert "bertopic.ipynb" in content
    assert "papers_content.csv" in content
    assert "papers_topics.csv" in content
    assert "requirements-analysis.txt" in content
