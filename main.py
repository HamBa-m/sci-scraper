# main.py
import argparse
import time

from scholar import ScholarScraper
from data_handler import DataHandler

def main(query, num_pages):
    # Initialize scrapers
    scholar_scraper = ScholarScraper(query=query, num_pages=num_pages)
    
    # Scrape Google Scholar and save results
    results = scholar_scraper.scrape()
    data_handler = DataHandler()
    
    # Save results to Excel
    data_handler.save_to_excel(results, "{}_results.xlsx".format(time.strftime("%Y%m%d-%H%M%S")))
    print("\nResults have been saved to {}_results.xlsx".format(time.strftime("%Y%m%d-%H%M%S")))
    
    # Show summary statistics
    data_handler.calculate_statistics(results)

test_query = '(adversarial OR attack OR attacks OR robust OR robustness OR defense OR defenses OR defensive OR corruption) AND ((("reinforcement learning" OR drl OR rl) AND ("multi-agent")) OR (madrl OR marl))'
# test_query = 'multi-agent reinforcement learning adversarial attacks'

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Scrape Google Scholar abstracts based on query.")
    # parser.add_argument("query", type=str, help="The search query for Google Scholar", default=test_query)
    # parser.add_argument("num_pages", type=int, help="The number of pages to scrape", default=50)
    
    # args = parser.parse_args()
    main(query=test_query, num_pages=20)
