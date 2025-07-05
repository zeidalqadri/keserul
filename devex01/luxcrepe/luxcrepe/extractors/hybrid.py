"""
Hybrid extraction system combining rule-based and ML approaches
"""

import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

from .traditional import TraditionalExtractor
from ..ml.inference.predictor import (
    ProductDetectionPredictor,
    PriceExtractionPredictor, 
    BrandExtractionPredictor,
    EnsemblePredictor
)
from ..core.utils import merge_dicts, validate_product_data
from ..core.config import get_config

logger = logging.getLogger(__name__)


class HybridExtractor:
    """Intelligent extraction using both rule-based and ML approaches"""
    
    def __init__(self):
        self.config = get_config()
        self.traditional_extractor = TraditionalExtractor()
        
        # Initialize ML predictors
        self.ml_predictors = []
        if self.config.ml.use_ml:
            try:
                self._initialize_ml_predictors()
            except Exception as e:
                logger.warning(f"Failed to initialize ML predictors: {e}")
                logger.info("Falling back to rule-based extraction only")
    
    def _initialize_ml_predictors(self) -> None:
        """Initialize and load ML prediction models"""
        # Product detection
        product_detector = ProductDetectionPredictor(
            confidence_threshold=self.config.ml.model_confidence_threshold
        )
        product_detector.load_model()
        if product_detector.is_available():
            self.ml_predictors.append(product_detector)
        
        # Price extraction
        price_extractor = PriceExtractionPredictor(
            confidence_threshold=self.config.ml.model_confidence_threshold
        )
        price_extractor.load_model()
        if price_extractor.is_available():
            self.ml_predictors.append(price_extractor)
        
        # Brand extraction
        brand_extractor = BrandExtractionPredictor(
            confidence_threshold=self.config.ml.model_confidence_threshold
        )
        brand_extractor.load_model()
        if brand_extractor.is_available():
            self.ml_predictors.append(brand_extractor)
        
        logger.info(f"Initialized {len(self.ml_predictors)} ML predictors")
    
    def extract_products_from_listing(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract products from listing/collection page using hybrid approach"""
        # Step 1: Rule-based extraction (fast, baseline)
        traditional_products = self._extract_traditional_products(soup, base_url)
        
        # Step 2: ML enhancement (if available)
        if self.ml_predictors and self.config.ml.use_ml:
            enhanced_products = self._enhance_with_ml(traditional_products, soup, base_url)
        else:
            enhanced_products = traditional_products
        
        # Step 3: Quality validation and scoring
        validated_products = self._validate_and_score_products(enhanced_products)
        
        # Step 4: Ensemble decision making
        final_products = self._make_ensemble_decisions(validated_products)
        
        return final_products
    
    def extract_product_detail(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract comprehensive product data from detail page"""
        # Traditional extraction
        traditional_data = self.traditional_extractor.extract_product_detail(soup, base_url)
        
        # ML enhancement
        if self.ml_predictors and self.config.ml.use_ml:
            ml_data = self._extract_ml_product_detail(soup, base_url)
            product_data = merge_dicts(traditional_data, ml_data)
        else:
            product_data = traditional_data
        
        # Quality validation
        validation_result = validate_product_data(
            product_data,
            self.config.quality.required_fields
        )
        
        product_data["_quality_score"] = validation_result["score"]
        product_data["_validation_issues"] = validation_result["issues"]
        
        return product_data
    
    def _extract_traditional_products(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract products using traditional rule-based methods"""
        # JSON-LD extraction
        jsonld_products = self.traditional_extractor.extract_jsonld_products(soup, base_url)
        
        # HTML extraction
        html_products = self.traditional_extractor.extract_html_products(soup, base_url)
        
        # Merge and deduplicate
        all_products = []
        seen_urls = set()
        
        for product in jsonld_products + html_products:
            url = product.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                product["_extraction_method"] = "traditional"
                all_products.append(product)
        
        return all_products
    
    def _enhance_with_ml(self, products: List[Dict[str, Any]], soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Enhance traditional extraction with ML predictions"""
        enhanced_products = []
        
        for product in products:
            enhanced_product = product.copy()
            
            # Get product element if available (for context)
            product_url = product.get("url")
            product_element = self._find_product_element_by_url(soup, product_url)
            
            if product_element:
                # ML-based enhancement
                ml_data = self._extract_ml_data_from_element(product_element, base_url)
                
                # Merge ML data with traditional data
                enhanced_product = merge_dicts(enhanced_product, ml_data)
                enhanced_product["_extraction_method"] = "hybrid"
                
                # Add confidence scores
                enhanced_product["_ml_confidence"] = self._calculate_ml_confidence(ml_data)
            
            enhanced_products.append(enhanced_product)
        
        return enhanced_products
    
    def _extract_ml_product_detail(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract product data using ML for detail pages"""
        ml_data = {}
        
        if not self.ml_predictors:
            return ml_data
        
        # Create ensemble predictor
        ensemble = EnsemblePredictor(self.ml_predictors, self.config.ml.ensemble_voting)
        
        # Extract text content for NLP models
        text_content = soup.get_text()
        
        # Use ensemble to predict product data
        predictions = ensemble.predict_product_data(soup, text_content)
        
        # Convert predictions to product data format
        if "price_data" in predictions:
            price_data = predictions["price_data"]
            if isinstance(price_data, dict):
                ml_data.update({
                    "price": price_data.get("amount"),
                    "priceCurrency": price_data.get("currency"),
                    "_price_confidence": predictions.get("price_confidence", 0.0)
                })
        
        if "brand" in predictions:
            ml_data["brand"] = predictions["brand"]
            ml_data["_brand_confidence"] = predictions.get("brand_confidence", 0.0)
        
        return ml_data
    
    def _find_product_element_by_url(self, soup: BeautifulSoup, product_url: str) -> Optional:
        """Find the HTML element containing a specific product URL"""
        if not product_url:
            return None
        
        # Look for anchor tags with matching href
        for a in soup.find_all("a", href=True):
            if product_url in a['href'] or a['href'] in product_url:
                # Return the parent container that likely contains product info
                parent = a.parent
                while parent and parent.name not in ['html', 'body']:
                    # Check if this parent has product-like content
                    if (parent.find('img') and 
                        len(parent.get_text().strip()) > 20):
                        return parent
                    parent = parent.parent
                return a.parent
        
        return None
    
    def _extract_ml_data_from_element(self, element, base_url: str) -> Dict[str, Any]:
        """Extract data from element using ML predictors"""
        ml_data = {}
        
        if not self.ml_predictors:
            return ml_data
        
        # Create ensemble predictor
        ensemble = EnsemblePredictor(self.ml_predictors, self.config.ml.ensemble_voting)
        
        # Extract text content
        text_content = element.get_text()
        
        # Get ML predictions
        predictions = ensemble.predict_product_data(element, text_content)
        
        # Convert to product data format
        if "price_data" in predictions:
            price_data = predictions["price_data"]
            if isinstance(price_data, dict):
                ml_data.update({
                    "price_ml": price_data.get("amount"),
                    "priceCurrency_ml": price_data.get("currency"),
                    "_price_confidence": predictions.get("price_confidence", 0.0)
                })
        
        if "brand" in predictions:
            ml_data["brand_ml"] = predictions["brand"]
            ml_data["_brand_confidence"] = predictions.get("brand_confidence", 0.0)
        
        if "is_product" in predictions:
            ml_data["_product_confidence"] = predictions["is_product"]
        
        return ml_data
    
    def _calculate_ml_confidence(self, ml_data: Dict[str, Any]) -> float:
        """Calculate overall ML confidence score"""
        confidence_scores = []
        
        # Collect all confidence scores
        for key, value in ml_data.items():
            if key.endswith("_confidence") and isinstance(value, (int, float)):
                confidence_scores.append(value)
        
        if not confidence_scores:
            return 0.0
        
        # Return average confidence
        return sum(confidence_scores) / len(confidence_scores)
    
    def _validate_and_score_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate product data quality and add quality scores"""
        validated_products = []
        
        for product in products:
            validation_result = validate_product_data(
                product,
                self.config.quality.required_fields
            )
            
            # Add quality metadata
            product["_quality_score"] = validation_result["score"]
            product["_validation_issues"] = validation_result["issues"]
            product["_is_valid"] = validation_result["is_valid"]
            
            # Only include products that meet minimum quality threshold
            if validation_result["score"] >= self.config.quality.quality_threshold:
                validated_products.append(product)
            else:
                logger.debug(f"Product failed quality threshold: {validation_result['issues']}")
        
        return validated_products
    
    def _make_ensemble_decisions(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Make final decisions using ensemble of traditional and ML data"""
        final_products = []
        
        for product in products:
            final_product = product.copy()
            
            # Ensemble decision for price
            final_product = self._ensemble_price_decision(final_product)
            
            # Ensemble decision for brand
            final_product = self._ensemble_brand_decision(final_product)
            
            # Remove temporary ML fields
            final_product = self._clean_temporary_fields(final_product)
            
            final_products.append(final_product)
        
        return final_products
    
    def _ensemble_price_decision(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Make ensemble decision for price field"""
        traditional_price = product.get("price")
        ml_price = product.get("price_ml")
        ml_confidence = product.get("_price_confidence", 0.0)
        
        if self.config.ml.ensemble_voting == "weighted":
            # Use ML price if confidence is high enough
            if ml_price and ml_confidence >= self.config.ml.model_confidence_threshold:
                product["price"] = ml_price
                product["priceCurrency"] = product.get("priceCurrency_ml", product.get("priceCurrency"))
                product["_price_source"] = "ml"
            elif traditional_price:
                product["_price_source"] = "traditional"
        
        elif self.config.ml.ensemble_voting == "confidence":
            # Always use the source with higher confidence
            if ml_price and ml_confidence > 0.7:  # Assume traditional has 0.7 confidence
                product["price"] = ml_price
                product["priceCurrency"] = product.get("priceCurrency_ml", product.get("priceCurrency"))
                product["_price_source"] = "ml"
            elif traditional_price:
                product["_price_source"] = "traditional"
        
        return product
    
    def _ensemble_brand_decision(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Make ensemble decision for brand field"""
        traditional_brand = product.get("brand")
        ml_brand = product.get("brand_ml")
        ml_confidence = product.get("_brand_confidence", 0.0)
        
        if self.config.ml.ensemble_voting == "weighted":
            if ml_brand and ml_confidence >= self.config.ml.model_confidence_threshold:
                product["brand"] = ml_brand
                product["_brand_source"] = "ml"
            elif traditional_brand:
                product["_brand_source"] = "traditional"
        
        return product
    
    def _clean_temporary_fields(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Remove temporary ML fields from final product"""
        temp_fields = [key for key in product.keys() if key.endswith("_ml")]
        for field in temp_fields:
            product.pop(field, None)
        return product
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get statistics about extraction capabilities"""
        return {
            "ml_available": len(self.ml_predictors) > 0,
            "ml_predictors": len(self.ml_predictors),
            "traditional_available": True,
            "extraction_methods": ["traditional", "ml", "hybrid"],
            "ensemble_voting": self.config.ml.ensemble_voting,
            "quality_threshold": self.config.quality.quality_threshold
        }