# Sci-Scraper

[![Python Version](https://img.shields.io/badge/Python-3.8.19%2B-blue.svg)](https://www.python.org/downloads/) [![GitHub Repo stars](https://img.shields.io/github/stars/HamBa-m/sci-scraper?style=social)](https://github.com/HamBa-m/sci-scraper/stargazers) [![GitHub issues](https://img.shields.io/github/issues/HamBa-m/sci-scraper)](https://github.com/HamBa-m/sci-scraper/issues) [![GitHub forks](https://img.shields.io/github/forks/HamBa-m/sci-scraper?style=social)](https://github.com/HamBa-m/sci-scraper/network/members) [![GitHub license](https://img.shields.io/github/license/HamBa-m/sci-scraper)](https://github.com/HamBa-m/sci-scraper/blob/main/LICENSE) 

A Python-based web scraping tool for collecting scientific literature from Google Scholar and academic venues. Extracts metadata like titles, abstracts, years, sources, and URLs into structured Excel files. Modular and extensible for various research domains.

## Features

- **Scholar Scraper**: Searches Google Scholar for top results (configurable pages). Custom extractors for publishers including IEEE, Springer, ArXiv, NeurIPS, MDPI, ScienceDirect (manual mode), ACM, AAAI, JAIR, JMLR.
- **Venues Scraper**: Targets specific conferences/journals with keyword-based filtering and time ranges.
- Parallel processing for faster scraping (up to 10x speedup).
- Ethical features: Rate limiting, delays, error handling.
- Output: Merged Excel datasets for easy analysis.
- Supports downstream workflows like lexical filtering, semantic filtering (e.g., via LLMs), and topic modeling (e.g., BERTopic).

## Workflow Overview

The tool fits into a pipeline:
- Scraping → Lexicographical (keyword) filtering.
- Semantic Filtering: Automated (LLM-based) + Manual review.
- Topic Modeling: Embedding (SBERT), Reduction (UMAP), Clustering (HDBSCAN), Vectorization (CountVectorizer), Weighting (c-TF-IDF), Representation (KeyBERT/MMR). Includes semi-supervised zero-shot and manual merging.

![g_pipeline](g_pipeline.png#gh-light-mode-only)
![g_pipeline](g_pipeline.png#gh-dark-mode-only)

## Installation

```bash
git clone https://github.com/HamBa-m/sci-scraper.git
cd sci-scraper
pip install -r requirements.txt  
```

## Usage

Run the tool via the main script in the `src/` folder using command-line arguments.

```bash
cd src
python main.py --mode [scholar|venues|all|none] --filter [True/False]
```

- `--mode`: Select scraping mode (default: `all`).
  - `scholar`: Scrape from Google Scholar only.
  - `venues`: Scrape from targeted venues only.
  - `all`: Scrape both, merge, remove duplicates by title, and save to `./results/all_results.xlsx`.
  - `none`: Skip scraping (useful with `--filter` if data already exists).
- `--filter`: (Optional) Apply LLM-based semantic filtering to refine results (reads from `./results/all_results.xlsx` and saves filtered output).

### Examples

- Scrape everything and save merged results:
  ```bash
  python main.py --mode all
  ```

- Scrape venues only (no auto-save; access dataframe in code for manual saving):
  ```bash
  python main.py --mode venues
  ```

- Filter existing data without scraping:
  ```bash
  python main.py --mode none --filter
  ```

- Scrape all and filter in one run:
  ```bash
  python main.py --mode all --filter
  ```

Logs are saved to `log/main.log`. Results (for `all` mode) are in `./results/`. For advanced usage or customization, import classes directly (e.g., in scripts):

```python
from scholar import ScholarScraper
from venues import VenueScraper
from llm_agent import AgentLLM

# Example: Custom scraping
scholar = ScholarScraper()
df_scholar = scholar.scrape()

venue = VenueScraper()
df_venue = venue.scrape_venues()

# Merge and save
merged_df = pd.concat([df_scholar, df_venue]).drop_duplicates(subset=["Title"])
merged_df.to_excel("../results/custom_results.xlsx", index=False)

# Filter
if filter_needed:
    agent = AgentLLM()
    filtered = agent.filter_papers(merged_df)
    agent.save_results(filtered)
```

Check `examples/` for more scripts.

### Configuration

Configurations are loaded from JSON files for easy customization without editing code. Defaults are set for adversarial multi-agent reinforcement learning (MARL), but can be adjusted for any domain.

- **config.json** (e.g., in `src/`): Adjust scraping parameters, queries, and LLM settings.
  - `start_year`: Start year for time range (default: 2018).
  - `end_year`: End year for time range (default: 2024).
  - `request_delay`: Delay between requests in seconds (default: 0.2) for ethical scraping.
  - `headers`: HTTP headers (e.g., User-Agent) to mimic browser requests.
  - `num_pages`: Number of Google Scholar pages to scrape (default: 50).
  - `scholar_query`: Complex query string for Google Scholar (supports OR, AND, exact phrases; default: adversarial MARL-related terms).
  - `api_key`: Hugging Face API key for LLM access (replace "YOUR_API_KEY_HERE").
  - `model_url`: LLM model path (default: "microsoft/Phi-3-mini-4k-instruct").

- **keywords.json** (e.g., in `src/`): Define keyword bags for venue scraping and lexical filtering.
  - Categories like "adversarial", "marl", "game_theory", "rl", "multi_agent" with lists of terms.
  - Used to form logical combinations, e.g., Adversarial ∧ (MARL ∨ Game Theory ∨ (RL ∧ Multi-Agent)).

Edit these JSON files to change queries, keywords, API keys, time ranges, or Scholar pages. Reload by running the script again. Add new publishers or venues by extending the classes in code if needed.

## Ethical Considerations

Respect site terms, robots.txt, and laws. Use delays to avoid overload. Not for unauthorized bulk scraping. ScienceDirect may need manual steps.

## Limitations

- Site layout changes can break scrapers.
- Lexical filters may need semantic post-processing.
- No full-text PDF downloads (metadata only).

## Future Work
- Add more publishers/venues.
- GUI for easier use. (ongoing, see ```app.py``` and ```templates/``` / ```static/``` folders)
- Control over the logic of keyword combinations.

## Contributing

Pull requests welcome! For major changes, open an issue first. Focus on:
- New publisher/venue support.
- Bug fixes.
- Documentation improvements.

## License

[MIT](LICENSE)

## Citation

[To be added upon arXiv publication of the associated paper.]

## Acknowledgments

Built with open-source libs like BeautifulSoup and pandas. Thanks to communities behind BERTopic and Hugging Face for inspiration on analysis pipelines.