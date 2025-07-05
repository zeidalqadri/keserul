# LuxCrepe 🍰

**ML-Enhanced Universal E-commerce Product Scraper**

LuxCrepe is a modern web scraping toolkit that combines traditional rule-based extraction with machine learning to intelligently extract product data from luxury e-commerce websites.

## Features

### 🤖 Hybrid Intelligence
- **Rule-based extraction**: Fast baseline extraction using heuristics
- **ML enhancement**: Smart pattern recognition with confidence scoring
- **Ensemble decisions**: Combines both approaches for optimal accuracy

### 🚀 Advanced Capabilities
- **Universal compatibility**: Works across different e-commerce platforms
- **Pagination support**: Automatically follows listing pages
- **Quality scoring**: Validates and scores extraction quality
- **Rate limiting**: Respectful crawling with configurable delays
- **Retry logic**: Handles network failures gracefully

### 📊 Data Intelligence
- **Product detection**: Computer vision models identify product cards
- **Price extraction**: NLP models handle complex pricing patterns
- **Brand recognition**: Trained on luxury brand databases
- **Quality validation**: Automatic data quality assessment

## Quick Start

### Installation

```bash
# Basic installation
pip install luxcrepe

# With ML features
pip install luxcrepe[ml]

# Development installation
git clone https://github.com/luxcrepe/luxcrepe.git
cd luxcrepe
pip install -e .[all]
```

### Command Line Usage

```bash
# Interactive mode
luxcrepe interactive

# Batch process URLs from file
luxcrepe batch urls.txt --details

# Scrape single product
luxcrepe detail https://example.com/product/123

# Scrape collection with custom settings
luxcrepe listing https://example.com/sale --pages 5 --output sale_products.json
```

### Python API

```python
from luxcrepe import LuxcrepeScraper

# Initialize scraper
scraper = LuxcrepeScraper()

# Scrape a listing page
products = scraper.scrape_listing("https://example.com/collection/all")

# Scrape product details
product = scraper.scrape_product_detail("https://example.com/product/123")

# Batch processing
results = scraper.batch_scrape_listing_and_details([
    "https://example.com/sale",
    "https://example.com/new-arrivals"
])
```

## Configuration

Create a `luxcrepe_config.json` file:

```json
{
  "scraping": {
    "max_pages": 5,
    "delay": 1.0,
    "timeout": 15,
    "max_retries": 3
  },
  "ml": {
    "use_ml": true,
    "model_confidence_threshold": 0.7,
    "ensemble_voting": "weighted"
  },
  "quality": {
    "min_product_fields": 3,
    "quality_threshold": 0.8
  }
}
```

## Architecture

```
luxcrepe/
├── core/               # Core functionality
│   ├── scraper.py     # Main scraper class
│   ├── config.py      # Configuration management
│   └── utils.py       # Utility functions
├── extractors/        # Extraction engines
│   ├── traditional.py # Rule-based extraction
│   └── hybrid.py      # ML + rule-based ensemble
├── ml/                # Machine learning components
│   ├── models/        # Model definitions
│   ├── inference/     # Prediction and serving
│   └── training/      # Training pipelines
└── modes/             # Operation modes
    ├── interactive.py # Interactive CLI mode
    ├── batch.py       # Batch processing
    └── detail.py      # Product detail mode
```

## Machine Learning Features

### Models Used
- **Product Detection**: YOLO-based computer vision for product card identification
- **Price Extraction**: Fine-tuned BERT for named entity recognition
- **Brand Classification**: DistilBERT trained on luxury brand data
- **Quality Scoring**: Ensemble model for data quality assessment

### Training Data
- Self-generated ground truth from rule-based extraction
- Manual annotation of complex cases
- Synthetic data generation for edge cases
- Active learning from uncertain predictions

## Performance

| Metric | Rule-based | ML-Enhanced | Improvement |
|--------|------------|-------------|-------------|
| Product Detection | ~60% | ~85% | +42% |
| Price Accuracy | ~70% | ~90% | +29% |
| Brand Recognition | ~45% | ~80% | +78% |
| Overall Quality | ~65% | ~87% | +34% |

## Supported Sites

LuxCrepe works with most e-commerce platforms including:
- Custom luxury brand sites
- Shopify stores
- WooCommerce sites
- Magento stores
- And many more...

## Development

### Setup Development Environment

```bash
git clone https://github.com/luxcrepe/luxcrepe.git
cd luxcrepe
pip install -e .[dev]
pre-commit install
```

### Running Tests

```bash
pytest
pytest --cov=luxcrepe tests/
```

### Code Formatting

```bash
black luxcrepe/
isort luxcrepe/
flake8 luxcrepe/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Areas for Contribution
- New ML models and training data
- Site-specific extraction adapters
- Performance optimizations
- Documentation improvements

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of BeautifulSoup and requests
- ML models powered by Transformers and PyTorch
- Inspired by the needs of luxury e-commerce data analysis

## Support

- 📖 [Documentation](https://luxcrepe.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/luxcrepe/luxcrepe/issues)
- 💬 [Discussions](https://github.com/luxcrepe/luxcrepe/discussions)

---

**LuxCrepe**: Where traditional web scraping meets modern AI 🍰✨