# utils.py
from urllib.parse import urlparse
from itertools import cycle

# User agent list and cycling
user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A305F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 OPR/70.0.3728.189",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 OPR/73.0.3856.344",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.320",
    "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36 OPR/52.2.2517.139570"
]
user_cycle = cycle(user_agent_list)

def detect_source(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    sources = {
        'arxiv.org': 'arXiv',
        'ieee.org': 'IEEE',
        'ieeexplore.ieee.org': 'IEEE',
        'sciencedirect.com': 'ScienceDirect',
        'springer.com': 'Springer',
        'link.springer.com': 'Springer',
        'acm.org': 'ACM',
        'dl.acm.org': 'ACM',
        'nature.com': 'Nature',
        'researchgate.net': 'ResearchGate',
        'academia.edu': 'Academia',
        'semanticscholar.org': 'Semantic Scholar',
        'elsevier.com': 'Elsevier',
        'wiley.com': 'Wiley',
        'sage.com': 'SAGE',
        'sagepub.com': 'SAGE',
        'tandfonline.com': 'Taylor & Francis',
        'biomedcentral.com': 'BioMed Central',
        'acs.org': 'ACS Publications',
        'jstor.org': 'JSTOR',
        'pubmed.ncbi.nlm.nih.gov': 'PubMed',
        'oxford.org': 'Oxford',
        'oxfordjournals.org': 'Oxford',
        'cambridge.org': 'Cambridge',
        'proceedings.neurips.cc': 'NeurIPS',
        'ojs.aaai.org': 'AAAI',
        'proceedings.mlr.press': 'MLR',
        'mdpi.com': 'MDPI',
        'www.mdpi.com': 'MDPI',
        'aaai.org': 'AAAI',
        'content.iospress.com': 'IOS Press',
        'ir.cwi.nl': 'CWI',
        'openaccess.thecvf.com': 'Computer Vision Foundation (CVF)',
        'openreview.net': 'OpenReview',
        'ora.ox.ac.uk': 'Oxford Research Archive (ORA)',
        'search.ebscohost.com': 'EBSCOhost'
    }
    
    return sources.get(domain, domain)
