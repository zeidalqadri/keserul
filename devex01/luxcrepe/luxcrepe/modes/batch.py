"""
Batch mode for processing multiple URLs (equivalent to original luxcrepe_batch.py)
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class BatchMode:
    """Batch processing mode for multiple URLs"""
    
    def __init__(self, scraper):
        self.scraper = scraper
    
    def run(
        self, 
        urls: List[str], 
        scrape_details: bool = True,
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Run batch processing mode
        
        Args:
            urls: List of URLs to process
            scrape_details: Whether to scrape individual product detail pages
            max_pages: Maximum pages per listing
            
        Returns:
            List of product dictionaries
        """
        if not urls:
            logger.warning("No URLs provided for batch processing")
            return []
        
        print(f"Batch processing {len(urls)} URLs...")
        print(f"Detail scraping: {'enabled' if scrape_details else 'disabled'}")
        if max_pages:
            print(f"Max pages per listing: {max_pages}")
        
        # Show URL list
        print("\nURLs to process:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
        
        # Apply max_pages override if provided
        if max_pages:
            self.scraper.update_config(max_pages=max_pages)
        
        # Process URLs
        results = self.scraper.batch_scrape_listing_and_details(
            listing_urls=urls,
            scrape_details=scrape_details
        )
        
        # Show summary statistics
        self._show_batch_summary(results, urls, scrape_details)
        
        return results
    
    def _show_batch_summary(
        self, 
        results: List[Dict[str, Any]], 
        original_urls: List[str],
        scrape_details: bool
    ) -> None:
        """Show batch processing summary"""
        print(f"\n{'='*50}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*50}")
        
        print(f"URLs processed: {len(original_urls)}")
        print(f"Total products: {len(results)}")
        
        if scrape_details:
            detail_count = sum(1 for p in results if p.get('_has_detail_data', False))
            print(f"Products with detail data: {detail_count}")
            print(f"Detail success rate: {detail_count/len(results)*100:.1f}%" if results else "0%")
        
        # Quality statistics
        quality_scores = [p.get('_quality_score', 0) for p in results if '_quality_score' in p]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            min_quality = min(quality_scores)
            max_quality = max(quality_scores)
            print(f"Average quality score: {avg_quality:.2f}")
            print(f"Quality range: {min_quality:.2f} - {max_quality:.2f}")
        
        # Source URL breakdown
        url_counts = {}
        for product in results:
            source_url = product.get('_source_url', 'Unknown')
            url_counts[source_url] = url_counts.get(source_url, 0) + 1
        
        print(f"\nProducts per source URL:")
        for url, count in sorted(url_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {count:3d} products - {url}")
        
        # Extraction method breakdown
        extraction_methods = {}
        for product in results:
            method = product.get('_extraction_method', 'unknown')
            extraction_methods[method] = extraction_methods.get(method, 0) + 1
        
        if extraction_methods:
            print(f"\nExtraction method breakdown:")
            for method, count in extraction_methods.items():
                percentage = count / len(results) * 100
                print(f"  {method}: {count} products ({percentage:.1f}%)")
        
        # Show sample products
        if results:
            print(f"\nSample products:")
            for i, product in enumerate(results[:3]):
                name = product.get('name', 'Unknown')[:50]
                price = product.get('price', 'N/A')
                currency = product.get('priceCurrency', '')
                brand = product.get('brand', 'Unknown')
                quality = product.get('_quality_score', 0)
                
                print(f"  {i+1}. {name}")
                print(f"     Brand: {brand} | Price: {price} {currency} | Quality: {quality:.2f}")
        
        print(f"{'='*50}")


class ListingMode(BatchMode):
    """Specialized mode for listing pages (alias for batch mode)"""
    pass