"""
Detail mode for scraping individual product pages (equivalent to original luxcrepe_deets.py)
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DetailMode:
    """Mode for scraping individual product detail pages"""
    
    def __init__(self, scraper):
        self.scraper = scraper
    
    def run(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Run detail scraping mode
        
        Args:
            urls: List of product detail URLs to scrape
            
        Returns:
            List of product dictionaries
        """
        if not urls:
            logger.warning("No URLs provided for detail scraping")
            return []
        
        print(f"Detail scraping {len(urls)} product URLs...")
        
        # Show URL list
        print("\nProduct URLs to scrape:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
        
        results = []
        failed_urls = []
        
        for i, url in enumerate(urls):
            print(f"\nScraping product {i+1}/{len(urls)}: {url}")
            
            try:
                product = self.scraper.scrape_product_detail(url)
                if product:
                    results.append(product)
                    
                    # Show basic product info
                    name = product.get('name', 'Unknown')[:60]
                    price = product.get('price', 'N/A')
                    currency = product.get('priceCurrency', '')
                    brand = product.get('brand', 'Unknown')
                    quality = product.get('_quality_score', 0)
                    
                    print(f"  ✓ {name}")
                    print(f"    Brand: {brand} | Price: {price} {currency} | Quality: {quality:.2f}")
                else:
                    failed_urls.append(url)
                    print(f"  ✗ Failed to extract product data")
                    
            except Exception as e:
                failed_urls.append(url)
                print(f"  ✗ Error: {e}")
                logger.error(f"Failed to scrape {url}: {e}")
        
        # Show summary
        self._show_detail_summary(results, urls, failed_urls)
        
        return results
    
    def _show_detail_summary(
        self, 
        results: List[Dict[str, Any]], 
        original_urls: List[str],
        failed_urls: List[str]
    ) -> None:
        """Show detail scraping summary"""
        print(f"\n{'='*50}")
        print("DETAIL SCRAPING SUMMARY")
        print(f"{'='*50}")
        
        print(f"URLs attempted: {len(original_urls)}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {len(failed_urls)}")
        print(f"Success rate: {len(results)/len(original_urls)*100:.1f}%" if original_urls else "0%")
        
        if failed_urls:
            print(f"\nFailed URLs:")
            for url in failed_urls:
                print(f"  - {url}")
        
        # Quality statistics
        if results:
            quality_scores = [p.get('_quality_score', 0) for p in results if '_quality_score' in p]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                min_quality = min(quality_scores)
                max_quality = max(quality_scores)
                print(f"\nQuality Statistics:")
                print(f"  Average: {avg_quality:.2f}")
                print(f"  Range: {min_quality:.2f} - {max_quality:.2f}")
        
        # Extraction method breakdown
        if results:
            extraction_methods = {}
            for product in results:
                method = product.get('_extraction_method', 'unknown')
                extraction_methods[method] = extraction_methods.get(method, 0) + 1
            
            print(f"\nExtraction method breakdown:")
            for method, count in extraction_methods.items():
                percentage = count / len(results) * 100
                print(f"  {method}: {count} products ({percentage:.1f}%)")
        
        # Data completeness analysis
        if results:
            field_counts = {}
            important_fields = ['name', 'price', 'brand', 'image', 'description']
            
            for field in important_fields:
                count = sum(1 for p in results if p.get(field))
                field_counts[field] = count
            
            print(f"\nData completeness:")
            for field, count in field_counts.items():
                percentage = count / len(results) * 100
                print(f"  {field}: {count}/{len(results)} ({percentage:.1f}%)")
        
        # Show best quality products
        if results:
            # Sort by quality score
            sorted_results = sorted(results, key=lambda x: x.get('_quality_score', 0), reverse=True)
            top_products = sorted_results[:3]
            
            print(f"\nTop quality products:")
            for i, product in enumerate(top_products):
                name = product.get('name', 'Unknown')[:50]
                price = product.get('price', 'N/A')
                currency = product.get('priceCurrency', '')
                brand = product.get('brand', 'Unknown')
                quality = product.get('_quality_score', 0)
                
                print(f"  {i+1}. {name}")
                print(f"     Brand: {brand} | Price: {price} {currency} | Quality: {quality:.2f}")
        
        print(f"{'='*50}")