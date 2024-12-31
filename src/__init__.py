# __init__.py
from .scholar import ScholarScraper
from .data_handler import DataHandler
from .scrapers import (
    AbstractScraper, ArxivScraper, IeeeScraper, SpringerScraper,
    MlrScraper, ACMScraper, NeuripsScraper, MdpiScraper, ScienceDirectScraper
)
from .utils import user_cycle, detect_source
