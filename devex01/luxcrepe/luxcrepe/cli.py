"""
Unified command-line interface for LuxCrepe
"""

import argparse
import json
import sys
import logging
from pathlib import Path
from typing import List, Optional

from .core.scraper import LuxcrepeScraper
from .modes.interactive import InteractiveMode
from .modes.batch import BatchMode
from .modes.detail import DetailMode
from .core.config import load_config

logger = logging.getLogger(__name__)


def setup_cli_parser() -> argparse.ArgumentParser:
    """Setup command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="LuxCrepe: ML-Enhanced Universal E-commerce Product Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  luxcrepe interactive                    # Interactive mode for manual URL input
  luxcrepe batch urls.txt                 # Batch process URLs from file
  luxcrepe detail https://example.com/product/123  # Scrape single product
  luxcrepe listing https://example.com/sale --pages 5  # Scrape listing with custom page limit
  luxcrepe --config custom_config.json batch urls.txt  # Use custom configuration
        """
    )
    
    # Global options
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="luxcrepe_output.json",
        help="Output file path (default: luxcrepe_output.json)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except errors"
    )
    parser.add_argument(
        "--no-ml",
        action="store_true",
        help="Disable ML enhancement, use rule-based only"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="mode", help="Operation modes")
    
    # Interactive mode
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Interactive mode for manual URL input"
    )
    interactive_parser.add_argument(
        "--max-urls",
        type=int,
        default=9,
        help="Maximum number of URLs to accept (default: 9)"
    )
    
    # Batch mode
    batch_parser = subparsers.add_parser(
        "batch",
        help="Batch process multiple URLs"
    )
    batch_parser.add_argument(
        "input",
        help="Input file with URLs (one per line) or comma-separated URLs"
    )
    batch_parser.add_argument(
        "--details",
        action="store_true",
        help="Scrape individual product detail pages"
    )
    batch_parser.add_argument(
        "--pages",
        type=int,
        help="Maximum pages per listing (overrides config)"
    )
    
    # Detail mode
    detail_parser = subparsers.add_parser(
        "detail",
        help="Scrape individual product detail pages"
    )
    detail_parser.add_argument(
        "urls",
        nargs="+",
        help="Product detail URLs to scrape"
    )
    
    # Listing mode
    listing_parser = subparsers.add_parser(
        "listing",
        help="Scrape product listing/collection pages"
    )
    listing_parser.add_argument(
        "urls",
        nargs="+",
        help="Listing/collection URLs to scrape"
    )
    listing_parser.add_argument(
        "--pages",
        type=int,
        help="Maximum pages per listing (overrides config)"
    )
    listing_parser.add_argument(
        "--details",
        action="store_true",
        help="Also scrape individual product detail pages"
    )
    
    # Stats mode
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show scraper statistics and capabilities"
    )
    
    return parser


def load_urls_from_input(input_str: str) -> List[str]:
    """Load URLs from file or comma-separated string"""
    input_path = Path(input_str)
    
    if input_path.exists():
        # Load from file
        with open(input_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        # Treat as comma-separated URLs
        urls = [url.strip() for url in input_str.split(',') if url.strip()]
    
    # Filter out empty URLs and comments
    urls = [url for url in urls if url and not url.startswith('#')]
    
    return urls


def save_results(results: List[dict], output_path: str, quiet: bool = False) -> None:
    """Save scraping results to JSON file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        if not quiet:
            print(f"Results saved to {output_path}")
            print(f"Total products: {len(results)}")
            
            # Show quality statistics
            quality_scores = [p.get('_quality_score', 0) for p in results]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                print(f"Average quality score: {avg_quality:.2f}")
                
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        sys.exit(1)


def setup_logging_from_args(args) -> None:
    """Setup logging based on command-line arguments"""
    if args.quiet:
        level = logging.ERROR
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    """Main CLI entry point"""
    parser = setup_cli_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging_from_args(args)
    
    # Load configuration
    config = None
    if args.config:
        config = load_config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
    
    # Initialize scraper
    scraper = LuxcrepeScraper(args.config)
    
    # Apply CLI overrides
    if args.no_ml:
        scraper.update_config(use_ml=False)
        logger.info("ML enhancement disabled")
    
    # Handle different modes
    results = []
    
    try:
        if args.mode == "interactive":
            mode = InteractiveMode(scraper)
            results = mode.run(max_urls=args.max_urls)
            
        elif args.mode == "batch":
            urls = load_urls_from_input(args.input)
            if not urls:
                print(f"No valid URLs found in {args.input}")
                sys.exit(1)
            
            mode = BatchMode(scraper)
            results = mode.run(
                urls=urls,
                scrape_details=args.details,
                max_pages=args.pages
            )
            
        elif args.mode == "detail":
            mode = DetailMode(scraper)
            results = mode.run(args.urls)
            
        elif args.mode == "listing":
            mode = BatchMode(scraper)  # Reuse batch mode for listings
            results = mode.run(
                urls=args.urls,
                scrape_details=args.details,
                max_pages=args.pages
            )
            
        elif args.mode == "stats":
            stats = scraper.get_scraper_stats()
            print(json.dumps(stats, indent=2))
            return
            
        else:
            parser.print_help()
            sys.exit(1)
        
        # Save results
        if results:
            save_results(results, args.output, args.quiet)
        else:
            if not args.quiet:
                print("No products found")
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()