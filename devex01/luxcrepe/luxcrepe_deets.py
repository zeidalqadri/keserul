# filename: product_detail_asset_scraper.py

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; UniversalLuxuryScraper/2.0; +https://example.com/bot)"
}

def extract_jsonld_product(soup, base_url):
    """Extract product data from JSON-LD scripts."""
    assets = {}
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except Exception:
            continue
        # Product or Offer
        if isinstance(data, dict) and data.get("@type") == "Product":
            assets["name"] = data.get("name")
            assets["brand"] = data.get("brand", {}).get("name") if isinstance(data.get("brand"), dict) else data.get("brand")
            assets["description"] = data.get("description")
            assets["sku"] = data.get("sku")
            assets["images"] = data.get("image") if isinstance(data.get("image"), list) else [data.get("image")] if data.get("image") else []
            assets["url"] = urljoin(base_url, data.get("url")) if data.get("url") else None
            offers = data.get("offers", {})
            if isinstance(offers, dict):
                assets["price"] = offers.get("price")
                assets["priceCurrency"] = offers.get("priceCurrency")
                assets["availability"] = offers.get("availability")
                assets["original_price"] = offers.get("PriceSpecification", {}).get("price")
                assets["offer_url"] = urljoin(base_url, offers.get("url")) if offers.get("url") else None
    return assets

def extract_meta_tags(soup):
    """Extract OpenGraph and Twitter meta tags."""
    assets = {}
    for tag in soup.find_all("meta"):
        prop = tag.get("property") or tag.get("name")
        content = tag.get("content")
        if not prop or not content:
            continue
        if prop in ["og:title", "twitter:title"]:
            assets.setdefault("name", content)
        elif prop in ["og:description", "twitter:description"]:
            assets.setdefault("description", content)
        elif prop in ["og:image", "twitter:image"]:
            assets.setdefault("images", []).append(content)
        elif prop == "og:url":
            assets.setdefault("url", content)
        elif prop == "product:price:amount":
            assets.setdefault("price", content)
        elif prop == "product:price:currency":
            assets.setdefault("priceCurrency", content)
    return assets

def extract_html_assets(soup, base_url):
    """Extract visible HTML assets."""
    assets = {}
    # Name/title
    title = soup.find(["h1", "h2"], class_=re.compile("title|name", re.I)) or soup.find("h1") or soup.find("title")
    if title:
        assets["name"] = title.get_text(strip=True)
    # Description
    desc = soup.find("div", class_=re.compile("description|desc|product-info", re.I))
    if desc:
        assets["description"] = desc.get_text(" ", strip=True)
    # Price
    price = soup.find(string=re.compile(r'[\$\€\£\¥]\s?\d'))
    if price:
        assets["price"] = price.strip()
    # Images
    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and not src.startswith("data:"):
            images.append(urljoin(base_url, src))
    if images:
        assets["images"] = list(set(images))
    # Variants/options
    variants = []
    for option in soup.find_all("option"):
        val = option.get_text(strip=True)
        if val and val.lower() not in ["select", "choose"]:
            variants.append(val)
    if variants:
        assets["variants"] = variants
    # Availability
    sold_out = soup.find(string=re.compile(r'sold out|unavailable|out of stock', re.I))
    if sold_out:
        assets["availability"] = "OutOfStock"
    else:
        assets["availability"] = "InStock"
    return assets

def merge_dicts(*dicts):
    """Merge dictionaries, preferring first non-empty value for each key."""
    result = {}
    for d in dicts:
        for k, v in d.items():
            if k not in result or not result[k]:
                result[k] = v
    return result

def scrape_product_detail(url):
    """Scrape all assets from a product detail page."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"[{url}] HTTP {resp.status_code}")
            return None
        soup = BeautifulSoup(resp.text, "lxml")
        base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
        jsonld = extract_jsonld_product(soup, base_url)
        meta = extract_meta_tags(soup)
        html = extract_html_assets(soup, base_url)
        assets = merge_dicts(jsonld, meta, html)
        assets["url"] = url  # Always include the detail page URL
        return assets
    except Exception as e:
        print(f"[{url}] Error: {e}")
        return None

def main():
    # Example: Replace with your list of product URLs
    product_urls = [
        "https://www.honeybirdette.com/products/whitney-underwire-balconette-ocean",
        "https://www.honeybirdette.com/products/whitney-bustier-ocean",
        # ... add more URLs here
    ]
    all_assets = []
    for url in product_urls:
        print(f"Scraping {url} ...")
        assets = scrape_product_detail(url)
        if assets:
            all_assets.append(assets)
        time.sleep(1)  # Be polite
    print(json.dumps(all_assets, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

