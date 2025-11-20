# scholar_scraper.py
import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import logging
import os
import json

from .scholar_scrapers import (
    IeeeScraper, SpringerScraper, MlrScraper, ArxivScraper,
    NeuripsScraper, MdpiScraper, ScienceDirectScraper, ACMScraper,
    AAAIScraper, JAIRScraper, JMLRScraper, IJCAIScraper
)
from .utils import detect_source, extract_year

##### Load configuration
current_dir = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(current_dir, 'config.json')
with open(config_file, 'r') as f:
    config = json.load(f)
    
NUM_PAGES = config['num_pages']
SCHOLAR_QUERY = config['scholar_query']

##### Main class
class ScholarScraper:
    def __init__(self, query = SCHOLAR_QUERY, num_pages = NUM_PAGES):
        self.query = query
        self.num_pages = num_pages
        self.scrapers = {
            'IEEE': IeeeScraper(),
            'Springer': SpringerScraper(),
            'MLR': MlrScraper(),
            'ACM': ACMScraper(),
            'NeurIPS': NeuripsScraper(),
            'MDPI': MdpiScraper(),
            'ScienceDirect': ScienceDirectScraper(),
            'AAAI': AAAIScraper(),
            'JAIR': JAIRScraper(),
            'JMLR': JMLRScraper(),
            'IJCAI': IJCAIScraper(),
            'arXiv': ArxivScraper()
        }

    def scrape(self, callback=None):
        base_url = "https://scholar.google.com/scholar"
        results = []
        last_check = None  # for ScienceDirect rate-limiting
        logging.info(f"=== Scraping Google Scholar for query: {self.query} ===")
        for page in tqdm(range(self.num_pages), desc='Scholar pages processed', unit='page'):
            params = {'q': self.query, 'start': page * 10, 'hl': 'en'}
            response = requests.get(base_url, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', class_='gs_ri')
            for article in articles:
                title_elem = article.find('h3', class_='gs_rt')
                title = title_elem.text if title_elem else 'No title'
                link_elem = title_elem.find('a') if title_elem else None
                link = link_elem['href'] if link_elem else 'No link'
                citation = article.find('div', class_='gs_a')
                
                # Detect the source and retrieve abstract
                source = detect_source(link)
                # if source == 'arXiv':
                #     continue # Skip arXiv papers
                abstract = None
                if source in self.scrapers:
                    scraper = self.scrapers[source]
                    if source == 'ScienceDirect' and isinstance(scraper, ScienceDirectScraper):
                        abstract, last_check = scraper.get_abstract(link, last_check)
                    else:
                        abstract = scraper.get_abstract(link)
                        
                paper_data = {
                    'Title': title,
                    'URL': link,
                    'Abstract': abstract,
                    'Source': source,
                    'Year': extract_year(citation.text) if citation else None
                }
                results.append(paper_data)
                
                logging.info(f"Processed article: {title[:50]}... | Source: {source} | Abstract found: {'Yes' if abstract else 'No'}")
                
                time.sleep(2)  # Delay to avoid blocking
                # Update progress
                if callback:
                    callback(page, self.num_pages, paper_data)
        
        # convert to dataframe
        df = pd.DataFrame(results, columns=['Title', 'URL', 'Abstract', 'Source', 'Year'])
        # save to excel
        output_file = "./results/scholar_results.xlsx"
        df.to_excel(output_file, index=False)
        logging.info(f"Scraping completed. {len(df)} papers saved to {output_file}.")
        return df
