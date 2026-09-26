# main.py
import argparse
import pandas as pd
import logging

try:
    from .scholar import ScholarScraper
    from .venues import VenueScraper
    from .llm_agent import AgentLLM
    from .config import setup_logging, RESULTS_DIR
except (ImportError, ValueError):
    from scholar import ScholarScraper
    from venues import VenueScraper
    from llm_agent import AgentLLM
    from config import setup_logging, RESULTS_DIR

# Configure centralized logging
setup_logging("main.log")

def main():
    parser = argparse.ArgumentParser(description='Scrape papers from Google Scholar and conferences')
    parser.add_argument('--mode',
                        help='Choose the scraping mode: scholar, venues, all, none',
                        type=str,
                        choices=['scholar', 'venues', 'all', 'none'],
                        default='all')
    parser.add_argument('--filter', help='Filter papers using LLM model', type=bool, nargs='?', const=True, default=False)
    args = parser.parse_args()

    if args.mode == 'none':
        logging.info("No scraping tasks selected. Exiting program.")
        
    elif args.mode == 'scholar':
        scholar_scraper = ScholarScraper()
        final_df = scholar_scraper.scrape()
        
    elif args.mode == 'venues':
        venue_scraper = VenueScraper()
        final_df = venue_scraper.scrape_venues()
        
    elif args.mode == 'all':
        scholar_scraper = ScholarScraper()
        scholar_df = scholar_scraper.scrape()
        venue_scraper = VenueScraper()
        venue_df = venue_scraper.scrape_venues()
        
        # merge scholar and venue dataframes
        final_df = pd.concat([scholar_df, venue_df], ignore_index=True)
        final_df.drop_duplicates(subset=["Title"], inplace=True)
        output_file = str(RESULTS_DIR / "all_results.xlsx")
        final_df.to_excel(output_file, index=False)
        logging.info(f"Scraping completed. {len(final_df)} papers saved to {output_file}.")
        logging.info("All scraping tasks completed.")
    
    else:
        logging.error("Invalid mode. Please choose from 'scholar', 'venues', 'all'.")
    
    if args.filter:
        llm_agent = AgentLLM()
        final_df = pd.read_excel(str(RESULTS_DIR / "all_results.xlsx"))
        filtered_df = llm_agent.filter_papers(final_df)
        llm_agent.save_results(filtered_df)
        logging.info("Filtering completed.")
        
    return

if __name__ == '__main__':
    main()