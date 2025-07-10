"""
Traditional rule-based extraction methods
Refactored from original luxcrepe scripts
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from ..core.utils import (
    safe_extract_text, normalize_url, extract_price_components,
    merge_dicts, find_next_page_url
)

logger = logging.getLogger(__name__)


class TraditionalExtractor:
    """Rule-based extraction using original LuxCrepe logic"""
    
    def __init__(self):
        self.name = "traditional_extractor"
    
    def extract_jsonld_products(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract product data from JSON-LD scripts"""
        products = []
        
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
            except (json.JSONDecodeError, TypeError, AttributeError):
                continue
            
            # Handle both single and list
            if isinstance(data, list):
                for entry in data:
                    products.extend(self._parse_jsonld_entry(entry, base_url))
            else:
                products.extend(self._parse_jsonld_entry(data, base_url))
        
        return products
    
    def _parse_jsonld_entry(self, data: Dict[str, Any], base_url: str) -> List[Dict[str, Any]]:
        """Parse a JSON-LD entry for product info"""
        products = []
        
        if not isinstance(data, dict):
            return products
        
        # ItemList (list of products)
        if data.get("@type") in ["ItemList", "OfferCatalog"]:
            for item in data.get("itemListElement", []):
                if isinstance(item, dict) and "item" in item:
                    products.extend(self._parse_jsonld_entry(item["item"], base_url))
                else:
                    products.extend(self._parse_jsonld_entry(item, base_url))
        
        # Product
        elif data.get("@type") == "Product":
            product = {
                "name": data.get("name"),
                "brand": self._extract_brand_from_jsonld(data.get("brand")),
                "image": data.get("image"),
                "sku": data.get("sku"),
                "url": normalize_url(data.get("url", ""), base_url),
                "description": data.get("description")
            }
            
            # Handle offers
            offers = data.get("offers", {})
            if isinstance(offers, dict):
                product.update({
                    "price": offers.get("price"),
                    "priceCurrency": offers.get("priceCurrency"),
                    "availability": offers.get("availability"),
                    "offer_url": normalize_url(offers.get("url", ""), base_url)
                })
                
                # Handle PriceSpecification
                price_spec = offers.get("PriceSpecification", {})
                if isinstance(price_spec, dict):
                    product["original_price"] = price_spec.get("price")
            
            # Handle reviews and ratings
            review = data.get("review")
            if review:
                product["reviews"] = review if isinstance(review, list) else [review]
            
            rating = data.get("aggregateRating")
            if rating:
                product["aggregateRating"] = rating
            
            products.append(product)
        
        # ListItem
        elif data.get("@type") == "ListItem":
            product = {
                "name": data.get("name"),
                "url": normalize_url(data.get("url", ""), base_url)
            }
            products.append(product)
        
        return products
    
    def _extract_brand_from_jsonld(self, brand_data: Any) -> Optional[str]:
        """Extract brand name from JSON-LD brand field"""
        if isinstance(brand_data, dict):
            return brand_data.get("name")
        elif isinstance(brand_data, str):
            return brand_data
        return None
    
    def extract_html_products(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract product data from visible HTML product cards"""
        products = []
        containers = self._find_product_containers(soup)
        seen_links = set()
        
        for elem in containers:
            product = self._extract_product_from_container(elem, base_url)
            if product and product.get("url") and product["url"] not in seen_links:
                seen_links.add(product["url"])
                products.append(product)
        
        return products
    
    def _find_product_containers(self, soup: BeautifulSoup) -> List:
        """Find potential product containers using heuristics"""
        containers = []
        
        # Look for elements that contain product-like content
        for tag in ['li', 'div', 'article']:
            for elem in soup.find_all(tag):
                if self._is_likely_product_container(elem):
                    containers.append(elem)
        
        return containers
    
    def _is_likely_product_container(self, elem) -> bool:
        """Check if element is likely a product container"""
        # Must have an image and a link
        img = elem.find('img')
        a = elem.find('a', href=True)
        
        if not (img and a):
            return False
        
        # Look for price indicators
        text = elem.get_text()
        price_found = bool(re.search(r'[\$\€\£\¥]\s?\d', text))
        
        # Check for product-like class names
        class_names = ' '.join(elem.get('class', [])).lower()
        product_indicators = ['product', 'item', 'card', 'listing', 'tile']
        has_product_class = any(indicator in class_names for indicator in product_indicators)
        
        # Avoid navigation/footer elements
        nav_indicators = ['nav', 'footer', 'header', 'menu', 'breadcrumb']
        is_navigation = any(indicator in class_names for indicator in nav_indicators)
        
        return (price_found or has_product_class) and not is_navigation
    
    def _extract_product_from_container(self, elem, base_url: str) -> Dict[str, Any]:
        """Extract product data from a container element"""
        product = {}
        
        # Product detail page URL
        a = elem.find('a', href=True)
        if a:
            product["url"] = normalize_url(a['href'], base_url)
        
        # Product name
        name = self._extract_product_name(elem)
        if name:
            product["name"] = name
        
        # Price information
        price_info = self._extract_price_info(elem)
        product.update(price_info)
        
        # Image
        img = elem.find('img')
        if img:
            image_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if image_url:
                product["image"] = normalize_url(image_url, base_url)
        
        # Brand
        brand = self._extract_brand_from_html(elem)
        if brand:
            product["brand"] = brand
        
        # Additional attributes
        product.update(self._extract_additional_attributes(elem))
        
        return product
    
    def _extract_product_name(self, elem) -> Optional[str]:
        """Extract product name from element"""
        # Look for heading tags first
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            heading = elem.find(tag)
            if heading:
                name = safe_extract_text(heading)
                if name and len(name) > 2:
                    return name
        
        # Look for elements with name-like classes
        name_selectors = [
            '[class*="name"]',
            '[class*="title"]',
            '[class*="product"]'
        ]
        
        for selector in name_selectors:
            name_elem = elem.select_one(selector)
            if name_elem:
                name = safe_extract_text(name_elem)
                if name and len(name) > 2:
                    return name
        
        # Fallback: first meaningful text
        for tag in ['span', 'p', 'div']:
            text_elem = elem.find(tag)
            if text_elem:
                text = safe_extract_text(text_elem)
                if text and 5 <= len(text) <= 100:
                    return text
        
        return None
    
    def _extract_price_info(self, elem) -> Dict[str, Any]:
        """Extract price information from element"""
        price_info = {}
        
        # Get all text content
        text = elem.get_text()
        
        # Find all potential price strings
        price_strings = []
        for string in elem.stripped_strings:
            if re.search(r'[\$\€\£\¥]\s?\d', string):
                price_strings.append(string)
        
        if not price_strings:
            return price_info
        
        # Categorize prices
        current_price = None
        original_price = None
        discount = None
        
        for price_str in price_strings:
            # Check for sale/discount indicators
            if any(indicator in price_str.lower() 
                   for indicator in ["was", "old", "compare", "retail", "msrp"]):
                if not original_price:
                    price_data = extract_price_components(price_str)
                    if price_data.get('amount'):
                        original_price = price_data
            elif not current_price:
                price_data = extract_price_components(price_str)
                if price_data.get('amount'):
                    current_price = price_data
        
        # Look for discount information
        for string in elem.stripped_strings:
            if any(indicator in string.lower() 
                   for indicator in ["off", "save", "discount"]) and "%" in string:
                discount = string
                break
        
        # Set price information
        if current_price:
            price_info["price"] = current_price.get('amount')
            price_info["priceCurrency"] = current_price.get('currency')
            price_info["price_text"] = current_price.get('original_text')
        
        if original_price:
            price_info["original_price"] = original_price.get('amount')
            price_info["original_price_text"] = original_price.get('original_text')
        
        if discount:
            price_info["discount"] = discount
        
        return price_info
    
    def _extract_brand_from_html(self, elem) -> Optional[str]:
        """Extract brand from HTML element"""
        # Look for brand-specific class names
        brand_selectors = [
            '[class*="brand"]',
            '[class*="designer"]',
            '[class*="maker"]',
            '[data-brand]'
        ]
        
        for selector in brand_selectors:
            brand_elem = elem.select_one(selector)
            if brand_elem:
                brand = safe_extract_text(brand_elem)
                if brand and len(brand) > 1:
                    return brand
        
        # Check data attributes
        brand = elem.get('data-brand')
        if brand:
            return brand
        
        return None
    
    def _extract_additional_attributes(self, elem) -> Dict[str, Any]:
        """Extract additional product attributes"""
        attrs = {}
        
        # Availability
        text = elem.get_text().lower()
        if any(indicator in text for indicator in ['sold out', 'unavailable', 'out of stock']):
            attrs["availability"] = "OutOfStock"
        else:
            attrs["availability"] = "InStock"
        
        # Variants/options (look for select/option elements)
        variants = []
        for option in elem.find_all("option"):
            val = safe_extract_text(option)
            if val and val.lower() not in ["select", "choose", "pick"]:
                variants.append(val)
        
        if variants:
            attrs["variants"] = variants
        
        # Rating/reviews count
        rating_elem = elem.find(class_=re.compile(r'rating|star', re.I))
        if rating_elem:
            rating_text = safe_extract_text(rating_elem)
            if rating_text:
                attrs["rating_text"] = rating_text
        
        return attrs
    
    def extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract OpenGraph and Twitter meta tags"""
        meta_data = {}
        
        for tag in soup.find_all("meta"):
            prop = tag.get("property") or tag.get("name")
            content = tag.get("content")
            
            if not prop or not content:
                continue
            
            # Product information
            if prop in ["og:title", "twitter:title"]:
                meta_data.setdefault("name", content)
            elif prop in ["og:description", "twitter:description"]:
                meta_data.setdefault("description", content)
            elif prop in ["og:image", "twitter:image"]:
                meta_data.setdefault("images", []).append(content)
            elif prop == "og:url":
                meta_data.setdefault("url", content)
            elif prop == "product:price:amount":
                meta_data.setdefault("price", content)
            elif prop == "product:price:currency":
                meta_data.setdefault("priceCurrency", content)
            elif prop in ["og:brand", "product:brand"]:
                meta_data.setdefault("brand", content)
        
        return meta_data
    
    def extract_product_detail(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract comprehensive product data from detail page"""
        # Combine all extraction methods
        jsonld_data = self.extract_jsonld_products(soup, base_url)
        meta_data = self.extract_meta_tags(soup)
        html_data = self._extract_detail_html_data(soup, base_url)
        
        # Merge data sources
        product_data = merge_dicts(
            jsonld_data[0] if jsonld_data else {},
            meta_data,
            html_data
        )
        
        # Ensure URL is set
        product_data["url"] = base_url
        
        return product_data
    
    def _extract_detail_html_data(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract data specifically for product detail pages"""
        data = {}
        
        # Product title/name
        title_selectors = [
            'h1[class*="product"]',
            'h1[class*="title"]',
            'h1[class*="name"]',
            'h1',
            '.product-name',
            '.product-title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                data["name"] = safe_extract_text(title_elem)
                break
        
        # Description
        desc_selectors = [
            '.product-description',
            '.description',
            '[class*="desc"]',
            '.product-details'
        ]
        
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                data["description"] = safe_extract_text(desc_elem)
                break
        
        # All images
        images = set()
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if src and not src.startswith("data:"):
                images.add(normalize_url(src, base_url))
        
        # Also check for high-res images in links
        for a in soup.find_all("a", href=True):
            if re.search(r'\.(jpg|jpeg|png|webp|gif)$', a['href'], re.I):
                images.add(normalize_url(a['href'], base_url))
        
        if images:
            data["images"] = list(images)
        
        # Price (more detailed for product pages)
        price_selectors = [
            '.price',
            '.product-price',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = safe_extract_text(price_elem)
                if price_text:
                    price_data = extract_price_components(price_text)
                    if price_data.get('amount'):
                        data.update({
                            "price": price_data['amount'],
                            "priceCurrency": price_data.get('currency'),
                            "price_text": price_data['original_text']
                        })
                        break
        
        return data