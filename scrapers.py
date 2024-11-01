# scrapers.py
import requests
from bs4 import BeautifulSoup, NavigableString
import re
import json
import datetime as dt
import time

from utils import user_cycle

class AbstractScraper:
    def get_abstract(self, url):
        raise NotImplementedError("Subclasses should implement this method!")


class ArxivScraper(AbstractScraper):
    def get_abstract(self, url):
        url = url.replace('export.arxiv.org', 'arxiv.org')
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            abstract_block = soup.find('blockquote', class_='abstract')
            if abstract_block:
                abstract = abstract_block.text.replace('Abstract:', '').strip()
                return abstract
        except Exception as e:
            print(f"Error fetching arXiv abstract: {e}")
        return None


class IeeeScraper(AbstractScraper):
    def get_abstract(self, url):
        try:
            article_number = None
            if 'document' in url:
                article_number = url.split('document/')[-1].split('/')[0]
            elif 'arnumber=' in url:
                article_number = re.search(r'arnumber=(\d+)', url).group(1)
            if not article_number:
                return None
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'https://ieeexplore.ieee.org',
                'Referer': f'https://ieeexplore.ieee.org/document/{article_number}',
                'Connection': 'keep-alive',
            }

            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            abstract_meta = soup.find('meta', attrs={'property': 'og:description'})
            if abstract_meta:
                abstract = abstract_meta['content']
                return abstract
        except Exception as e:
            print(f"Error fetching IEEE abstract for article {url}: {e}")
        return None


class SpringerScraper(AbstractScraper):
    def get_abstract(self, url):
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            abstract_section = soup.find('div', {'id': 'Abs1-content'})
            if abstract_section:
                return abstract_section.get_text().strip()
            
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                return meta_desc.get('content', '').strip()
            
            abstract_p = soup.find('div', {'class': 'c-article-section__content'})
            if abstract_p:
                return abstract_p.get_text().strip()
        except Exception as e:
            print(f"Error fetching Springer abstract: {e}")
        return None


class MlrScraper(AbstractScraper):
    def get_abstract(self, url):
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            abstract_elem = soup.find('div', {'class': 'abstract'}) or soup.find('section', {'class': 'abstract'})
            if abstract_elem:
                return abstract_elem.get_text().strip()

            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                return meta_desc.get('content', '').strip()
            
            content = soup.find('div', {'id': 'content'})
            if content:
                paragraphs = content.find_all('p')
                for p in paragraphs:
                    if 'abstract' in p.get_text().lower()[:20]:
                        return p.get_text().strip()
        except Exception as e:
            print(f"Error fetching MLR abstract: {e}")
        return None


class AcmScraper(AbstractScraper):
    def get_abstract(self, url):
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Referer': 'https://www.google.com/',
                'DNT': '1'
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            abstract_elements = soup.select('div.article__abstract p, div.abstractSection p, div.abstract p')
            if abstract_elements:
                return ' '.join(elem.get_text().strip() for elem in abstract_elements)

            abstract_elements = soup.find_all(['div', 'p'], class_=lambda x: x and 'abstract' in x.lower())
            for elem in abstract_elements:
                text = elem.get_text().strip()
                if len(text) > 100:
                    return text

            script_tags = soup.find_all('script', {'type': 'application/ld+json'})
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'description' in data:
                        return data['description']
                except:
                    continue

            meta_desc = soup.find('meta', {'name': ['description', 'citation_abstract']})
            if meta_desc:
                return meta_desc.get('content', '').strip()
        except Exception as e:
            print(f"Error fetching ACM abstract: {e}")
        return None

    def get_abstract(self, url):
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            abstract_section = soup.find('div', {'class': 'art-abstract'})
            if abstract_section:
                paragraphs = abstract_section.find_all('p')
                return ' '.join([p.get_text(strip=True) for p in paragraphs])

            meta_desc = soup.find('meta', {'name': 'citation_abstract'})
            if meta_desc:
                return meta_desc.get('content', '').strip()
            
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'abstract' in data:
                        return data['abstract']
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            print(f"Error fetching MDPI abstract: {e}")
        return None

class NeuripsScraper(AbstractScraper):
    def get_abstract(self, url):
        """Extract abstract from NeurIPS papers."""
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Look for specific abstract sections
            abstract_sections = soup.select(
                'div.abstract, p.abstract, section#abstract, div.paper-abstract, div#abstract-content'
            )
            for section in abstract_sections:
                text = section.get_text().strip()
                if len(text) > 100:
                    return text

            # Method 2: Look for JSON-LD structured data
            script_tags = soup.find_all('script', {'type': 'application/ld+json'})
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'description' in data:
                        return data['description']
                except json.JSONDecodeError:
                    continue

            # Method 3: Search for paragraphs following "Abstract" headers
            for header in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                if 'abstract' in header.get_text().lower():
                    next_elem = header.find_next(['p', 'div'])
                    if next_elem and len(next_elem.get_text().strip()) > 100:
                        return next_elem.get_text().strip()
        except Exception as e:
            print(f"Error fetching NeurIPS abstract: {e}")
        return None

class MdpiScraper(AbstractScraper):
    def get_abstract(self, url):
        """Extract abstract from MDPI papers."""
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Look for the abstract section in standard MDPI structure
            abstract_section = soup.find('div', {'class': 'art-abstract'})
            if abstract_section:
                paragraphs = abstract_section.find_all('p')
                return ' '.join([p.get_text(strip=True) for p in paragraphs])

            # Method 2: Look for meta description
            meta_desc = soup.find('meta', {'name': 'citation_abstract'})
            if meta_desc:
                return meta_desc.get('content', '').strip()

            # Method 3: Look for JSON-LD structured data
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'abstract' in data:
                        return data['abstract']
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            print(f"Error fetching MDPI abstract: {e}")
        return None

class ScienceDirectScraper(AbstractScraper):
    def get_abstract(self, url, last_check):
        """Extract abstract from ScienceDirect papers with rate-limiting."""
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Referer': 'https://www.google.com/'
            }
            min_interval = 10
            delay = dt.datetime.now() - last_check
            if delay.total_seconds() <= min_interval:
                time.sleep(60 - delay.total_seconds())
            last_check = dt.datetime.now()

            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                return None, last_check
            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Try specific ScienceDirect abstract containers
            abstract_selectors = [
                'div.Abstracts', 'div.abstract', 'section.Abstract', 
                'div.abstract-content', 'div.abstract-sec'
            ]
            for selector in abstract_selectors:
                abstract_elem = soup.select_one(selector)
                if abstract_elem:
                    text_parts = [
                        text.strip() for text in abstract_elem.stripped_strings
                        if isinstance(text, NavigableString)
                    ]
                    return ' '.join(text_parts), last_check

            # Method 2: Look for JSON-LD data in script tags
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'window.__PRELOADED_STATE__' in script.string:
                    try:
                        json_data = script.string.split('window.__PRELOADED_STATE__ = ')[1].strip()
                        data = json.loads(json_data.rstrip(';'))
                        if 'abstracts' in data and 'content' in data['abstracts']:
                            for content in data['abstracts']['content']:
                                if content.get('#name') == 'abstract':
                                    for section in content.get('$$', []):
                                        if section.get('#name') == 'abstract-sec':
                                            return section.get('_', '').strip(), last_check
                    except Exception as e:
                        print(f"Error parsing ScienceDirect JSON data: {e}")
        except Exception as e:
            print(f"Error fetching ScienceDirect abstract: {e}")
        return None, last_check
