"""
Configuration management for LuxCrepe scraper
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json


@dataclass
class ScrapingConfig:
    """Configuration for scraping behavior"""
    max_pages: int = 3
    delay: float = 1.0
    timeout: int = 15
    max_retries: int = 3
    retry_delay: float = 2.0
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (compatible; UniversalLuxuryScraper/3.0; +https://example.com/bot)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ])
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers with rotating user agent"""
        import random
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }


@dataclass 
class MLConfig:
    """Configuration for ML models and inference"""
    use_ml: bool = True
    model_confidence_threshold: float = 0.7
    ensemble_voting: str = "weighted"  # "majority", "weighted", "confidence"
    batch_size: int = 32
    max_sequence_length: int = 512
    device: str = "auto"  # "auto", "cpu", "cuda"
    model_cache_dir: str = "./models"
    
    # Model-specific configs
    price_model: str = "distilbert-base-uncased"
    brand_model: str = "distilbert-base-uncased" 
    detection_model: str = "yolov5s"
    quality_threshold: float = 0.8


@dataclass
class QualityConfig:
    """Configuration for data quality and validation"""
    min_product_fields: int = 3  # Minimum fields required for valid product
    max_price_value: float = 50000.0  # Max reasonable price
    min_name_length: int = 3
    max_name_length: int = 200
    required_fields: List[str] = field(default_factory=lambda: ["name", "price"])
    price_patterns: List[str] = field(default_factory=lambda: [
        r'[\$\€\£\¥]\s?\d+(?:,\d{3})*(?:\.\d{2})?',
        r'\d+(?:,\d{3})*(?:\.\d{2})?\s?[\$\€\£\¥]'
    ])


@dataclass
class LuxCrepeConfig:
    """Main configuration class"""
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'LuxCrepeConfig':
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            return cls()
            
        with open(config_path, 'r') as f:
            data = json.load(f)
            
        return cls(
            scraping=ScrapingConfig(**data.get('scraping', {})),
            ml=MLConfig(**data.get('ml', {})),
            quality=QualityConfig(**data.get('quality', {}))
        )
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to JSON file"""
        data = {
            'scraping': self.scraping.__dict__,
            'ml': self.ml.__dict__,
            'quality': self.quality.__dict__
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)


# Global configuration instance
config = LuxCrepeConfig()

def load_config(config_path: Optional[str] = None) -> LuxCrepeConfig:
    """Load configuration from file or environment"""
    if config_path is None:
        config_path = os.getenv('LUXCREPE_CONFIG', 'luxcrepe_config.json')
    
    global config
    config = LuxCrepeConfig.from_file(config_path)
    return config

def get_config() -> LuxCrepeConfig:
    """Get current configuration instance"""
    return config