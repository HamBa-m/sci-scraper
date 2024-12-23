import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import tqdm
import concurrent.futures
from urllib.parse import urljoin
import logging

# -------------------- Configuration -------------------- #

# Define the conferences with their specific scraping configurations
VENUES = {
    "IJCAI": {
        "base_url": "https://www.ijcai.org",
        "proceedings_url_template": "https://www.ijcai.org/proceedings/{year}/",
        "paper_wrapper_class": "paper_wrapper",
        "title_selector": "div.title",
        "details_selector": "div.details a",
        "abstract_page_selector": "div.abstract",
        "venue_name": "IJCAI",
        "year_mapping": None  # Years are directly in the URL
    },
    "PMLR": {
        "base_url": "https://proceedings.mlr.press",
        "proceedings_url_template": "https://proceedings.mlr.press/v{volume}/",
        "paper_wrapper_class": "paper",
        "title_selector": "p.title",
        "details_selector": "p.links a[href*='abs']",
        "abstract_page_selector": "div#abstract",
        "venue_name": "PMLR",
        "year_mapping": {
            2018: 232,
            2019: 233,
            2020: 234,
            2021: 235,
            2022: 236,
            2023: 237,
            2024: 238
        }
    }
    # Add other venues here as needed
}

# Keywords to filter papers related to Adversarial Machine Learning
KEYWORDS_ADVERSARIAL_ML = [
    "adversarial",
    "attack",
    "attacks",
    "robust",
    "robustness",
    "defense",
    "defenses",
    "defensive",
    "corruption"
]

# Keywords to filter papers related to Reinforcement Learning
KEYWORDS_RL = [
    "reinforcement",
    "drl",
    "rl",
    "madrl",
    "marl"
]

# Keywords to filter papers related to Multi-Agent Reinforcement Learning
KEYWORDS_MULTI_AGENT = [
    "multi-agent",
    "agents",
    "madrl",
    "marl"
]

# Years to scrape
START_YEAR = 2018
END_YEAR = 2024

# HTTP headers to mimic a legitimate browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DataScraper/1.0; +https://yourdomain.com/bot)"
}

# Delay between requests in seconds to respect server load
REQUEST_DELAY = 0.2  # Adjust as needed

