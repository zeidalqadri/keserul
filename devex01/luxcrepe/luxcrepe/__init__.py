"""
LuxCrepe: ML-Enhanced Universal E-commerce Product Scraper

A modern web scraping toolkit that combines rule-based heuristics with machine learning
for intelligent product data extraction from luxury e-commerce websites.
"""

__version__ = "0.1.0"
__author__ = "LuxCrepe Team"

from .core.scraper import LuxcrepeScraper
from .extractors.hybrid import HybridExtractor
from .ml.inference.predictor import MLPredictor

__all__ = [
    "LuxcrepeScraper",
    "HybridExtractor", 
    "MLPredictor"
]