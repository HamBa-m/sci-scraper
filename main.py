#!/usr/bin/env python3
"""
Main CLI entrypoint for Sci-Scraper.
Allows running the scraping pipeline, venue harvesters, and LLM semantic filter directly from the project root.
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
import logging

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.scholar import ScholarScraper
from src.venues import VenueScraper
from src.llm_agent import AgentLLM
from src.config import setup_logging, RESULTS_DIR

def run_pipeline(mode: str = 'all', filter_papers: bool = False):
    """Run the scientific paper scraping and filtering pipeline."""
    setup_logging("main.log")
    logging.info(f"=== Starting Sci-Scraper CLI in mode: {mode} (filter={filter_papers}) ===")

    final_df = None

    if mode == 'none':
        logging.info("No scraping tasks selected.")
    elif mode == 'scholar':
        scholar_scraper = ScholarScraper()
        final_df = scholar_scraper.scrape()
    elif mode == 'venues':
        venue_scraper = VenueScraper()
        final_df = venue_scraper.scrape_venues()
    elif mode == 'all':
        logging.info("Step 1/2: Scraping Google Scholar...")
        scholar_scraper = ScholarScraper()
        scholar_df = scholar_scraper.scrape()

        logging.info("Step 2/2: Scraping targeted conference venues...")
        venue_scraper = VenueScraper()
        venue_df = venue_scraper.scrape_venues()

        # Merge and deduplicate
        final_df = pd.concat([scholar_df, venue_df], ignore_index=True)
        final_df.drop_duplicates(subset=["Title"], inplace=True)
        output_file = RESULTS_DIR / "all_results.xlsx"
        final_df.to_excel(str(output_file), index=False)
        logging.info(f"Scraping completed. {len(final_df)} unique papers saved to {output_file}.")

    if filter_papers:
        if final_df is not None:
            logging.info(f"Filtering {len(final_df)} freshly scraped papers from mode '{mode}' using LLM model...")
            papers_df = final_df
        else:
            input_file = RESULTS_DIR / "all_results.xlsx"
            if not input_file.exists():
                error_msg = f"Cannot filter: {input_file} does not exist. Run with --mode all first, or scrape before filtering."
                logging.error(error_msg)
                print(f"Error: {error_msg}", file=sys.stderr)
                return 1
            
            logging.info(f"Starting LLM semantic filtering on {input_file}...")
            papers_df = pd.read_excel(str(input_file))
            
        llm_agent = AgentLLM()
        filtered_df = llm_agent.filter_papers(papers_df)
        llm_agent.save_results(filtered_df)
        logging.info("LLM semantic filtering completed.")

    logging.info("Sci-Scraper run completed successfully.")
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Sci-Scraper: Automated scientific literature harvesting and curation pipeline."
    )
    parser.add_argument(
        "--mode",
        choices=["scholar", "venues", "all", "none"],
        default="all",
        help="Scraping mode: 'scholar' (Google Scholar only), 'venues' (Conferences only), 'all' (Both), 'none' (Skip scraping)."
    )
    parser.add_argument(
        "--filter",
        action="store_true",
        default=False,
        help="Apply LLM-based semantic filtering (Phi-3.5) on the resulting or existing all_results.xlsx."
    )
    args = parser.parse_args()
    sys.exit(run_pipeline(mode=args.mode, filter_papers=args.filter))

if __name__ == "__main__":
    main()
