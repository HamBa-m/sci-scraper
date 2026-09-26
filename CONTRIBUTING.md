# Contributing to Sci-Scraper

Thank you for your interest in contributing to **Sci-Scraper**! We welcome contributions from researchers and developers, including bug reports, new publisher extractors, additional venue crawlers, and documentation improvements.

All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features & Enhancements](#suggesting-features--enhancements)
  - [Adding a New Publisher Extractor](#adding-a-new-publisher-extractor)
  - [Adding a New Conference / Venue](#adding-a-new-conference--venue)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)

---

## Getting Started

1. Fork the repository on GitHub: `https://github.com/HamBa-m/sci-scraper`.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/sci-scraper.git
   cd sci-scraper
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

We recommend using Python 3.8 or higher in a dedicated virtual environment:

```bash
# Create and activate virtual environment
python -m venv venv

# On Linux/macOS:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## How to Contribute

### Reporting Bugs
If you encounter a broken scraper or an unexpected error:
1. Check existing [GitHub Issues](https://github.com/HamBa-m/sci-scraper/issues) to ensure it has not already been reported.
2. Open a new issue with:
   - A clear description of the bug.
   - The exact command run or script executed.
   - The publisher / venue URL causing the issue.
   - Full stack trace from `log/main.log`.
   - Your Python and OS version.

### Suggesting Features & Enhancements
Open an issue describing the proposed feature, the rationale, and how it benefits scientific literature curation.

---

### Adding a New Publisher Extractor

To add support for a new academic publisher:

1. **Implement the Extractor in `src/scholar_scrapers.py`:**
   Create a new class inheriting from `AbstractScraper`:
   ```python
   class NewPublisherScraper(AbstractScraper):
       def get_abstract(self, url: str) -> Optional[str]:
           try:
               headers = {'User-Agent': next(user_cycle)}
               response = requests.get(url, headers=headers, timeout=10)
               soup = BeautifulSoup(response.text, 'html.parser')
               
               # Extract abstract via DOM selectors, meta tags, or JSON-LD
               abstract_elem = soup.find('div', class_='abstract-content')
               if abstract_elem:
                   return abstract_elem.get_text().strip()
           except Exception as e:
               logging.error(f"Error fetching abstract from {url}: {e}")
           return None
   ```

2. **Register Domain Mapping in `src/utils.py`:**
   Add the publisher's domain pattern to the `sources` dictionary in `detect_source()`:
   ```python
   'newpublisher.org': 'NewPublisher',
   'dl.newpublisher.org': 'NewPublisher',
   ```

3. **Register the Class in `src/scholar.py`:**
   Import the class and register it in `ScholarScraper.__init__()`:
   ```python
   self.scrapers['NewPublisher'] = NewPublisherScraper()
   ```

---

### Adding a New Conference / Venue

To add a new conference proceedings target:

1. **Add Venue Configuration in `src/venues.json`:**
   ```json
   "NEWCONF": {
       "base_url": "https://proceedings.example.org",
       "proceedings_url_template": "https://proceedings.example.org/{year}/",
       "paper_wrapper_class": "paper-entry",
       "title_selector": "h3.title",
       "details_selector": "a.details",
       "abstract_page_selector": "div.abstract",
       "venue_name": "NEWCONF"
   }
   ```

2. **Implement Venue Crawler in `src/venues_scrapers.py`:**
   Subclass `BaseScraper` if custom parsing logic is required, or map the selectors in `src/venues.py`.

---

## Pull Request Process

1. Ensure your code follows the project's coding style (PEP 8, clear variable names, informative logging).
2. Test your changes locally to confirm scraping works and no existing functionality is broken.
3. Commit your changes with clear, descriptive commit messages.
4. Push to your fork and submit a Pull Request against `main`.
5. Clearly explain what changes were made and why in the PR description.

---

## Coding Standards

- **Defensive Networking:** Always set sensible `timeout` values on `requests.get()` and handle network errors gracefully.
- **Polite Crawling:** Respect inter-request delays and cycling user-agents to avoid overloading publisher servers.
- **Logging:** Use `logging.info()` for operational progress and `logging.error()` for handled exceptions. Avoid bare `print()` statements in library code.
- **Clean Output:** Normalize whitespace and strip formatting artifacts from all extracted text.
