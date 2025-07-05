"""
ML model inference and prediction components
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """Container for ML model predictions"""
    value: Any
    confidence: float
    model_name: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MLPredictor:
    """Base class for ML-based predictions"""
    
    def __init__(self, model_name: str, confidence_threshold: float = 0.7):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.is_loaded = False
    
    def load_model(self) -> None:
        """Load the ML model (to be implemented by subclasses)"""
        raise NotImplementedError
    
    def predict(self, input_data: Any) -> Prediction:
        """Make prediction on input data"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if model is available and loaded"""
        return self.is_loaded


class ProductDetectionPredictor(MLPredictor):
    """Computer vision-based product detection"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        super().__init__("product_detector", confidence_threshold)
        self.model = None
    
    def load_model(self) -> None:
        """Load YOLO-based product detection model"""
        try:
            # For now, implement a rule-based fallback
            # TODO: Implement actual YOLO model loading
            self.is_loaded = True
            logger.info("Product detection model loaded (rule-based fallback)")
        except Exception as e:
            logger.error(f"Failed to load product detection model: {e}")
            self.is_loaded = False
    
    def predict(self, html_elements: List[Any]) -> List[Prediction]:
        """Predict which HTML elements are product cards"""
        if not self.is_loaded:
            return []
        
        predictions = []
        
        for i, element in enumerate(html_elements):
            # Rule-based product detection (enhanced version)
            confidence = self._calculate_product_confidence(element)
            
            if confidence >= self.confidence_threshold:
                prediction = Prediction(
                    value=True,
                    confidence=confidence,
                    model_name=self.model_name,
                    metadata={'element_index': i, 'method': 'rule_based'}
                )
                predictions.append(prediction)
        
        return predictions
    
    def _calculate_product_confidence(self, element) -> float:
        """Calculate confidence that element is a product card"""
        score = 0.0
        max_score = 100.0
        
        # Check for image
        if element.find('img'):
            score += 25
        
        # Check for link
        if element.find('a', href=True):
            score += 20
        
        # Check for price indicators
        price_patterns = [
            r'[\$\€\£\¥]\s?\d',
            r'\d+\.\d{2}',
            r'price',
            r'cost'
        ]
        text = element.get_text().lower()
        for pattern in price_patterns:
            if re.search(pattern, text):
                score += 15
                break
        
        # Check for product-like class names
        class_names = ' '.join(element.get('class', []))
        product_indicators = ['product', 'item', 'card', 'listing', 'tile']
        for indicator in product_indicators:
            if indicator in class_names.lower():
                score += 10
                break
        
        # Check for brand/name indicators
        if element.find(['h1', 'h2', 'h3', 'h4']):
            score += 10
        
        # Penalty for navigation/footer elements
        nav_indicators = ['nav', 'footer', 'header', 'menu', 'breadcrumb']
        for indicator in nav_indicators:
            if indicator in class_names.lower():
                score -= 20
                break
        
        return max(0, min(score / max_score, 1.0))


class PriceExtractionPredictor(MLPredictor):
    """NLP-based price extraction and normalization"""
    
    def __init__(self, confidence_threshold: float = 0.8):
        super().__init__("price_extractor", confidence_threshold)
    
    def load_model(self) -> None:
        """Load BERT-based NER model for price extraction"""
        try:
            # For now, implement enhanced rule-based approach
            # TODO: Implement actual BERT model loading
            self.is_loaded = True
            logger.info("Price extraction model loaded (rule-based fallback)")
        except Exception as e:
            logger.error(f"Failed to load price extraction model: {e}")
            self.is_loaded = False
    
    def predict(self, text_content: str) -> Optional[Prediction]:
        """Extract and normalize price from text"""
        if not self.is_loaded or not text_content:
            return None
        
        # Enhanced price extraction patterns
        price_patterns = [
            # Currency symbol before amount
            r'([\$\€\£\¥])\s?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            # Amount before currency symbol
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s?([\$\€\£\¥])',
            # Amount with currency code
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s?(USD|EUR|GBP|JPY|CAD|AUD)',
            # Sale price patterns
            r'(?i)(?:sale|now|price)[:;]?\s*([\$\€\£\¥])\s?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            # From price patterns
            r'(?i)from\s*([\$\€\£\¥])\s?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        best_match = None
        best_confidence = 0.0
        
        for pattern_idx, pattern in enumerate(price_patterns):
            matches = re.finditer(pattern, text_content)
            
            for match in matches:
                groups = match.groups()
                confidence = self._calculate_price_confidence(match, text_content, pattern_idx)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = {
                        'groups': groups,
                        'match': match,
                        'pattern_idx': pattern_idx
                    }
        
        if best_match and best_confidence >= self.confidence_threshold:
            price_data = self._parse_price_match(best_match)
            return Prediction(
                value=price_data,
                confidence=best_confidence,
                model_name=self.model_name,
                metadata={'pattern_used': best_match['pattern_idx']}
            )
        
        return None
    
    def _calculate_price_confidence(self, match, text: str, pattern_idx: int) -> float:
        """Calculate confidence score for price match"""
        base_confidence = 0.7  # Base confidence for pattern match
        
        # Pattern-specific confidence adjustments
        pattern_confidences = [0.9, 0.8, 0.85, 0.95, 0.9]  # Confidence by pattern index
        confidence = pattern_confidences[min(pattern_idx, len(pattern_confidences) - 1)]
        
        # Context-based adjustments
        context_before = text[max(0, match.start() - 20):match.start()].lower()
        context_after = text[match.end():min(len(text), match.end() + 20)].lower()
        
        # Positive indicators
        positive_indicators = ['price', 'cost', 'sale', 'now', 'was', 'retail', 'msrp']
        for indicator in positive_indicators:
            if indicator in context_before or indicator in context_after:
                confidence += 0.1
                break
        
        # Negative indicators
        negative_indicators = ['id', 'code', 'zip', 'phone', 'year', 'quantity', 'qty']
        for indicator in negative_indicators:
            if indicator in context_before or indicator in context_after:
                confidence -= 0.2
                break
        
        return max(0.0, min(confidence, 1.0))
    
    def _parse_price_match(self, match_data: Dict) -> Dict[str, Any]:
        """Parse price match into structured data"""
        groups = match_data['groups']
        
        # Currency mapping
        currency_map = {
            '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY',
            'USD': 'USD', 'EUR': 'EUR', 'GBP': 'GBP', 'JPY': 'JPY',
            'CAD': 'CAD', 'AUD': 'AUD'
        }
        
        if len(groups) >= 2:
            # Determine which group is amount and which is currency
            amount_str = groups[1] if groups[0] in currency_map else groups[0]
            currency_str = groups[0] if groups[0] in currency_map else groups[1]
            
            try:
                amount = float(amount_str.replace(',', ''))
                currency = currency_map.get(currency_str, currency_str)
                
                return {
                    'amount': amount,
                    'currency': currency,
                    'original_text': match_data['match'].group(0)
                }
            except ValueError:
                pass
        
        return {'original_text': match_data['match'].group(0)}


class BrandExtractionPredictor(MLPredictor):
    """Brand name extraction and classification"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        super().__init__("brand_extractor", confidence_threshold)
        self.known_brands = set()  # Could be loaded from external source
    
    def load_model(self) -> None:
        """Load brand classification model"""
        try:
            # Load known luxury brands (could be from database/API)
            self._load_known_brands()
            self.is_loaded = True
            logger.info("Brand extraction model loaded")
        except Exception as e:
            logger.error(f"Failed to load brand extraction model: {e}")
            self.is_loaded = False
    
    def predict(self, text_elements: List[str]) -> Optional[Prediction]:
        """Extract brand name from text elements"""
        if not self.is_loaded:
            return None
        
        best_brand = None
        best_confidence = 0.0
        
        for text in text_elements:
            if not text:
                continue
            
            # Check against known brands
            for brand in self.known_brands:
                if brand.lower() in text.lower():
                    confidence = self._calculate_brand_confidence(brand, text)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_brand = brand
        
        if best_brand and best_confidence >= self.confidence_threshold:
            return Prediction(
                value=best_brand,
                confidence=best_confidence,
                model_name=self.model_name
            )
        
        return None
    
    def _load_known_brands(self) -> None:
        """Load known luxury brands"""
        # Sample luxury brands - in production, this would come from a comprehensive database
        luxury_brands = [
            'Chanel', 'Louis Vuitton', 'Hermès', 'Gucci', 'Prada', 'Dior', 'Versace',
            'Armani', 'Dolce & Gabbana', 'Valentino', 'Givenchy', 'Saint Laurent',
            'Balenciaga', 'Bottega Veneta', 'Fendi', 'Moschino', 'Burberry', 'Cartier',
            'Tiffany & Co', 'Van Cleef & Arpels', 'Bulgari', 'Chopard', 'Rolex',
            'Patek Philippe', 'Audemars Piguet', 'Vacheron Constantin', 'Agent Provocateur',
            'La Perla', 'Honey Birdette', 'Fleur du Mal', 'Kiki de Montparnasse'
        ]
        self.known_brands.update(luxury_brands)
    
    def _calculate_brand_confidence(self, brand: str, text: str) -> float:
        """Calculate confidence for brand match"""
        base_confidence = 0.8
        
        # Exact case match gets higher confidence
        if brand in text:
            base_confidence += 0.1
        
        # Check if brand appears at start of text (common for product names)
        if text.lower().startswith(brand.lower()):
            base_confidence += 0.1
        
        # Check context for brand indicators
        brand_indicators = ['by', 'from', 'collection', 'designer']
        for indicator in brand_indicators:
            if indicator in text.lower():
                base_confidence += 0.05
                break
        
        return min(base_confidence, 1.0)


class EnsemblePredictor:
    """Ensemble predictor that combines multiple ML models"""
    
    def __init__(self, predictors: List[MLPredictor], voting_method: str = "weighted"):
        self.predictors = predictors
        self.voting_method = voting_method
    
    def predict_product_data(self, html_element, text_content: str) -> Dict[str, Any]:
        """Use ensemble of predictors to extract product data"""
        result = {}
        
        # Product detection
        for predictor in self.predictors:
            if isinstance(predictor, ProductDetectionPredictor):
                predictions = predictor.predict([html_element])
                if predictions:
                    result['is_product'] = predictions[0].confidence
        
        # Price extraction
        for predictor in self.predictors:
            if isinstance(predictor, PriceExtractionPredictor):
                prediction = predictor.predict(text_content)
                if prediction:
                    result['price_data'] = prediction.value
                    result['price_confidence'] = prediction.confidence
        
        # Brand extraction
        text_elements = [text_content]  # Could be enhanced to extract from multiple elements
        for predictor in self.predictors:
            if isinstance(predictor, BrandExtractionPredictor):
                prediction = predictor.predict(text_elements)
                if prediction:
                    result['brand'] = prediction.value
                    result['brand_confidence'] = prediction.confidence
        
        return result