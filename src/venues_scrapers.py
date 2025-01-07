import requests
from bs4 import BeautifulSoup
import time
import re
import tqdm
from urllib.parse import urljoin
from PyPDF2 import PdfReader
import io
import logging
import json
import os

# -------------------- Configuration -------------------- #

# Import keywords from a separate JSON file
current_dir = os.path.dirname(os.path.realpath(__file__))
keywords_file = os.path.join(current_dir, 'keywords.json')
with open(keywords_file, 'r') as f:
    KEYWORDS = json.load(f)

KEYWORDS_ADVERSARIAL = KEYWORDS["adversarial"]
KEYWORDS_RL = KEYWORDS["rl"]
KEYWORDS_MULTI_AGENT = KEYWORDS["multi_agent"]
KEYWORDS_MARL = KEYWORDS["marl"]
KEYWORDS_GAME_THEORY = KEYWORDS["game_theory"]

# Other configurations
config_file = os.path.join(current_dir, 'config.json')
with open(config_file, 'r') as f:
    config = json.load(f)
    
START_YEAR = config["start_year"]
END_YEAR = config["end_year"]
HEADERS = config["headers"]
REQUEST_DELAY = config["request_delay"]
# -------------------------------------------------------- #
class BaseScraper:
    def __init__(self, venue_name, config):
        self.venue_name = venue_name
        self.config = config
        self.base_url = config["base_url"]
        self.proceedings_url_template = config["proceedings_url_template"]
        self.paper_wrapper_class = config["paper_wrapper_class"]
        self.abstract_page_selector = config["abstract_page_selector"]
        self.venue_display_name = config["venue_name"]

    def fetch_html(self, url):
        """Fetches the HTML content of a given URL."""
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    def extract_paper_links(self, proceedings_html, proceedings_url):
        """Extracts paper links from the proceedings page."""
        raise NotImplementedError("Subclasses must implement this method")

    def extract_paper_details(self, paper_info, year):
        """Extracts paper details based on the venue."""
        raise NotImplementedError("Subclasses must implement this method")

    def clean_title(self, title):
        """Remove redundant _x000D_, newline characters, and extra whitespace from titles"""
        title = re.sub(r'_x000D_', '', title)
        title = re.sub(r'\s+', ' ', title)
        return title.strip()

    def extract_abstract_from_pdf(self, pdf_url):
        """Extract abstract from PDF paper"""
        try:
            response = requests.get(pdf_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            pdf_file = io.BytesIO(response.content)
            reader = PdfReader(pdf_file)
            
            first_page = reader.pages[0].extract_text()
            
            if re.search(r'\bExtended Abstract\b', first_page, re.IGNORECASE):
                return "Extended Abstract found. Skipping extraction."
            else:
                pattern = r'\bABSTRACT\b\s*(.*?)(?=\b(?:Introduction|1\s+INTRODUCTION|Keywords)\b)'
                abstract_match = re.search(pattern, first_page, re.DOTALL | re.IGNORECASE)

                if abstract_match:
                    abstract = abstract_match.group(1).strip()
                    abstract = ' '.join(abstract.split())
                    return abstract
                else:
                    return "Abstract extraction failed"
            
        except Exception as e:
            logging.error(f"Error extracting abstract from {pdf_url}: {e}")
            return "Abstract extraction failed"

    def paper_contains_keywords(self, title, abstract):
        """
        Checks if a paper is about adversarial aspects of multi-agent RL by verifying
        it contains terms from all three concept sets while excluding single-agent papers.
        
        Args:
            title (str): Paper title
            abstract (str): Paper abstract
            
        Returns:
            bool: True if paper is about adversarial attacks/defenses in MARL
        """
        combined_text = f"{title} | {abstract}".lower()
        
        # Check presence of at least one term from each concept set
        has_multi_agent = any(kw.lower() in combined_text for kw in KEYWORDS_MULTI_AGENT)
        has_rl = any(kw.lower() in combined_text for kw in KEYWORDS_RL)
        has_adversarial = any(kw.lower() in combined_text for kw in KEYWORDS_ADVERSARIAL)
        has_marl = any(kw.lower() in combined_text for kw in KEYWORDS_MARL)
        has_game_theory = any(kw.lower() in combined_text for kw in KEYWORDS_GAME_THEORY)
        
        # If it has :
        # - adversarial and MARL keywords
        # - adversarial and game theory keywords
        # - adversarial and multi-agent and RL keywords
        # then it is a relevant paper        
        if has_adversarial:
            if has_marl or has_game_theory:
                return True
            elif has_multi_agent and has_rl:
                return True
        
        # If none of the above conditions are met, return False
        return False
    
    def fetch_papers_for_year(self, year):
        all_papers_for_year = []
        logging.info(f"Processing {self.venue_display_name} {year}...")

        if self.venue_name == "AISTATS" or self.venue_name == "ICML":
            volume = self.config["year_mapping"].get(str(year))
            if not volume:
                logging.warning(f"No volume mapping found for year {year}. Skipping.")
                return []
            proceedings_url = self.proceedings_url_template.format(volume=volume)
        else:
            proceedings_url = self.proceedings_url_template.format(year=year)

        logging.info(f"Fetching proceedings page: {proceedings_url}")
        proceedings_html = self.fetch_html(proceedings_url)
        if not proceedings_html:
            logging.warning(f"Failed to fetch proceedings for {self.venue_display_name} {year}. Skipping.")
            return []

        # Pass the proceedings_url to extract_paper_links
        paper_details = self.extract_paper_links(proceedings_html, proceedings_url)
        
        for paper_info in tqdm.tqdm(paper_details, desc=f"Processing {self.venue_display_name} {year} papers"):
            details = self.extract_paper_details(paper_info, year)
            
            if details:
                title = details.get('Title', "")
                abstract = details.get('Abstract', "")
                if self.paper_contains_keywords(title, abstract):
                    all_papers_for_year.append(details)
                    logging.info(f"Found relevant paper: {title} | {year} | {details.get('URL', '')}")
                else:
                    logging.info(f"Skipping non-relevant paper: {title}")
            # break # for fast testing, remove this line to process all papers

        logging.info(f"Found {len(all_papers_for_year)} relevant papers for {self.venue_display_name} {year}.")
        time.sleep(REQUEST_DELAY * 10)
        
        return all_papers_for_year

class AAMASScraper(BaseScraper):
    def extract_paper_links(self, proceedings_html, proceedings_url):
        """Extracts paper links from AAMAS proceedings page."""
        soup = BeautifulSoup(proceedings_html, 'html.parser')
        paper_details = []
        
        # Find all table rows that contain paper information
        for row in soup.find_all('tr'):
            if not row.text.strip():
                continue
                
            # Find all paper titles and PDF links within the row
            for title_link in row.find_all('a', href=lambda x: x and x.endswith('.pdf')):
                title = title_link.get_text(strip=True)
                # Resolve the relative PDF path to a full URL using the proceedings URL as the base
                pdf_url = urljoin(proceedings_url, title_link['href'])
                
                paper_details.append({
                    'title': title,
                    'url': pdf_url
                })
        
        return paper_details

    def extract_paper_details(self, paper_info, year):
        """Creates paper details dictionary with abstract from PDF."""
        details = {
            'Title': self.clean_title(paper_info['title']),
            'Abstract': self.extract_abstract_from_pdf(paper_info['url']),
            'Year': year,
            'Source': "AAMAS",
            'URL': paper_info['url']
        }
        return details

class IJCAIScraper(BaseScraper):
    def extract_paper_links(self, proceedings_html, proceedings_url):
        """Extracts paper detail page links from IJCAI proceedings page."""
        soup = BeautifulSoup(proceedings_html, 'html.parser')
        paper_links = []

        for paper_div in soup.find_all('div', class_=self.paper_wrapper_class):
            details_div = paper_div.find('div', class_='details')
            if details_div:
                details_link = details_div.find('a', string=re.compile(r'Details', re.I))
                if details_link and 'href' in details_link.attrs:
                    paper_url = urljoin(self.base_url, details_link['href'])
                    paper_links.append(paper_url)
        return paper_links

    def extract_paper_details(self, paper_url, year):
        """Extracts paper details from IJCAI paper details page."""
        paper_html = self.fetch_html(paper_url)
        if not paper_html:
            return None

        soup = BeautifulSoup(paper_html, 'html.parser')
        details = {}

        title_tag = soup.find('meta', attrs={'name': 'citation_title'})
        if title_tag and 'content' in title_tag.attrs:
            details['Title'] = title_tag['content']
        else:
            details['Title'] = "N/A"

        abstract = ""
        abstract_tag = soup.find('div', class_='col-md-12')
        if abstract_tag:
            abstract = abstract_tag.get_text(separator=" ", strip=True)
        details['Abstract'] = abstract

        details['Source'] = "IJCAI"

        year_match = re.search(r'/proceedings/(\d{4})/', paper_url)
        if year_match:
            details['Year'] = int(year_match.group(1))
        else:
            details['Year'] = "N/A"
            
        details['URL'] = paper_url

        return details

class AISTATSScraper(BaseScraper):
    def extract_paper_links(self, proceedings_html, proceedings_url):
        """Extracts paper abstract page links from AISTATS proceedings page."""
        soup = BeautifulSoup(proceedings_html, 'html.parser')
        paper_links = []
        for paper_div in soup.find_all('div', class_=self.paper_wrapper_class):
            abs_link = paper_div.find('a', string=re.compile(r'abs', re.I))
            if abs_link and 'href' in abs_link.attrs:
                paper_url = urljoin(self.base_url, abs_link['href'])
                paper_links.append(paper_url)

        return paper_links

    def extract_paper_details(self, paper_url, year):
        """Extracts paper details from AISTATS paper abstract page."""
        paper_html = self.fetch_html(paper_url)
        if not paper_html:
            return None

        soup = BeautifulSoup(paper_html, 'html.parser')
        details = {}

        title_tag = soup.find('h1')
        if title_tag:
            details['Title'] = title_tag.get_text(strip=True)
        else:
            details['Title'] = "N/A"

        abstract = ""
        abstract_tag = soup.find('div', id='abstract')
        if abstract_tag:
            abstract = abstract_tag.get_text(separator=" ", strip=True)
        details['Abstract'] = abstract

        info_tag = soup.find('div', id='info')
        if info_tag:
            year_match = re.search(r',\s*(\d{4})\.', info_tag.get_text())
            if year_match:
                details['Year'] = int(year_match.group(1))
            else:
                details['Year'] = "N/A"
        else:
            details['Year'] = "N/A"

        details['Source'] = "AISTATS"
        
        details['URL'] = paper_url
        
        return details
    
class ICMLScraper(BaseScraper):
    def extract_paper_links(self, proceedings_html, proceedings_url):
        """Extracts paper abstract page links from ICML proceedings page."""
        soup = BeautifulSoup(proceedings_html, 'html.parser')
        paper_links = []
        for paper_div in soup.find_all('div', class_=self.paper_wrapper_class):
            abs_link = paper_div.find('a', string=re.compile(r'abs', re.I))
            if abs_link and 'href' in abs_link.attrs:
                paper_url = urljoin(self.base_url, abs_link['href'])
                paper_links.append(paper_url)

        return paper_links

    def extract_paper_details(self, paper_url, year):
        """Extracts paper details from ICML paper abstract page."""
        paper_html = self.fetch_html(paper_url)
        if not paper_html:
            return None

        soup = BeautifulSoup(paper_html, 'html.parser')
        details = {}

        title_tag = soup.find('h1')
        if title_tag:
            details['Title'] = title_tag.get_text(strip=True)
        else:
            details['Title'] = "N/A"

        abstract = ""
        abstract_tag = soup.find('div', id='abstract')
        if abstract_tag:
            abstract = abstract_tag.get_text(separator=" ", strip=True)
        details['Abstract'] = abstract

        info_tag = soup.find('div', id='info')
        if info_tag:
            year_match = re.search(r',\s*(\d{4})\.', info_tag.get_text())
            if year_match:
                details['Year'] = int(year_match.group(1))
            else:
                details['Year'] = "N/A"
        else:
            details['Year'] = "N/A"

        details['Source'] = "ICML"
        
        details['URL'] = paper_url
        
        return details

class ICLRScraper(BaseScraper):
    def __init__(self, venue_name, config):
        super().__init__(venue_name, config)
        self.batch_size = 1000  # Maximum number of papers to fetch per request
        self.base_api_url = "https://dblp.uni-trier.de/search/publ/api"
        self.max_retries = 3
        self.base_delay = 0.5  # Base delay between requests in seconds

    def fetch_with_retry(self, url, max_retries=3, initial_delay=5):
        """Fetch URL with exponential backoff retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Too Many Requests
                    delay = initial_delay * (2 ** attempt)  # Exponential backoff
                    logging.warning(f"Rate limited. Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    continue
                raise
            except Exception as e:
                logging.error(f"Error fetching {url}: {e}")
                raise

    def construct_search_query(self, year):
        """
        Constructs an advanced search query using DBLP syntax.
        Combines keywords and venue in the correct format.
        """
        # Keywords for initial filtering (using OR operator)
        keywords = "Robust|Adversarial|Attack|Defense|Multi|agent|MARL|Game|Theory|Reinforcement|Learning"
        
        # Venue and year specification
        venue_year = f"toc:db/conf/iclr/iclr{year}.bht:"
        
        # Combine them in the correct order
        # Format: keyword venue_specification
        query = f"{keywords} {venue_year}"
        
        return requests.utils.quote(query)

    def extract_paper_links(self, proceedings_html, proceedings_url):
        """
        Fetches paper information from DBLP API for ICLR proceedings using advanced search query.
        """
        year = int(re.search(r'iclr(\d{4})', proceedings_url).group(1))
        all_papers = []
        total_fetched = 0
        first_request = True
        total_results = None
        
        # Get the query
        query = self.construct_search_query(year)
        
        while True:
            api_url = (f"{self.base_api_url}"
                      f"?q={query}"
                      f"&h={self.batch_size}&f={total_fetched}&format=json")
            
            logging.info(f"Fetching from API: {api_url}")
            
            try:
                response = requests.get(api_url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                hits = data['result']['hits']
                
                if first_request:
                    total_results = int(hits['@total'])
                    first_request = False
                    logging.info(f"Total relevant papers found for ICLR {year}: {total_results}")

                # Handle single result case
                if '@total' in hits and int(hits['@total']) == 1:
                    papers = [hits['hit']]
                elif not hits['hit']:  # No results
                    break
                else:
                    papers = hits['hit']
                
                for paper in papers:
                    paper_info = paper['info']
                    paper_details = {
                        'title': paper_info['title'],
                        'url': paper_info['ee'],
                        'year': int(paper_info['year'])
                    }
                    all_papers.append(paper_details)
                
                papers_in_batch = len(papers)
                total_fetched += papers_in_batch
                
                logging.info(f"Fetched {papers_in_batch} papers. Total fetched so far: {total_fetched}/{total_results}")
                
                if total_fetched >= total_results:
                    logging.info(f"Successfully fetched all {total_fetched} papers for ICLR {year}")
                    break
                    
                time.sleep(self.base_delay)
                
            except Exception as e:
                logging.error(f"Error fetching DBLP API results for ICLR {year}: {e}")
                break
                
        return all_papers

    def extract_paper_details(self, paper_info, year):
        """Extracts paper details including abstract from OpenReview with retry logic."""
        try:
            # Fetch the OpenReview page with retry logic
            paper_html = self.fetch_with_retry(
                paper_info['url'], 
                max_retries=self.max_retries,
                initial_delay=self.base_delay
            )
            
            if not paper_html:
                return None

            soup = BeautifulSoup(paper_html, 'html.parser')
            
            details = {
                'Title': self.clean_title(paper_info['title']),
                'Year': year,
                'Source': 'ICLR',
                'URL': paper_info['url']
            }
            
            # Extract abstract from the meta tag with name="citation_abstract"
            abstract_meta = soup.find('meta', attrs={'name': 'citation_abstract'})
            
            if abstract_meta and 'content' in abstract_meta.attrs:
                details['Abstract'] = abstract_meta['content'].strip()
            else:
                details['Abstract'] = "Abstract not found"
            
            # Add delay between requests to respect rate limits
            time.sleep(self.base_delay)
            
            return details
            
        except Exception as e:
            logging.error(f"Error extracting paper details from OpenReview {paper_info['url']}: {e}")
            return None
            