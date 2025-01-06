# main.py
import argparse
import pandas as pd
import logging

from scholar import ScholarScraper
from venues import VenueScraper

from llm_agent import AgentLLM

# Configure logging to use UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/main.log', encoding='utf-8')
    ]
)

def main():
    parser = argparse.ArgumentParser(description='Scrape papers from Google Scholar and conferences')
    parser.add_argument('--mode',
                        help='Choose the scraping mode: scholar, venues, all',
                        required=True,
                        type=str,
                        choices=['scholar', 'venues', 'all'],
                        default='all')
    parser.add_argument('--filter', help='Filter papers using LLM model', type=bool, nargs='?', const=True, default=False)
    parser.add_argument('--classify', help='Classify papers using LLM model', type=bool, nargs='?', const=True, default=False)
    args = parser.parse_args()

    if args.mode == 'scholar':
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
        output_file = "./results/all_results.xlsx"
        final_df.to_excel(output_file, index=False)
        logging.info(f"Scraping completed. {len(final_df)} papers saved to {output_file}.")
        logging.info("All scraping tasks completed.")
    
    else:
        logging.error("Invalid mode. Please choose from 'scholar', 'venues', 'all'.")
        return
    
    if args.filter:
        llm_agent = AgentLLM()
        filtered_df = llm_agent.filter_papers(final_df)
        llm_agent.save_results(filtered_df)
        logging.info("Filtering completed.")
        if args.classify:
            llm_agent.classify_papers(filtered_df)
            logging.info("Classification completed.")
    
    if args.classify and not args.filter:
        logging.error("Cannot classify papers without filtering them first. Please set the --filter flag to True.")
        return
        
if __name__ == '__main__':
    main()