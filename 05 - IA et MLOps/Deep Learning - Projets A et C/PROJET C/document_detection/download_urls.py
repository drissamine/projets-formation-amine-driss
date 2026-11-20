import requests
import shutil
from pathlib import Path
from urllib.parse import urlparse
import ssl
import concurrent.futures

OUTPUT_DIR = Path("dataset/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_URLS = {
    "id_card": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Generic_Italian_ID_card_front.jpg/800px-Generic_Italian_ID_card_front.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/European_National_ID_Card_%28Italy%29_-_specimen.jpg/800px-European_National_ID_Card_%28Italy%29_-_specimen.jpg",
    ],
    "driver_license": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Driving_Licence_-_UK_specimen.jpg/800px-Driving_Licence_-_UK_specimen.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Driving_licence_France_front.jpg/800px-Driving_licence_France_front.jpg",
    ],
    "residence_permit": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Permesso_di_soggiorno_2014.jpg/800px-Permesso_di_soggiorno_2014.jpg",
    ],
    "passport": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Sample_Biometric_Passport.jpg/800px-Sample_Biometric_Passport.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/European_union_passport.JPG/800px-European_union_passport.JPG",
    ]
}

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def download_image(url: str, filepath: Path) -> bool:
    try:
        resp = session.get(url, timeout=15, verify=False)
        if resp.status_code == 200 and len(resp.content) > 5000:
            filepath.write_bytes(resp.content)
            return True
    except Exception as e:
        print(f"Error: {url[:50]} - {e}")
    return False

def main():
    ssl._create_default_https_context = ssl._create_unverified_https_context
    
    total = 0
    for category, urls in IMAGE_URLS.items():
        cat_dir = OUTPUT_DIR / category
        cat_dir.mkdir(exist_ok=True)
        
        count = 0
        for url in urls:
            ext = Path(urlparse(url).suffix.split('?')[0] or '.jpg'
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']: ext = '.jpg'
            path = cat_dir / f"{category}_{count:03d}{ext}"
            
            if download_image(url, path):
                count += 1
                print(f"✓ {path.name}")
            total += 1
        
        print(f"{category}: {count} images")
    
    print(f"\nTotal: {total} images")

if __name__ == "__main__":
    main()