# __init__.py
from .scholar import ScholarScraper
from .venues import VenueScraper
from .llm_agent import AgentLLM

from .scholar_scrapers import (
    AbstractScraper, ArxivScraper, IeeeScraper, SpringerScraper,
    MlrScraper, ACMScraper, NeuripsScraper, MdpiScraper, ScienceDirectScraper
)

from .venues_scrapers import (
    AAMASScraper, AISTATSScraper, ICMLScraper, IJCAIScraper
)

from .utils import user_cycle, detect_source, extract_year
