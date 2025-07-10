"""
Main scraper class integrating all components
"""

import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

from .config import get_config
from .utils import (
    setup_logging, extract_domain, find_next_page_url,
    deduplicate_products, RateLimiter, RetrySession
)
from ..extractors.hybrid import HybridExtractor

logger = logging.getLogger(__name__)


class LuxcrepeScraper:
    """Main scraper class with ML-enhanced extraction capabilities"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Load configuration
        if config_path:
            from .config import load_config
            self.config = load_config(config_path)
        else:
            self.config = get_config()
        
        # Setup logging
        setup_logging()
        
        # Initialize components
        self.extractor = HybridExtractor()
        self.rate_limiter = RateLimiter(self.config.scraping.delay)
        self.session = RetrySession(
            max_retries=self.config.scraping.max_retries,
            retry_delay=self.config.scraping.retry_delay
        )
        
        logger.info("LuxcrepeScraper initialized")
        logger.info(f"Extraction stats: {self.extractor.get_extraction_stats()}")
    
    def scrape_listing(self, url: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrape products from a listing/collection page with pagination support
        
        Args:
            url: URL of the listing page
            max_pages: Maximum pages to scrape (overrides config)
            
        Returns:
            List of product dictionaries
        """
        if max_pages is None:
            max_pages = self.config.scraping.max_pages
        
        all_products = []
        current_url = url
        pages_scraped = 0
        
        logger.info(f"Starting listing scrape: {url}")
        
        for page_num in range(max_pages):
            try:
                # Rate limiting
                self.rate_limiter.wait()
                
                # Fetch page
                logger.info(f"Scraping page {page_num + 1}: {current_url}")
                response = self.session.get(
                    current_url,
                    headers=self.config.scraping.headers,
                    timeout=self.config.scraping.timeout
                )
                
                soup = BeautifulSoup(response.text, "lxml")
                base_url = extract_domain(current_url)
                
                # Extract products
                products = self.extractor.extract_products_from_listing(soup, base_url)
                
                # Add source metadata
                for product in products:
                    product["_source_url"] = current_url
                    product["_scraped_at"] = time.time()
                    product["_page_number"] = page_num + 1
                
                logger.info(f"Found {len(products)} products on page {page_num + 1}")
                all_products.extend(products)
                pages_scraped += 1
                
                # Find next page
                next_url = find_next_page_url(soup, current_url)
                if not next_url or next_url == current_url:
                    logger.info("No more pages found")
                    break
                
                current_url = next_url
                
            except Exception as e:
                logger.error(f"Error scraping page {page_num + 1} of {url}: {e}")
                break
        
        # Deduplicate products
        unique_products = deduplicate_products(all_products)
        
        logger.info(f"Listing scrape complete: {len(unique_products)} unique products from {pages_scraped} pages")
        
        return unique_products
    
    def scrape_product_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape detailed product information from a product page
        
        Args:
            url: URL of the product detail page
            
        Returns:
            Product dictionary with detailed information
        """
        try:
            # Rate limiting
            self.rate_limiter.wait()
            
            logger.info(f"Scraping product detail: {url}")
            
            # Fetch page
            response = self.session.get(
                url,
                headers=self.config.scraping.headers,
                timeout=self.config.scraping.timeout
            )
            
            soup = BeautifulSoup(response.text, "lxml")
            base_url = extract_domain(url)
            
            # Extract product data
            product = self.extractor.extract_product_detail(soup, base_url)
            
            # Add metadata
            product["_source_url"] = url
            product["_scraped_at"] = time.time()
            product["_scrape_type"] = "detail"
            
            logger.info(f"Product detail extracted: {product.get('name', 'Unknown')}")
            
            return product
            
        except Exception as e:
            logger.error(f"Error scraping product detail {url}: {e}")
            return None
    
    def batch_scrape_listing_and_details(
        self,
        listing_urls: List[str],
        max_pages: Optional[int] = None,
        scrape_details: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Batch scrape multiple listings and optionally their product details
        
        Args:
            listing_urls: List of listing page URLs
            max_pages: Maximum pages per listing
            scrape_details: Whether to scrape individual product detail pages
            
        Returns:
            List of product dictionaries
        """
        all_products = []
        
        # Phase 1: Scrape all listings
        logger.info(f"Phase 1: Scraping {len(listing_urls)} listings")
        listing_products = []
        
        for i, url in enumerate(listing_urls):
            logger.info(f"Scraping listing {i+1}/{len(listing_urls)}: {url}")
            products = self.scrape_listing(url, max_pages)
            listing_products.extend(products)
        
        # Deduplicate by URL
        unique_urls = set()
        unique_listing_products = []
        
        for product in listing_products:
            url = product.get("url")
            if url and url not in unique_urls:
                unique_urls.add(url)
                unique_listing_products.append(product)
        
        logger.info(f"Phase 1 complete: {len(unique_listing_products)} unique products found")
        
        if not scrape_details:
            return unique_listing_products
        
        # Phase 2: Scrape product details
        logger.info(f"Phase 2: Scraping details for {len(unique_listing_products)} products")
        
        for i, listing_product in enumerate(unique_listing_products):
            product_url = listing_product.get("url")
            if not product_url:
                all_products.append(listing_product)
                continue
            
            logger.info(f"Scraping detail {i+1}/{len(unique_listing_products)}: {product_url}")
            
            detailed_product = self.scrape_product_detail(product_url)
            if detailed_product:
                # Merge listing data with detailed data
                merged_product = {**listing_product, **detailed_product}
                merged_product["_has_detail_data"] = True
                all_products.append(merged_product)
            else:
                # Use listing data only
                listing_product["_has_detail_data"] = False
                all_products.append(listing_product)
        
        logger.info(f"Batch scrape complete: {len(all_products)} products")
        
        return all_products
    
    def scrape_single_url(self, url: str, scrape_type: str = "auto") -> List[Dict[str, Any]]:
        """
        Scrape a single URL, automatically detecting if it's a listing or product page
        
        Args:
            url: URL to scrape
            scrape_type: "auto", "listing", or "detail"
            
        Returns:
            List of product dictionaries
        """
        if scrape_type == "auto":
            scrape_type = self._detect_page_type(url)
        
        if scrape_type == "listing":
            return self.scrape_listing(url)
        elif scrape_type == "detail":
            product = self.scrape_product_detail(url)
            return [product] if product else []
        else:
            logger.warning(f"Could not determine page type for {url}, trying listing")
            return self.scrape_listing(url)
    
    def _detect_page_type(self, url: str) -> str:
        """
        Detect if URL is a listing or product detail page
        
        Args:
            url: URL to analyze
            
        Returns:
            "listing" or "detail"
        """
        # Simple heuristics based on URL patterns
        url_lower = url.lower()
        
        # Product detail indicators
        detail_indicators = [
            '/product/', '/item/', '/p/', '/products/',
            'product-', 'item-', '.html', '/sku/'
        ]
        
        # Listing indicators
        listing_indicators = [
            '/collection/', '/category/', '/collections/',
            '/categories/', '/shop/', '/sale/', '/search',
            'category=', 'collection=', 'search='
        ]
        
        for indicator in detail_indicators:
            if indicator in url_lower:
                return "detail"
        
        for indicator in listing_indicators:
            if indicator in url_lower:
                return "listing"
        
        # Default to listing if uncertain
        return "listing"
    
    def get_scraper_stats(self) -> Dict[str, Any]:
        """Get scraper statistics and capabilities"""
        return {
            "config": {
                "max_pages": self.config.scraping.max_pages,
                "delay": self.config.scraping.delay,
                "timeout": self.config.scraping.timeout,
                "max_retries": self.config.scraping.max_retries,
                "ml_enabled": self.config.ml.use_ml
            },
            "extraction": self.extractor.get_extraction_stats(),
            "user_agents": len(self.config.scraping.user_agents)
        }
    
    def update_config(self, **kwargs) -> None:
        """Update scraper configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.scraping, key):
                setattr(self.config.scraping, key, value)
                logger.info(f"Updated config: {key} = {value}")
            elif hasattr(self.config.ml, key):
                setattr(self.config.ml, key, value)
                logger.info(f"Updated ML config: {key} = {value}")
            else:
                logger.warning(f"Unknown config key: {key}")
        
        # Reinitialize components that depend on config
        self.rate_limiter = RateLimiter(self.config.scraping.delay)
        self.session = RetrySession(
            max_retries=self.config.scraping.max_retries,
            retry_delay=self.config.scraping.retry_delay
        )