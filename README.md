# Sci-Scraper

[![Python Version](https://img.shields.io/badge/Python-3.8.19%2B-blue.svg)](https://www.python.org/downloads/) [![GitHub Repo stars](https://img.shields.io/github/stars/HamBa-m/sci-scraper?style=social)](https://github.com/HamBa-m/sci-scraper/stargazers) [![GitHub issues](https://img.shields.io/github/issues/HamBa-m/sci-scraper)](https://github.com/HamBa-m/sci-scraper/issues) [![GitHub forks](https://img.shields.io/github/forks/HamBa-m/sci-scraper?style=social)](https://github.com/HamBa-m/sci-scraper/network/members) [![GitHub license](https://img.shields.io/github/license/HamBa-m/sci-scraper)](https://github.com/HamBa-m/sci-scraper/blob/main/LICENSE) 

A Python-based web scraping tool for collecting scientific literature from Google Scholar and academic venues. Extracts metadata like titles, abstracts, years, sources, and URLs into structured Excel files. Modular and extensible for various research domains.

This repository provides the complete implementation, intermediate datasets, and engineering documentation of the literature collection pipeline accompanying our survey paper:
> **"A Survey on Adversarial Multi-Agent Deep Reinforcement Learning"**  
> *ACM Computing Surveys (CSUR)*, Manuscript ID: `CSUR-2025-1595`.

---

## Features

- **Scholar Scraper**: Searches Google Scholar for top results (configurable $K$ pages). Features 12 custom extractors for publishers including IEEE, Springer Nature, MLR, ArXiv, NeurIPS, MDPI, ScienceDirect (with rate-limiting & manual mode), ACM, AAAI, JAIR, JMLR, and IJCAI.
- **Venue Scraper**: Directly targets specific conference and journal proceedings with combinatorial keyword filtering across configurable time horizons.
- **Parallel Processing**: Employs multithreaded worker pools (`ThreadPoolExecutor`) for up to 10× scraping speedup.
- **In-Memory PDF Parsing**: Extracts abstracts directly from proceedings PDFs on the fly without disk overhead.
- **Defensive & Ethical Scraping**: Implements user-agent rotation, domain-specific cooldown intervals, error handling, and polite delays.
- **Structured Output**: Merges, deduplicates, and saves datasets in standardized Excel format for downstream analysis.
- **Downstream Workflow Integration**: Supports automated LLM-based semantic filtering (e.g., via Hugging Face Hub) and topic modeling (BERTopic).

---

## Quick Start

### Installation

```bash
git clone https://github.com/HamBa-m/sci-scraper.git
cd sci-scraper
pip install -r requirements.txt

# (Optional) For EDA and BERTopic topic modeling in notebooks/:
pip install -r requirements-analysis.txt
```

### Basic Usage (CLI)

Run the tool from the repository root using command-line arguments:

```bash
python main.py --mode [scholar|venues|all|none] [--filter]
```

- `--mode`: Select scraping mode (default: `all`).
  - `scholar`: Scrape from Google Scholar only.
  - `venues`: Scrape from targeted venues only.
  - `all`: Scrape both, merge, remove duplicates by title, and save to `./results/all_results.xlsx`.
  - `none`: Skip scraping (useful with `--filter` if data already exists).
- `--filter`: (Optional) Apply LLM-based semantic filtering to refine results (reads from `./results/all_results.xlsx` and saves filtered output).

#### CLI Examples

- **Scrape everything and save merged results:**
  ```bash
  python main.py --mode all
  ```

- **Scrape venues only:**
  ```bash
  python main.py --mode venues
  ```

- **Filter existing data without scraping:**
  ```bash
  python main.py --mode none --filter
  ```

- **Scrape all and filter in one run:**
  ```bash
  python main.py --mode all --filter
  ```

Logs are saved to `log/main.log`. Output datasets are saved in `./results/`.

### Interactive Web Interface

An interactive Flask-based web dashboard is available for configuring queries, monitoring live scraping progress, and inspecting corpus statistics:

```bash
python web/app.py
```

Once launched, navigate to `http://127.0.0.1:5000` in your web browser.

### Python API Example

For programmatic integration or custom research workflows, import the modules directly from `src`:

```python
from src.scholar import ScholarScraper
from src.venues import VenueScraper
from src.llm_agent import AgentLLM
from src.config import RESULTS_DIR
import pandas as pd

# 1. Custom scraping
scholar = ScholarScraper()
df_scholar = scholar.scrape()

venue = VenueScraper()
df_venue = venue.scrape_venues()

# 2. Merge and deduplicate by title
merged_df = pd.concat([df_scholar, df_venue]).drop_duplicates(subset=["Title"])
merged_df.to_excel(RESULTS_DIR / "custom_results.xlsx", index=False)

# 3. Semantic filtering via LLM
agent = AgentLLM()
filtered = agent.filter_papers(merged_df)
agent.save_results(filtered)
```

### Running Automated Tests

A comprehensive test suite of automated regression and smoke tests is provided in `tests/`:

```bash
python -m pytest
```

### Repository Structure

```text
sci-scraper/
├── main.py                   # Root CLI entrypoint (multi-mode scraper & filter)
├── requirements.txt          # Core scraping & filtering dependencies
├── requirements-analysis.txt # Dependencies for notebooks (EDA, BERTopic)
├── pytest.ini                # Pytest configuration
├── src/                      # Core scraping & filtering library
│   ├── config/               # JSON configurations (config, keywords, venues)
│   ├── config.py             # Centralized path anchoring (PROJECT_ROOT)
│   ├── data_handler.py       # Data cleaning, deduplication, and persistence
│   ├── scholar.py            # Google Scholar scraping coordinator
│   ├── scholar_scrapers.py   # 12 publisher-specific extractors
│   ├── venues.py             # Venue scraping coordinator & parallel runner
│   ├── venues_scrapers.py    # Venue-specific extractors
│   ├── llm_agent.py          # LLM-based semantic filter (Hugging Face Hub)
│   └── utils.py              # User-agent rotation and polite delay helpers
├── web/                      # Web UI application
│   ├── app.py                # Flask application server
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS stylesheets & JavaScript assets
├── notebooks/                # Analysis & topic modeling replication
│   ├── eda.ipynb             # Exploratory Data Analysis
│   ├── bertopic.ipynb        # Neural topic modeling (BERTopic)
│   └── README.md             # Replication guide for survey figures
├── tests/                    # Automated smoke & regression test suite
└── results/                  # Scraped datasets and survey corpora
```

---

## Pipeline Overview

The tool is designed to support a systematic, four-phase literature survey methodology that is fully reproducible and adaptable to any research domain:

$$\textbf{Data Collection} \;\longrightarrow\; \textbf{Semantic Filtering} \;\longrightarrow\; \textbf{Exploratory Data Analysis} \;\longrightarrow\; \textbf{Topic Modeling}$$

![Overview of the data collection and processing pipeline](g_pipeline.png#gh-light-mode-only)
![Overview of the data collection and processing pipeline](g_pipeline.png#gh-dark-mode-only)

1. **Data Collection (Lexical Phase):** Collects papers from multiple sources using lexical matching, merges records, and strips title duplicates.
2. **Semantic Filtering:** Filters lexical results semantically using a Large Language Model (LLM) API to reduce noise and eliminate irrelevant matches.
3. **Exploratory Data Analysis (EDA):** Summarizes key corpus statistics, including publication counts over time, venue ranks, and source distributions.
4. **Topic Modeling:** Employs BERTopic to uncover underlying research themes and cluster papers into distinct categories.

---

## Scraper Implementation & Engineering Details

To build a robust dataset of research papers relevant to an area of interest (AOI), `sci-scraper` implements two primary components: **Scholar Scraper** and **Venue Scraper**; each targeting distinct sources of academic literature.

### Scholar Scraper

This component performs targeted searches on Google Scholar using a pre-defined query string $q$. It retrieves the top $K$ pages of search results, where $K$ is a configurable parameter (default: $K = 50$ pages, yielding up to 500 search results). 

Because Google Scholar search snippets truncate abstracts, the engine extracts the canonical landing URL (`h3.gs_rt a`), determines the hosting publisher via domain resolution, and dispatches the record to the appropriate publisher-specific extractor.

#### Publisher Domain Resolution
The `detect_source()` helper in `src/utils.py` inspects the URL's network location and routes it to the corresponding publisher extractor:
- `arxiv.org` $\rightarrow$ arXiv
- `ieee.org`, `ieeexplore.ieee.org` $\rightarrow$ IEEE
- `sciencedirect.com`, `elsevier.com` $\rightarrow$ ScienceDirect
- `springer.com`, `link.springer.com` $\rightarrow$ Springer Nature
- `acm.org`, `dl.acm.org` $\rightarrow$ ACM
- `proceedings.neurips.cc` $\rightarrow$ NeurIPS
- `ojs.aaai.org`, `aaai.org` $\rightarrow$ AAAI
- `proceedings.mlr.press` $\rightarrow$ MLR
- `mdpi.com`, `www.mdpi.com` $\rightarrow$ MDPI
- `jmlr.org` $\rightarrow$ JMLR
- `jair.org` $\rightarrow$ JAIR
- `ijcai.org` $\rightarrow$ IJCAI

### Custom Abstract Scrapers by Publisher

The component was designed to be highly modular and extensible, allowing for easy integration of additional publishers as needed. In `src/scholar_scrapers.py`, each publisher has a dedicated class inheriting from `AbstractScraper`:

1. **IEEE (`IeeeScraper`):**
   - Parses the numerical article identifier (`arnumber` or `/document/<id>/`) from the landing URL.
   - Emulates active browser sessions using custom headers (`Origin: https://ieeexplore.ieee.org`, referer binding).
   - Extracts abstract content from OpenGraph metadata: `<meta property="og:description">`.

2. **Springer Nature (`SpringerScraper`):**
   - Targets the main abstract container `<div id="Abs1-content">`.
   - Fallback 1: `<meta name="description">`.
   - Fallback 2: `<div class="c-article-section__content">`.

3. **MLR (`MlrScraper`):**
   - Targets `<div class="abstract">` or `<section class="abstract">`.
   - Fallback 1: `<meta name="description">`.
   - Fallback 2: Searches `<div id="content">` for paragraphs prefixed with "abstract".

4. **ArXiv (`ArxivScraper`):**
   - Normalizes any `export.arxiv.org` links to `arxiv.org`.
   - Extracts `<blockquote class="abstract">` and strips the leading `"Abstract:"` prefix.

5. **NeurIPS (`NeuripsScraper`):**
   - Scans headings `h1` through `h4` for the "abstract" text and extracts the subsequent paragraph or div element.

6. **MDPI (`MdpiScraper`):**
   - Targets `<div class="art-abstract">` and joins paragraph text.
   - Fallback 1: Dublin Core `<meta name="citation_abstract">`.
   - Fallback 2: Embedded JSON-LD schema (`application/ld+json`) looking for the `abstract` key.

7. **ScienceDirect (`ScienceDirectScraper`):**
   - ScienceDirect employs strict anti-scraping measures.
   - Implements a mandatory **11-second sliding cooldown window** between consecutive requests.
   - Cascades through three DOM selectors:
     - `div.abstract.author div.u-margin-s-bottom`
     - Selectors `div[class*="abstract"]` with automatic decomposition of `h2.section-title`.
     - Span elements within `<div class="abstract">`.
   - When anti-scraping challenges (e.g., Cloudflare verification) cannot be bypassed automatically, manual intervention is supported without losing records.

8. **ACM (`ACMScraper`):**
   - Targets `div.abstractSection`, `div.abstract-text`, or `div[class*="abstract"]`.
   - Fallback 1: Parses JSON-LD structured data looking for the `description` key.
   - Fallback 2: Checks `<meta name="citation_abstract">`.

9. **AAAI (`AAAIScraper`):**
   - Targets `<article class="obj_article_details"> <section class="item abstract">` and strips `h2.label`.
   - Fallback 1: Generic `<section class="abstract">`.
   - Fallback 2: Dublin Core `<meta name="citation_abstract">`.

10. **JAIR (`JAIRScraper`):**
    - Targets `div.abstract`, `div.article-abstract`, or `section.abstract-content`.
    - Fallback: Checks `<meta property="og:description">`.

11. **JMLR (`JMLRScraper`):**
    - Targets `div.abstract`, `div.paper-abstract`, or `div.abstractText`.
    - Fallback: Scans headers containing "abstract" for the immediate next paragraph.

12. **IJCAI (`IJCAIScraper`):**
    - Targets `div.abstract`, `div.paper-abstract`, or `section#abstract-content`.
    - Fallback 1: Parses JSON-LD metadata for `description`.
    - Fallback 2: Checks `<meta name="citation_abstract">` and `<meta name="description">`.

### Venue Scraper

We directly target high-impact conference websites known for their focus on the target research domain:
- **AAMAS:** International Conference on Autonomous Agents and Multiagent Systems
- **IJCAI:** International Joint Conference on Artificial Intelligence
- **AISTATS:** International Conference on Artificial Intelligence and Statistics
- **ICML:** International Conference on Machine Learning
- **ICLR:** International Conference on Learning Representations

#### Parallelized Scraping Mechanism
To speed up the process and reduce the overall runtime **up to 10 times compared to a sequential approach**, `src/venues.py` implements a parallelized scraping mechanism using `concurrent.futures.ThreadPoolExecutor`:

```python
with concurrent.futures.ThreadPoolExecutor() as executor:
    for venue_name, config in self.venues.items():
        for year in range(START_YEAR, END_YEAR + 1):
            future = executor.submit(scraper.fetch_papers_for_year, year)
            future_to_year[future] = (venue_name, year)
```

Each thread independently fetches proceedings for a specific venue and year, parses paper titles and links, retrieves abstracts, and filters candidate records.

### In-Memory PDF Abstract Extraction

For conferences whose proceedings lack dedicated HTML landing pages for individual abstracts (such as AAMAS via IFAAMAS proceedings), the scraper downloads the paper PDF directly into an in-memory byte buffer (`io.BytesIO`) using `PyPDF2.PdfReader` without writing temporary files to disk:

1. **Extended Abstract Handling:** Checks the first page for `\bExtended Abstract\b`. Extended abstracts are skipped to retain only full archival papers.
2. **Boundary Extraction:** Uses regular expressions to extract the abstract between the `ABSTRACT` header and the beginning of the next section:
   ```python
   pattern = r'\bABSTRACT\b\s*(.*?)(?=\b(?:Introduction|1\s+INTRODUCTION|Keywords)\b)'
   abstract_match = re.search(pattern, first_page, re.DOTALL | re.IGNORECASE)
   ```
3. **Text Normalization:** Cleans redundant formatting, removes newline splits, and strips Excel-specific artifacts such as `_x000D_`.

### Handling Anti-Scraping Measures & Network Delays

We made sure to handle the scraping limitations imposed by the publishers, such as rate limiting and CAPTCHAs, by incorporating appropriate delays and error handling mechanisms:

- **User-Agent Cycling:** `src/utils.py` maintains an active pool of 24 distinct browser user-agents across desktop and mobile platforms (Chrome, Firefox, Safari, Opera). Requests cycle through user agents via `itertools.cycle` to prevent client fingerprinting.
- **Request Delays:** 
  - Standard polite delay (`request_delay = 0.2s`) between requests.
  - A 2-second sleep interval between Google Scholar page requests.
- **ScienceDirect Anti-Scraping Handling:** Enforces an **11-second minimum interval** between consecutive calls:
  ```python
  delay = current_time - last_check
  if delay.total_seconds() <= 10:
      time.sleep(11 - delay.total_seconds())
  ```
  If Cloudflare verification or CAPTCHAs cannot be solved automatically, manual intervention is supported so papers can still be retrieved without loss.
- **Defensive Error Handling:** All network calls use explicit timeouts and exception logging to ensure transient request failures do not interrupt long-running scrapes.

### Keyword Bags & Combinatorial Formulation

Using keyword bags containing numerous relevant words to the targeted field, `sci-scraper` builds a logical combination that helps selecting the most likely papers to be relevant to the AOI through query combinations.

Defaults in `src/config/keywords.json` are structured into 5 bags:
- **`adversarial` (21 keywords):** *adversarial, attack, attacks, robust, robustness, defense, defenses, defensive, corruption, evasion, backdoor, poisoning, injection, black-box, white-box, gray-box, perturbation, malicious agent, malicious agents, adversarial intent, byzantine.*
- **`marl` (13 keywords):** *multi-agent reinforcement learning, multi-agent rl, multi-agent deep reinforcement learning, multi-agent drl, cooperative multi-agent reinforcement learning, madrl, marl, cmarl, c-marl, pomdp, dec-mdp, maddpg, mappo, masac.*
- **`game_theory` (8 keywords):** *mean field, mean-field, mfg, mfgs, game theory, Game-Theoretic, stochastic game, zero-sum.*
- **`rl` (21 keywords):** *reinforcement learning, deep reinforcement, inverse reinforcement, drl, rl, irl, mdp, q-learning, sarsa, actor-critic, policy gradient, deep q, ddpg, dqn, ppo, trpo, a3c, sac, td3, dpg.*
- **`multi_agent` (5 keywords):** *multi-agent, multiagent, multi agent, cooperative, competitive.*

The combination structure is evaluated as:

$$\text{Adversarial} \land ((\text{MARL}) \lor (\text{GA}) \lor (\text{RL} \land \text{MA}))$$

### Summary Comparison of Scraper Parameters

The table below summarizes the parameters used across both scraping components:

| Parameter | Scholar Scraper | Venue Scraper |
| :--- | :--- | :--- |
| **Top $K$ pages** | 50 | N/A |
| **Time lapse** | N/A | 01/01/2018 to 07/01/2025 |
| **Keyword Bags** | RL, MARL, GA, Adversarial | RL, MARL, GA, Adversarial |

The results from both components are merged into a unified dataset stored in an Excel file containing five columns: *Title*, *Abstract*, *Year*, *Source*, and *URL*.

---

## Configuration

Configurations are loaded from JSON files for easy customization without editing code. Defaults are set for adversarial multi-agent reinforcement learning (MARL), but can be adjusted for any domain:

- **`config.json`** (in `src/config/`): Adjust scraping parameters, queries, and LLM settings:
  - `start_year`: Start year for time range (default: 2018).
  - `end_year`: End year for time range (default: 2024).
  - `request_delay`: Delay between requests in seconds (default: 0.2) for ethical scraping.
  - `headers`: HTTP headers (e.g., User-Agent) to mimic browser requests.
  - `num_pages`: Number of Google Scholar pages to scrape (default: 50).
  - `scholar_query`: Complex query string for Google Scholar (supports OR, AND, exact phrases).
  - `api_key`: Hugging Face API key for LLM access.
  - `model_url`: LLM model path (default: `"microsoft/Phi-3-mini-4k-instruct"`).

- **`keywords.json`** (in `src/config/`): Define keyword bags for venue scraping and lexical filtering. Edit these lists to adapt the tool to any research field.

- **`venues.json`** (in `src/config/`): Define venue proceeding URL templates, DOM selectors, and volume mappings for AAMAS, IJCAI, AISTATS, ICML, and ICLR. Add new venues by extending this JSON configuration.

---

## Case Study: Adversarial MARL Survey (ACM CSUR)

As a concrete demonstration, `sci-scraper` was utilized to construct the literature corpus for our ACM Computing Surveys article:

1. **Initial Lexical Dataset:** Through iterative experimentation with keyword combinations and query strings, we curated an initial dataset of **647 papers** based on lexical matching.
2. **Automated Semantic Filtering:** We employed Microsoft's **Phi-3.5** model via Hugging Face Hub with a carefully engineered prompt to evaluate paper relevance from titles and abstracts. This reduced the dataset from **647** to **148 papers**.
   - In a manual audit of 60 papers marked as irrelevant, no false negatives were identified, demonstrating high recall in practice and significantly reducing subsequent manual review effort.
3. **Topic Modeling with BERTopic:** The corpus was analyzed using Sentence-BERT (SBERT), UMAP dimensionality reduction, HDBSCAN clustering, CountVectorizer, c-TF-IDF weighting, and KeyBERT with Maximal Marginal Relevance (MMR). See [`notebooks/README.md`](notebooks/README.md) for full reproduction instructions. This clustered the surveyed literature into four primary themes:
   - **Attacks**
   - **Defenses**
   - **Communication**
   - **Applications**

---

## Ethical Considerations

Respect site terms, robots.txt, and laws. Use delays to avoid overload. Not for unauthorized bulk scraping. ScienceDirect may need manual steps.

## Limitations

- Site layout changes can break scrapers.
- Lexical filters may need semantic post-processing.
- No full-text PDF downloads (metadata only).

## Future Work

- Add more publishers/venues.
- GUI for easier use (ongoing; see `web/app.py`, `web/templates/`, and `web/static/`).
- User control over the logic of keyword combinations.

## Contributing

Pull requests welcome! For major changes, open an issue first. Focus on:
- New publisher/venue support.
- Bug fixes.
- Documentation improvements.

---

## License

[MIT](LICENSE) — Copyright (c) 2025 Hamza Ba-mohammed, Latifa El Bouga, Amine Andam, Mostapha Essoullami, Douae Benhlima, Jamal Bentahar, Mustapha Hedabou.

---

## Citation

If you use `sci-scraper` in your research or literature review, please cite our survey paper:

```bibtex
@article{bamohammed2025survey,
  title={A Survey on Adversarial Multi-Agent Deep Reinforcement Learning},
  author={Ba-mohammed, Hamza and El Bouga, Latifa and Andam, Amine and Essoullami, Mostapha and Benhlima, Douae and Hedabou, Mustapha and Bentahar, Jamal},
  journal={ACM Computing Surveys},
  year={2025},
  note={Under revision (CSUR-2025-1595)}
}
```

---

## Acknowledgments

Built with open-source libraries like BeautifulSoup and pandas. Thanks to the communities behind BERTopic and Hugging Face for inspiration on analysis pipelines.