# Configure logging
logging.basicConfig(filename='log/venues.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------------------------------------------------------- #

def fetch_html(url):
    """
    Fetches the HTML content of a given URL.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def extract_paper_links_ijcai(proceedings_html, base_url, paper_wrapper_class):
    """
    Extracts paper detail page links from IJCAI proceedings page.
    """
    soup = BeautifulSoup(proceedings_html, 'html.parser')
    paper_links = []

    # Each paper is within a div with class 'paper_wrapper'
    for paper_div in soup.find_all('div', class_=paper_wrapper_class):
        details_div = paper_div.find('div', class_='details')
        if details_div:
            details_link = details_div.find('a', string=re.compile(r'Details', re.I))
            if details_link and 'href' in details_link.attrs:
                paper_url = urljoin(base_url, details_link['href'])
                paper_links.append(paper_url)
    return paper_links

def extract_paper_links_pmlr(proceedings_html, base_url, paper_wrapper_class):
    """
    Extracts paper abstract page links from PMLR proceedings page.
    """
    soup = BeautifulSoup(proceedings_html, 'html.parser')
    paper_links = []
    # Each paper is within a div with class 'paper'
    for paper_div in soup.find_all('div', class_=paper_wrapper_class):
        abs_link = paper_div.find('a', string=re.compile(r'abs', re.I))
        if abs_link and 'href' in abs_link.attrs:
            paper_url = urljoin(base_url, abs_link['href'])
            paper_links.append(paper_url)

    return paper_links

def extract_paper_details_ijcai(paper_url, base_url, abstract_page_selector):
    """
    Extracts paper details from IJCAI paper details page.
    """
    paper_html = fetch_html(paper_url)
    if not paper_html:
        return None

    soup = BeautifulSoup(paper_html, 'html.parser')
    details = {}

    # Extract Title
    title_tag = soup.find('meta', attrs={'name': 'citation_title'})
    if title_tag and 'content' in title_tag.attrs:
        details['Title'] = title_tag['content']
    else:
        details['Title'] = "N/A"

    # Extract Abstract
    abstract = ""
    abstract_tag = soup.find('div', class_='col-md-12')
    if abstract_tag:
        abstract = abstract_tag.get_text(separator=" ", strip=True)
    details['Abstract'] = abstract

    # Venue is already known (IJCAI)
    details['Venue'] = "IJCAI"

    # Year is inferred from the proceedings URL; extract from paper_url
    year_match = re.search(r'/proceedings/(\d{4})/', paper_url)
    if year_match:
        details['Year'] = int(year_match.group(1))
    else:
        details['Year'] = "N/A"

    return details

def extract_paper_details_pmlr(paper_url, base_url, abstract_page_selector):
    """
    Extracts paper details from PMLR paper abstract page.
    """
    paper_html = fetch_html(paper_url)
    if not paper_html:
        return None

    soup = BeautifulSoup(paper_html, 'html.parser')
    details = {}

    # Extract Title
    title_tag = soup.find('h1')
    if title_tag:
        details['Title'] = title_tag.get_text(strip=True)
    else:
        details['Title'] = "N/A"

    # Extract Abstract
    abstract = ""
    abstract_tag = soup.find('div', id='abstract')
    if abstract_tag:
        abstract = abstract_tag.get_text(separator=" ", strip=True)
    details['Abstract'] = abstract

    # Extract Year from the info section
    info_tag = soup.find('div', id='info')
    if info_tag:
        year_match = re.search(r',\s*(\d{4})\.', info_tag.get_text())
        if year_match:
            details['Year'] = int(year_match.group(1))
        else:
            details['Year'] = "N/A"
    else:
        details['Year'] = "N/A"

    # Venue is already known (PMLR)
    details['Venue'] = "PMLR"
    return details

def paper_contains_keywords(title, abstract, keyword_groups):
    """
    Checks if at least one keyword from each sublist of keywords is present in the title or abstract.
    """
    combined_text = f"{title} | {abstract}".lower()
    for group in keyword_groups:
        if not any(kw.lower() in combined_text for kw in group):
            return False
    return True

def fetch_papers_for_year(venue_name, config, year):
    all_papers_for_year = []
    logging.info(f"Processing {config['venue_name']} {year}...")

    base_url = config["base_url"]
    proceedings_url_template = config["proceedings_url_template"]
    paper_wrapper_class = config["paper_wrapper_class"]
    abstract_page_selector = config["abstract_page_selector"]
    year_mapping = config["year_mapping"]
    venue_display_name = config["venue_name"]

    # Determine the proceedings URL based on the venue
    if venue_name == "PMLR":
        volume = year_mapping.get(year)
        if not volume:
            logging.warning(f"No volume mapping found for year {year}. Skipping.")
            return []
        proceedings_url = proceedings_url_template.format(volume=volume)
    else:
        proceedings_url = proceedings_url_template.format(year=year)

    logging.info(f"Fetching proceedings page: {proceedings_url}")
    proceedings_html = fetch_html(proceedings_url)
    if not proceedings_html:
        logging.warning(f"Failed to fetch proceedings for {venue_display_name} {year}. Skipping.")
        return []

    # Extract paper links based on venue
    if venue_name == "IJCAI":
        paper_links = extract_paper_links_ijcai(proceedings_html, base_url, paper_wrapper_class)
    elif venue_name == "PMLR":
        paper_links = extract_paper_links_pmlr(proceedings_html, base_url, paper_wrapper_class)
    else:
        logging.warning(f"Venue {venue_name} is not supported yet.")
        return []

    logging.info(f"Found {len(paper_links)} papers for {venue_display_name} {year}.")

    relevant_papers_count = 0
    for idx, paper_url in enumerate(tqdm.tqdm(paper_links, desc="Found papers: {}".format(len(paper_links))), 1):
        # Extract paper details based on venue
        if venue_name == "IJCAI":
            details = extract_paper_details_ijcai(paper_url, base_url, abstract_page_selector)
        elif venue_name == "PMLR":
            details = extract_paper_details_pmlr(paper_url, base_url, abstract_page_selector)
        else:
            details = None

        if not details:
            logging.warning(f"Failed to extract details for {paper_url}")
            continue

        title = details.get('Title', "")
        abstract = details.get('Abstract', "")
        year_extracted = details.get('Year', year)  # Fallback to loop year
        url = paper_url

        if paper_contains_keywords(title, abstract, [KEYWORDS_ADVERSARIAL_ML, KEYWORDS_RL, KEYWORDS_MULTI_AGENT]):
            paper_entry = {
                "Title": title,
                "Year": year_extracted,
                "Venue": details.get('Venue', venue_display_name),
                "Abstract": abstract,
                "URL": url
            }
            all_papers_for_year.append(paper_entry)
            relevant_papers_count += 1

        # Respect rate limiting
        time.sleep(REQUEST_DELAY)

    logging.info(f"Found {relevant_papers_count} relevant papers for {venue_display_name} {year}.")
    # Additional delay after each year's proceedings
    time.sleep(REQUEST_DELAY * 10)

    return all_papers_for_year


def main():
    all_papers = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_year = {}

        # Create futures for each year per venue
        for venue_name, config in VENUES.items():
            logging.info(f"=== Scraping Venue: {venue_name} ===")
            for year in range(START_YEAR, END_YEAR + 1):
                future = executor.submit(fetch_papers_for_year, venue_name, config, year)
                future_to_year[future] = (venue_name, year)

        # Wait for the results and collect them
        for future in concurrent.futures.as_completed(future_to_year):
            venue_name, year = future_to_year[future]
            try:
                papers = future.result()
                all_papers.extend(papers)
                logging.info(f"Completed processing for {venue_name} {year} with {len(papers)} papers.")
            except Exception as exc:
                logging.error(f"Error occurred while processing {venue_name} {year}: {exc}")

    # Create DataFrame
    df = pd.DataFrame(all_papers)

    # Remove duplicates based on Title and Year
    df.drop_duplicates(subset=["Title", "Year", "Venue"], inplace=True)

    # Save to Excel
    output_file = "results/venues_results.xlsx"
    df.to_excel(output_file, index=False)
    logging.info(f"Scraping completed. {len(df)} papers saved to {output_file}.")

if __name__ == "__main__":
    main()
