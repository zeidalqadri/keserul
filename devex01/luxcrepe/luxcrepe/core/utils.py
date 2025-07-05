"""
Utility functions for LuxCrepe scraper
"""

import re
import time
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional, Union, Set
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Setup structured logging for the application"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('luxcrepe.log')
        ]
    )


def safe_extract_text(element, strip: bool = True) -> Optional[str]:
    """Safely extract text from BeautifulSoup element"""
    if not element:
        return None
    
    try:
        text = element.get_text() if hasattr(element, 'get_text') else str(element)
        return text.strip() if strip else text
    except Exception as e:
        logger.warning(f"Failed to extract text: {e}")
        return None


def normalize_url(url: str, base_url: str) -> str:
    """Normalize and join URLs properly"""
    if not url:
        return ""
    
    if url.startswith(('http://', 'https://')):
        return url
    
    return urljoin(base_url, url)


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return ""


def clean_price_text(price_text: str) -> str:
    """Clean and normalize price text"""
    if not price_text:
        return ""
    
    # Remove extra whitespace
    price_text = re.sub(r'\s+', ' ', price_text.strip())
    
    # Common price cleaning patterns
    price_text = re.sub(r'(?i)(was|now|sale|price)[:;]?\s*', '', price_text)
    price_text = re.sub(r'(?i)\s*(each|per\s+item)\s*', '', price_text)
    
    return price_text


def extract_price_components(price_text: str) -> Dict[str, Any]:
    """Extract price amount, currency, and type from text"""
    if not price_text:
        return {}
    
    cleaned_text = clean_price_text(price_text)
    
    # Currency patterns
    currency_map = {
        '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY',
        'USD': 'USD', 'EUR': 'EUR', 'GBP': 'GBP', 'JPY': 'JPY'
    }
    
    # Price extraction patterns
    patterns = [
        r'([\$\€\£\¥])\s?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $123.45
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s?([\$\€\£\¥])',  # 123.45$
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s?(USD|EUR|GBP|JPY)',  # 123.45 USD
    ]
    
    for pattern in patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                if groups[0] in currency_map:
                    currency, amount = groups[0], groups[1]
                else:
                    amount, currency = groups[0], groups[1]
                
                try:
                    # Clean amount (remove commas)
                    amount_clean = float(amount.replace(',', ''))
                    return {
                        'amount': amount_clean,
                        'currency': currency_map.get(currency, currency),
                        'original_text': price_text
                    }
                except ValueError:
                    continue
    
    return {'original_text': price_text}


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge dictionaries, preferring first non-empty value for each key"""
    result = {}
    for d in dicts:
        if not isinstance(d, dict):
            continue
        for k, v in d.items():
            if k not in result or not result[k]:
                result[k] = v
    return result


def deduplicate_products(products: List[Dict[str, Any]], key_fields: List[str] = None) -> List[Dict[str, Any]]:
    """Deduplicate products based on key fields"""
    if not products:
        return []
    
    if key_fields is None:
        key_fields = ['url', 'name', 'sku']
    
    seen = set()
    deduped = []
    
    for product in products:
        # Create a unique key from available key fields
        key_parts = []
        for field in key_fields:
            value = product.get(field)
            if value:
                key_parts.append(str(value).lower().strip())
        
        if not key_parts:
            # No key fields available, use hash of entire product
            key = hashlib.md5(json.dumps(product, sort_keys=True).encode()).hexdigest()
        else:
            key = '|'.join(key_parts)
        
        if key not in seen:
            seen.add(key)
            deduped.append(product)
    
    return deduped


def validate_product_data(product: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, Any]:
    """Validate and score product data quality"""
    if required_fields is None:
        required_fields = ['name', 'price']
    
    validation_result = {
        'is_valid': True,
        'score': 0.0,
        'issues': [],
        'missing_fields': []
    }
    
    # Check required fields
    for field in required_fields:
        if not product.get(field):
            validation_result['missing_fields'].append(field)
            validation_result['issues'].append(f"Missing required field: {field}")
    
    # Quality scoring
    total_possible_score = 10
    current_score = 0
    
    # Field presence scoring
    important_fields = ['name', 'price', 'brand', 'image', 'url']
    for field in important_fields:
        if product.get(field):
            current_score += 2
    
    # Content quality scoring
    name = product.get('name', '')
    if len(name) > 5:
        current_score += 1
    
    price = product.get('price')
    if price and isinstance(price, (int, float)) and 0 < price < 50000:
        current_score += 1
    
    # URL validation
    url = product.get('url', '')
    if url and url.startswith(('http://', 'https://')):
        current_score += 1
    
    validation_result['score'] = min(current_score / total_possible_score, 1.0)
    validation_result['is_valid'] = len(validation_result['missing_fields']) == 0
    
    return validation_result


def find_next_page_url(soup: BeautifulSoup, current_url: str) -> Optional[str]:
    """Find the next page URL for pagination"""
    base_url = extract_domain(current_url)
    
    # Method 1: rel="next" link
    next_link = soup.find("link", rel="next")
    if next_link and next_link.get("href"):
        return normalize_url(next_link["href"], base_url)
    
    # Method 2: anchor with 'next' text
    next_anchors = soup.find_all("a", string=re.compile(r'next|→|>', re.I))
    for anchor in next_anchors:
        if anchor.get("href"):
            return normalize_url(anchor["href"], base_url)
    
    # Method 3: increment page parameter
    page_match = re.search(r'([?&]page=)(\d+)', current_url)
    if page_match:
        next_page = int(page_match.group(2)) + 1
        return re.sub(r'([?&]page=)\d+', rf'\g<1>{next_page}', current_url)
    
    return None


class RateLimiter:
    """Simple rate limiter for HTTP requests"""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.last_request_time = 0
    
    def wait(self) -> None:
        """Wait if necessary to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        
        self.last_request_time = time.time()


class RetrySession:
    """HTTP session with retry logic"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        self.session = requests.Session()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """GET request with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(url, **kwargs)
                if response.status_code == 200:
                    return response
                elif response.status_code in [429, 503, 504]:  # Rate limit or server errors
                    if attempt < self.max_retries:
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limited on {url}, waiting {wait_time}s")
                        time.sleep(wait_time)
                        continue
                response.raise_for_status()
                
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Request failed for {url}, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All retry attempts failed for {url}: {e}")
                    raise
        
        if last_exception:
            raise last_exception