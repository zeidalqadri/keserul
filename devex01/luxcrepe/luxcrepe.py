# filename: luxcrepe.py

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin, urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; UniversalLuxuryScraper/2.0; +https://example.com/bot)"
}

def extract_jsonld_products(soup, base_url):
    """Extract product data from JSON-LD scripts."""
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
            # Some have {"@type": "ListItem", "item": {...}}
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
        # Offers
        offers = data.get("offers", {})
        if isinstance(offers, dict):
            prod["price"] = offers.get("price")
            prod["priceCurrency"] = offers.get("priceCurrency")
            prod["availability"] = offers.get("availability")
            prod["original_price"] = offers.get("PriceSpecification", {}).get("price")
            prod["offer_url"] = urljoin(base_url, offers.get("url")) if offers.get("url") else None
        products.append(prod)
    return products

def extract_html_products(soup, base_url):
    """Extract product data from visible HTML product cards."""
    products = []
    # Heuristically find product containers
    containers = []
    for tag in ['li', 'div', 'article']:
        for elem in soup.find_all(tag):
            # Must have an image and a link
            img = elem.find('img')
            a = elem.find('a', href=True)
            price = elem.find(string=lambda s: s and re.search(r'[\$\€\£\¥]\s?\d', s))
            if img and a and price:
                containers.append(elem)
    seen_links = set()
    for elem in containers:
        # Product detail page URL
        a = elem.find('a', href=True)
        link = urljoin(base_url, a['href']) if a else None
        if not link or link in seen_links:
            continue
        seen_links.add(link)
        # Name
        name = None
        for tag in ['h2', 'h3', 'h4', 'span', 'p', 'div']:
            t = elem.find(tag)
            if t and t.get_text(strip=True):
                name = t.get_text(strip=True)
                break
        # Price
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
        # Image
        img = elem.find('img')
        image_url = img['src'] if img and img.has_attr('src') else (img['data-src'] if img and img.has_attr('data-src') else None)
        if image_url and not image_url.startswith('http'):
            image_url = urljoin(base_url, image_url)
        # Brand
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
    # Look for rel="next"
    link = soup.find("link", rel="next")
    if link and link.get("href"):
        return urljoin(current_url, link["href"])
    # Look for anchor with 'next' in text
    a = soup.find("a", string=re.compile(r'next', re.I))
    if a and a.get("href"):
        return urljoin(current_url, a["href"])
    # Try to increment ?page= or &page=
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
    # Deduplicate by URL
    deduped = []
    seen = set()
    for prod in all_products:
        key = prod.get("url")
        if key and key not in seen:
            deduped.append(prod)
            seen.add(key)
    return deduped

def main():
    print("Enter up to 9 sale/listing URLs (one per line, blank line to finish):")
    urls = []
    while len(urls) < 9:
        u = input(f"URL {len(urls)+1}: ").strip()
        if not u:
            break
        urls.append(u)
    if not urls:
        print("No URLs provided.")
        return

    all_results = []
    for url in urls:
        print(f"\nScraping {url} ...")
        products = advanced_universal_scrape(url)
        for p in products:
            p['source_url'] = url
        all_results.extend(products)

    with open("advanced_universal_luxury_womens_sale.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nScraping complete. {len(all_results)} products saved to advanced_universal_luxury_womens_sale.json")

if __name__ == "__main__":
    main()
