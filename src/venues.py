import logging
import concurrent.futures
import pandas as pd
from venues_scrapers import AAMASScraper, IJCAIScraper, AISTATSScraper, ICMLScraper, ICLRScraper, START_YEAR, END_YEAR
import json
import os

# Load venue configurations from JSON file
current_dir = os.path.dirname(__file__)
venues_file = os.path.join(current_dir, 'venues.json')
with open(venues_file, 'r') as f:
    VENUES = json.load(f)

class VenueScraper:
    def __init__(self, venues = VENUES):
        self.venues = venues

    def scrape_venues(self):
        all_papers = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_year = {}

            for venue_name, config in self.venues.items():
                logging.info(f"=== Scraping Venue: {venue_name} ===")
                if venue_name == "AAMAS":
                    scraper = AAMASScraper(venue_name, config)
                elif venue_name == "IJCAI":
                    scraper = IJCAIScraper(venue_name, config)
                elif venue_name == "AISTATS":
                    scraper = AISTATSScraper(venue_name, config)
                elif venue_name == "ICML":
                    scraper = ICMLScraper(venue_name, config)
                elif venue_name == "ICLR":
                    scraper = ICLRScraper(venue_name, config)
                else:
                    continue

                for year in range(START_YEAR, END_YEAR + 1):
                    future = executor.submit(scraper.fetch_papers_for_year, year)
                    future_to_year[future] = (venue_name, year)

            for future in concurrent.futures.as_completed(future_to_year):
                venue_name, year = future_to_year[future]
                try:
                    papers = future.result()
                    all_papers.extend(papers)
                    logging.info(f"Completed processing for {venue_name} {year} with {len(papers)} papers.")
                except Exception as exc:
                    logging.error(f"Error occurred while processing {venue_name} {year}: {exc}")

        df = pd.DataFrame(all_papers)
        df.drop_duplicates(subset=["Title", "Year", "Source"], inplace=True)

        output_file = "./results/venues_results.xlsx"
        df.to_excel(output_file, index=False)
        logging.info(f"Scraping completed. {len(df)} papers saved to {output_file}.")
        return df