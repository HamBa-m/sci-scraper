# main.py
import argparse

from scholar_scraper import ScholarScraper
from data_handler import DataHandler

def main(query, num_pages):
    # Initialize scrapers
    scholar_scraper = ScholarScraper(query=query, num_pages=num_pages)
    
    # Scrape Google Scholar and save results
    results = scholar_scraper.scrape()
    data_handler = DataHandler()
    
    # Save results to Excel
    data_handler.save_to_excel(results, "{}_results.xlsx".format(query))
    print("\nResults have been saved to {}_results.xlsx".format(query))
    
    # Show summary statistics
    data_handler.calculate_statistics(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Google Scholar abstracts based on query.")
    parser.add_argument("query", type=str, help="The search query for Google Scholar")
    parser.add_argument("num_pages", type=int, help="The number of pages to scrape")
    
    args = parser.parse_args()
    main(query=args.query, num_pages=args.num_pages)
