import os
import requests
from urllib.parse import urlparse, parse_qs
import json
import time
import random
from pathlib import Path

OUTPUT_DIR = Path("dataset/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DOCUMENT_QUERIES = {
    "id_card": [
        "carte d'identité nationale",
        "ID card photo",
        "CIN card",
        "national identity card",
    ],
    "driver_license": [
        "driver license photo",
        "permis de conduire",
        "driving license card",
    ],
    "residence_permit": [
        "permesso di soggiorno",
        "residence permit card",
        "titre de séjour",
    ],
    "passport": ["passport photo", " biometric passport"],
}

DOCUMENT_KEYWORDS = {
    "id_card": ["identity card", "ID card", "CIN", "carte identité", "national ID"],
    "driver_license": [
        "driver license",
        "driving permit",
        "permis conduire",
        "driver's license",
    ],
    "residence_permit": [
        "residence permit",
        "permesso soggiorno",
        "titre séjour",
        "residence card",
    ],
    "passport": ["passport", "passeport", "biometric passport"],
}


class GoogleImagesScraper:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self.downloaded_urls = set()

    def get_image_urls(self, query: str, num_images: int = 50) -> list:
        url = "https://www.google.com/search"
        params = {"q": query, "tbm": "isch", "ijn": str(random.randint(0, 100))}

        urls = []
        for start in range(0, num_images, 20):
            params["start"] = start
            try:
                resp = self.session.get(url, params=params, timeout=10)
                resp.raise_for_status()

                for line in resp.text.split(";"):
                    if line.startswith("AF_initDataCallback"):
                        if '"AGO' in line:
                            try:
                                parsed = json.loads(line[20:-1])
                                if isinstance(parsed, dict):
                                    for item in parsed.get("data", []):
                                        if isinstance(item, list):
                                            for img in item:
                                                if isinstance(
                                                    img, str
                                                ) and img.startswith("http"):
                                                    if any(
                                                        kw in img.lower()
                                                        for kw in [
                                                            "jpg",
                                                            "jpeg",
                                                            "png",
                                                            "webp",
                                                        ]
                                                    ):
                                                        urls.append(img)
                            except:
                                pass
            except Exception as e:
                print(f"Error: {e}")
                continue
            time.sleep(random.uniform(1, 3))

        return list(set(urls))[:num_images]

    def download_image(self, url: str, filename: str) -> bool:
        if url in self.downloaded_urls:
            return False
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 5000:
                ext = os.path.splitext(urlparse(url).path)[1].split("?")[0]
                if not ext in [".jpg", ".jpeg", ".png", ".webp"]:
                    ext = ".jpg"
                filepath = self.output_dir / f"{filename}{ext}"
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                self.downloaded_urls.add(url)
                return True
        except:
            pass
        return False

    def scrape_category(
        self, category: str, queries: list, num_images: int = 50
    ) -> int:
        print(f"\n=== Scraping: {category} ===")
        category_dir = self.output_dir / category
        category_dir.mkdir(exist_ok=True)

        total = 0
        for query in queries:
            print(f"搜索: {query}")
            urls = self.get_image_urls(query, num_images)
            print(f"  Found {len(urls)} URLs")

            for i, url in enumerate(urls):
                if self.download_image(url, f"{category}_{total:03d}"):
                    total += 1
                    if total >= num_images:
                        break
                if total % 10 == 0:
                    print(f"  Downloaded: {total}")
                time.sleep(random.uniform(0.5, 1.5))

            if total >= num_images:
                break

        print(f"  Total: {total} images")
        return total


def scrape_with_duckduckgo():
    from duckduckgo_search import DDGS

    ddgs = DDGS()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_queries = []
    for category, queries in DOCUMENT_QUERIES.items():
        for q in queries:
            all_queries.append((category, q))

    for category, query in all_queries:
        print(f"Searching: {query}")
        try:
            results = ddgs.images(query, max_results=50)
            category_dir = OUTPUT_DIR / category
            category_dir.mkdir(exist_ok=True)

            count = 0
            for r in results:
                if count >= 50:
                    break
                try:
                    resp = requests.get(r["image"], timeout=10)
                    if resp.status_code == 200 and len(resp.content) > 5000:
                        ext = r.get("image", ".jpg").split(".")[-1][:4]
                        if ext not in ["jpg", "jpeg", "png", "webp"]:
                            ext = "jpg"
                        path = category_dir / f"{category}_{count:03d}.{ext}"
                        with open(path, "wb") as f:
                            f.write(resp.content)
                        count += 1
                        print(f"  Saved: {path.name}")
                except Exception as e:
                    print(f"Error: {e}")
            print(f"Category {category}: {count} images")
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")


def main():
    print("Document Image Scraper")
    print("=" * 50)

    scraper = GoogleImagesScraper(OUTPUT_DIR)

    for category, queries in DOCUMENT_QUERIES.items():
        scraper.scrape_category(category, queries, num_images=50)
        time.sleep(2)

    print("\n=== Done ===")
    print(f"Images saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
