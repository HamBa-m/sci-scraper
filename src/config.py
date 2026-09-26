# src/config.py
from pathlib import Path
import json
import logging
import os

# Project root anchor (one level up from src/)
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "results"
LOG_DIR = PROJECT_ROOT / "log"

# Ensure essential runtime directories exist
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_config_path(filename: str) -> Path:
    """Find a configuration file in src/config/ if present, otherwise in src/."""
    nested_path = SRC_DIR / "config" / filename
    if nested_path.exists():
        return nested_path
    return SRC_DIR / filename

def load_json_config(filename: str) -> dict:
    """Safely load a JSON configuration file using absolute paths."""
    config_path = get_config_path(filename)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Convenience loaders
def get_config() -> dict:
    return load_json_config("config.json")

def get_keywords() -> dict:
    return load_json_config("keywords.json")

def get_venues() -> dict:
    return load_json_config("venues.json")

def setup_logging(log_filename: str = "main.log", level: int = logging.INFO):
    """Configure centralized logging to write UTF-8 logs to LOG_DIR."""
    log_file = LOG_DIR / log_filename
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(str(log_file), encoding="utf-8")
        ]
    )
    return log_file
