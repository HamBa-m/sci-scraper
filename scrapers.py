# scrapers.py
import requests
from bs4 import BeautifulSoup, NavigableString
import re
import json
import datetime as dt
import time
from typing import Optional
from typing import Tuple

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
    def get_abstract(self, url: str, last_check: Optional[dt.datetime] = None) -> Tuple[Optional[str], dt.datetime]:
        """
        Extract abstract from ScienceDirect papers with rate-limiting and multiple fallback methods.
        
        Args:
            url: The URL of the ScienceDirect paper
            last_check: Timestamp of the last request to maintain rate limits. 
                       If None, will use a timestamp far in the past.
            
        Returns:
            Tuple of (abstract text or None, updated last_check timestamp)
        """
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Referer': 'https://www.google.com/',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }

            # Handle rate limiting
            current_time = dt.datetime.now()
            if last_check is None:
                last_check = current_time - dt.timedelta(seconds=11)  # Past minimum interval
            
            delay = current_time - last_check
            if delay.total_seconds() <= 10:
                time.sleep(11 - delay.total_seconds())
            last_check = dt.datetime.now()

            # Make request with retry
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None, last_check
            
            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Look for the exact structure
            abstract_div = soup.find('div', {'class': 'abstract author'})
            if abstract_div:
                # Find the inner div containing the actual text
                content_div = abstract_div.find('div', {'class': 'u-margin-s-bottom'})
                if content_div:
                    text = content_div.get_text().strip()
                    if len(text) > 100:
                        return text, last_check

            # Method 2: More general selectors as backup
            abstract_selectors = [
                'div.abstract.author',
                'div[class*="abstract"]',
                'div.u-margin-s-bottom'
            ]
            for selector in abstract_selectors:
                abstract_elem = soup.select_one(selector)
                if abstract_elem:
                    # Remove the "Abstract" heading if present
                    heading = abstract_elem.find('h2', {'class': 'section-title'})
                    if heading:
                        heading.decompose()
                    
                    text = abstract_elem.get_text().strip()
                    if len(text) > 100:
                        return text, last_check

            # Method 3: Look for spans within abstract divs
            abstract_container = soup.find('div', {'class': ['abstract', 'abstract author']})
            if abstract_container:
                span_text = abstract_container.find('span')
                if span_text:
                    text = span_text.get_text().strip()
                    if len(text) > 100:
                        return text, last_check

        except Exception as e:
            print(f"Error fetching ScienceDirect abstract: {e}")
            
        return None, last_check
class AAAIScraper(AbstractScraper):
    def get_abstract(self, url: str) -> Optional[str]:
        """Extract abstract from AAAI papers."""
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Look for the specific AAAI article structure
            article = soup.find('article', class_='obj_article_details')
            if article:
                abstract_section = article.find('section', class_='item abstract')
                if abstract_section:
                    # Remove the "Abstract" label if present
                    label = abstract_section.find('h2', class_='label')
                    if label:
                        label.decompose()
                    text = abstract_section.get_text().strip()
                    if len(text) > 100:
                        return text

            # Method 2: Backup - look for any section with abstract class
            abstract_section = soup.find('section', class_='abstract')
            if abstract_section:
                text = abstract_section.get_text().strip()
                if len(text) > 100:
                    return text

            # Method 3: Look for meta tags as fallback
            meta_abstract = soup.find('meta', {'name': 'citation_abstract'})
            if meta_abstract and meta_abstract.get('content'):
                return meta_abstract['content']

        except Exception as e:
            print(f"Error fetching AAAI abstract: {e}")
        return None
class JMLRScraper(AbstractScraper):
    def get_abstract(self, url: str) -> Optional[str]:
        """Extract abstract from JMLR papers."""
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Look for JMLR-specific abstract sections
            abstract_sections = soup.select(
                'div.abstract, div.paper-abstract, div.abstractText'
            )
            for section in abstract_sections:
                text = section.get_text().strip()
                if len(text) > 100:
                    return text

            # Method 2: Look for abstract after specific headers
            for header in soup.find_all(['h2', 'h3']):
                if 'abstract' in header.get_text().lower():
                    next_elem = header.find_next('p')
                    if next_elem and len(next_elem.get_text().strip()) > 100:
                        return next_elem.get_text().strip()

        except Exception as e:
            print(f"Error fetching JMLR abstract: {e}")
        return None

class JAIRScraper(AbstractScraper):
    def get_abstract(self, url: str) -> Optional[str]:
        """Extract abstract from JAIR papers."""
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Look for JAIR-specific abstract containers
            abstract_sections = soup.select(
                'div.abstract, div.article-abstract, section.abstract-content'
            )
            for section in abstract_sections:
                text = section.get_text().strip()
                if len(text) > 100:
                    return text

            # Method 2: Look for metadata in Open Graph tags
            meta_abstract = soup.find('meta', {'property': 'og:description'})
            if meta_abstract and meta_abstract.get('content'):
                return meta_abstract['content']

        except Exception as e:
            print(f"Error fetching JAIR abstract: {e}")
        return None

class ACMScraper(AbstractScraper):
    def get_abstract(self, url: str) -> Optional[str]:
        """Extract abstract from ACM Digital Library papers."""
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Look for ACM-specific abstract divs
            abstract_sections = soup.select(
                'div.abstractSection, div.abstract-text, div[class*="abstract"]'
            )
            for section in abstract_sections:
                text = section.get_text().strip()
                if len(text) > 100:
                    return text

            # Method 2: Look for structured data
            for script in soup.find_all('script', {'type': 'application/ld+json'}):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'description' in data:
                        return data['description']
                except json.JSONDecodeError:
                    continue

            # Method 3: Look for meta tags
            meta_abstract = soup.find('meta', {'name': 'citation_abstract'})
            if meta_abstract and meta_abstract.get('content'):
                return meta_abstract['content']

        except Exception as e:
            print(f"Error fetching ACM abstract: {e}")
        return None

class IJCAIScraper(AbstractScraper):
    def get_abstract(self, url: str) -> Optional[str]:
        """Extract abstract from IJCAI papers."""
        try:
            headers = {
                'User-Agent': next(user_cycle),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Look for IJCAI-specific abstract sections
            abstract_sections = soup.select(
                'div.abstract, div.paper-abstract, section#abstract-content'
            )
            for section in abstract_sections:
                text = section.get_text().strip()
                if len(text) > 100:
                    return text

            # Method 2: Look for JSON-LD data
            for script in soup.find_all('script', {'type': 'application/ld+json'}):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'description' in data:
                        return data['description']
                except json.JSONDecodeError:
                    continue

            # Method 3: Look for abstract in meta tags
            meta_abstract = soup.find('meta', {'name': ['description', 'citation_abstract']})
            if meta_abstract and meta_abstract.get('content'):
                return meta_abstract['content']

        except Exception as e:
            print(f"Error fetching IJCAI abstract: {e}")
        return None