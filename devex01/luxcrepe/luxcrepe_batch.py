# filename: luxcrepe_batch.py

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin, urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; UniversalLuxuryScraper/3.0; +https://example.com/bot)"
}

def extract_jsonld_products(soup, base_url):
    """Extract product data from JSON-LD scripts (for collection/listing pages)."""
    products = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except Exception:
            continue
        # Handle both single and list
        if isinstance(data, list):
            for entry in data:
                products.extend(parse_jsonld_entry(entry, base_url))
        else:
            products.extend(parse_jsonld_entry(data, base_url))
    return products

def parse_jsonld_entry(data, base_url):
    """Parse a JSON-LD entry for product info."""
    products = []
    # ItemList (list of products)
    if data.get("@type") in ["ItemList", "OfferCatalog"]:
        for item in data.get("itemListElement", []):
            if isinstance(item, dict) and "item" in item:
                products.extend(parse_jsonld_entry(item["item"], base_url))
            else:
                products.extend(parse_jsonld_entry(item, base_url))
    # Product
    elif data.get("@type") == "Product":
        prod = {
            "name": data.get("name"),
            "brand": data.get("brand", {}).get("name") if isinstance(data.get("brand"), dict) else data.get("brand"),
            "image": data.get("image"),
            "sku": data.get("sku"),
            "url": urljoin(base_url, data.get("url")) if data.get("url") else None,
        }
        offers = data.get("offers", {})
        if isinstance(offers, dict):
            prod["price"] = offers.get("price")
            prod["priceCurrency"] = offers.get("priceCurrency")
            prod["availability"] = offers.get("availability")
            prod["original_price"] = offers.get("PriceSpecification", {}).get("price")
            prod["offer_url"] = urljoin(base_url, offers.get("url")) if offers.get("url") else None
        products.append(prod)
    # ListItem (for ItemList)
    elif data.get("@type") == "ListItem":
        prod = {
            "name": data.get("name"),
            "url": urljoin(base_url, data.get("url")) if data.get("url") else None,
        }
        products.append(prod)
    return products

def extract_html_products(soup, base_url):
    """Extract product data from visible HTML product cards."""
    products = []
    containers = []
    for tag in ['li', 'div', 'article']:
        for elem in soup.find_all(tag):
            img = elem.find('img')
            a = elem.find('a', href=True)
            price = elem.find(string=lambda s: s and re.search(r'[\$\€\£\¥]\s?\d', s))
            if img and a and price:
                containers.append(elem)
    seen_links = set()
    for elem in containers:
        a = elem.find('a', href=True)
        link = urljoin(base_url, a['href']) if a else None
        if not link or link in seen_links:
            continue
        seen_links.add(link)
        name = None
        for tag in ['h2', 'h3', 'h4', 'span', 'p', 'div']:
            t = elem.find(tag)
            if t and t.get_text(strip=True):
                name = t.get_text(strip=True)
                break
        price = None
        orig_price = None
        discount = None
        for s in elem.stripped_strings:
            if re.search(r'[\$\€\£\¥]\s?\d', s):
                if not price:
                    price = s
                elif not orig_price and ("old" in s.lower() or "compare" in s.lower() or "retail" in s.lower()):
                    orig_price = s
            if "%" in s or "off" in s.lower() or "save" in s.lower():
                discount = s
        img = elem.find('img')
        image_url = img['src'] if img and img.has_attr('src') else (img['data-src'] if img and img.has_attr('data-src') else None)
        if image_url and not image_url.startswith('http'):
            image_url = urljoin(base_url, image_url)
        brand = None
        for tag in ['span', 'div']:
            b = elem.find(tag, class_=lambda x: x and 'brand' in x.lower())
            if b and b.get_text(strip=True):
                brand = b.get_text(strip=True)
                break
        products.append({
            "name": name,
            "brand": brand,
            "image": image_url,
            "price": price,
            "original_price": orig_price,
            "discount": discount,
            "url": link
        })
    return products

def merge_products(jsonld_products, html_products):
    """Merge products from JSON-LD and HTML by URL or name."""
    merged = []
    seen = set()
    for prod in jsonld_products + html_products:
        key = prod.get("url") or prod.get("name")
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(prod)
    return merged

