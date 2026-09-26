# Results & Datasets Directory

This directory contains the intermediate and final datasets produced throughout the literature collection and processing pipeline for our survey paper:
> **"A Survey on Adversarial Multi-Agent Deep Reinforcement Learning"** (*ACM Computing Surveys*, CSUR-2025-1595).

---

## Dataset Inventory & Pipeline Stages

| File Name | Records | Columns | Pipeline Stage & Description |
| :--- | :---: | :--- | :--- |
| **`scholar_results.xlsx`** | 370 | `Title, URL, Abstract, Source, Year` | **Data Collection (Scholar):** Raw search results harvested from Google Scholar using the Boolean query string across top $K=50$ pages, with abstracts parsed via custom publisher extractors. |
| **`venues_results.xlsx`** | 285 | `Title, Abstract, Year, Source, URL` | **Data Collection (Venues):** Results from targeted conference proceedings (AAMAS, IJCAI, AISTATS, ICML, ICLR; 2018–2024) filtered via the 5 keyword bags propositional formula. |
| **`all_results.xlsx`** | 647 | `Title, URL, Abstract, Source, Year` | **Merged Lexical Corpus:** Combined and deduplicated dataset of Scholar and Venue scrapers (produced by running `python main.py --mode all`). |
| **`filtred_papers.xlsx`** | 647 | `Title, URL, Abstract, Source, Year, is_relevent, Verdict` | **LLM Semantic Evaluation:** The full 647 lexical corpus annotated with automated relevance classifications and rationale (`Verdict`) produced by Microsoft's **Phi-3.5** model. |
| **`merged_results.xlsx`** | 148 | `Title, Source, Year, Abstract, URL, Q Index, Verdict` | **Filtered Relevant Corpus:** The 148 candidate papers deemed relevant after the automated LLM filtering stage, enriched with journal/conference quality rankings. |
| **`relevant_papers.xlsx`** | 105 | `Title, URL, Abstract, Source, Year, Verdict` | **Curated Candidate Set:** Refined candidate subset used during intermediate screening. |
| **`old_results.xlsx`** | 84 | 19 attributes (taxonomic labels) | **Exploratory Taxonomy Matrix:** Early exploratory matrix classifying candidate papers across attack surfaces, defense mechanisms, and multi-agent settings. |

---

## Schema & Column Definitions

- **`Title`**: Cleaned, normalized title of the publication (whitespace collapsed, newline and formatting artifacts removed).
- **`URL`**: Canonical DOI or direct publisher landing URL.
- **`Abstract`**: Extracted paper abstract (retrieved via HTML DOM, meta-tags, JSON-LD, or in-memory PDF parsing).
- **`Source`**: Normalized academic venue or publisher (e.g., *IEEE, Springer, ACM, NeurIPS, AAMAS, AAAI, ICML, ICLR*).
- **`Year`**: Publication year.
- **`is_relevent` / `Verdict`**: Binary relevance flag and explanation generated during LLM semantic filtering.
- **`Q Index`**: Scimago / Core venue quality ranking cluster (e.g., *A\*, A, Q1, Q2*).

---

## Reproducing Datasets

To re-run the data collection and filtering from scratch:

```bash
# Scrape both sources, merge, and output to all_results.xlsx
cd src
python main.py --mode all

# Run LLM semantic filtering on all_results.xlsx
python main.py --mode none --filter
```
