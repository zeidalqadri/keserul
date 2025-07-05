"""
Interactive mode for manual URL input (equivalent to original luxcrepe.py)
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class InteractiveMode:
    """Interactive mode for manual URL input"""
    
    def __init__(self, scraper):
        self.scraper = scraper
    
    def run(self, max_urls: int = 9) -> List[Dict[str, Any]]:
        """Run interactive mode"""
        print(f"Enter up to {max_urls} sale/listing URLs (one per line, blank line to finish):")
        
        urls = []
        while len(urls) < max_urls:
            try:
                url = input(f"URL {len(urls)+1}: ").strip()
                if not url:
                    break
                
                # Basic URL validation
                if not url.startswith(('http://', 'https://')):
                    print("Please enter a valid URL starting with http:// or https://")
                    continue
                
                urls.append(url)
                
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                return []
        
        if not urls:
            print("No URLs provided.")
            return []
        
        print(f"\nStarting scrape of {len(urls)} URLs...")
        
        # Use batch processing for multiple URLs
        results = self.scraper.batch_scrape_listing_and_details(
            listing_urls=urls,
            scrape_details=False  # Interactive mode typically doesn't need detail pages
        )
        
        # Show summary
        print(f"\nScraping complete!")
        print(f"Total products found: {len(results)}")
        
        # Show per-URL breakdown
        url_counts = {}
        for product in results:
            source_url = product.get('_source_url', 'Unknown')
            url_counts[source_url] = url_counts.get(source_url, 0) + 1
        
        print("\nProducts per URL:")
        for url, count in url_counts.items():
            print(f"  {url}: {count} products")
        
        return results