def find_next_page(soup, current_url):
    """Try to find the next page URL for pagination."""
    link = soup.find("link", rel="next")
    if link and link.get("href"):
        return urljoin(current_url, link["href"])
    a = soup.find("a", string=re.compile(r'next', re.I))
    if a and a.get("href"):
        return urljoin(current_url, a["href"])
    m = re.search(r'([?&]page=)(\d+)', current_url)
    if m:
        next_page = int(m.group(2)) + 1
        return re.sub(r'([?&]page=)\d+', r'\g<1>{}'.format(next_page), current_url)
    return None

def advanced_universal_scrape(url, max_pages=3, delay=1):
    """Universal scraper with advanced heuristics and JSON-LD support."""
    all_products = []
    current_url = url
    for _ in range(max_pages):
        resp = requests.get(current_url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"[{url}] HTTP {resp.status_code}")
            break
        soup = BeautifulSoup(resp.text, "lxml")
        base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(current_url))
        jsonld_products = extract_jsonld_products(soup, base_url)
        html_products = extract_html_products(soup, base_url)
        merged = merge_products(jsonld_products, html_products)
        print(f"[{current_url}] {len(merged)} products found.")
        all_products.extend(merged)
        next_url = find_next_page(soup, current_url)
        if not next_url or next_url == current_url:
            break
        current_url = next_url
        time.sleep(delay)
    deduped = []
    seen = set()
    for prod in all_products:
        key = prod.get("url")
        if key and key not in seen:
            deduped.append(prod)
            seen.add(key)
    return deduped

# --- Product Detail Scraping ---

def extract_jsonld_product(soup, base_url):
    """Extract product data from JSON-LD scripts."""
    assets = {}
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except Exception:
            continue
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
            # Reviews
            review = data.get("review")
            if review:
                assets["reviews"] = review if isinstance(review, list) else [review]
            rating = data.get("aggregateRating")
            if rating:
                assets["aggregateRating"] = rating
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
    """Extract visible HTML assets, including all images, variants, and reviews."""
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
    # All images (including gallery, thumbnails, etc.)
    images = set()
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and not src.startswith("data:"):
            images.add(urljoin(base_url, src))
    # Also look for images in <a> tags (for zoom/gallery)
    for a in soup.find_all("a", href=True):
        if re.search(r'\.(jpg|jpeg|png|webp|gif)$', a['href'], re.I):
            images.add(urljoin(base_url, a['href']))
    if images:
        assets["images"] = list(images)
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
    # Reviews (look for review blocks, stars, etc.)
    reviews = []
    for review_block in soup.find_all(class_=re.compile("review|testimonial|comment", re.I)):
        text = review_block.get_text(" ", strip=True)
        if text and len(text) > 20:
            reviews.append(text)
    if reviews:
        assets["reviews"] = reviews
    # Custom attributes (look for data-attributes, tables, etc.)
    custom_attrs = {}
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) == 2:
                k = cells[0].get_text(strip=True)
                v = cells[1].get_text(strip=True)
                if k and v:
                    custom_attrs[k] = v
    if custom_attrs:
        assets["custom_attributes"] = custom_attrs
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

def batch_scrape_listing_and_details(listing_urls, max_pages=3, delay=1):
    """Batch pipeline: scrape listings, then drill into each product detail page."""
    all_listing_products = []
    for url in listing_urls:
        print(f"\nScraping listing: {url}")
        products = advanced_universal_scrape(url, max_pages=max_pages, delay=delay)
        all_listing_products.extend(products)
    # Deduplicate by URL
    product_urls = []
    seen = set()
    for prod in all_listing_products:
        if prod.get("url") and prod["url"] not in seen:
            product_urls.append(prod["url"])
            seen.add(prod["url"])
    print(f"\nTotal unique product detail URLs to scrape: {len(product_urls)}")
    all_assets = []
    for idx, url in enumerate(product_urls):
        print(f"[{idx+1}/{len(product_urls)}] Scraping product: {url}")
        assets = scrape_product_detail(url)
        if assets:
            all_assets.append(assets)
        time.sleep(delay)
    return all_assets

def main():
    # Example: Replace with your list of collection/listing URLs
    listing_urls = [
        "https://www.honeybirdette.com/collections/all-lingerie",
        # Add more collection/listing URLs here
    ]
    all_assets = batch_scrape_listing_and_details(listing_urls, max_pages=2, delay=1)
    with open("batch_luxury_product_assets.json", "w", encoding="utf-8") as f:
        json.dump(all_assets, f, indent=2, ensure_ascii=False)
    print(f"\nScraping complete. {len(all_assets)} products saved to batch_luxury_product_assets.json")

if __name__ == "__main__":
    main()

