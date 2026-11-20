import requests
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import io

OUTPUT_DIR = Path("dataset/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_synthetic_documents():
    """Create synthetic document images for testing"""

    categories = {
        "id_card": {"color": (240, 240, 245), "text": "CARTE D'IDENTITE"},
        "driver_license": {"color": (245, 240, 235), "text": "PERMIS DE CONDUIRE"},
        "residence_permit": {"color": (235, 245, 240), "text": "TITRE DE SEJOUR"},
        "passport": {"color": (235, 235, 245), "text": "PASSEPORT"},
    }

    for cat, config in categories.items():
        cat_dir = OUTPUT_DIR / cat
        cat_dir.mkdir(exist_ok=True)

        for i in range(5):
            img = np.full((640, 480, 3), config["color"], dtype=np.uint8)

            cv2.rectangle(img, (40, 40), (440, 600), (200, 200, 200), 2)
            cv2.rectangle(img, (60, 60), (420, 580), (180, 180, 180), 1)

            (text_w, text_h), _ = cv2.getTextSize(
                config["text"], cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3
            )
            cv2.putText(
                img,
                config["text"],
                (240 - text_w // 2, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (50, 50, 50),
                3,
            )

            cv2.putText(
                img,
                f"ID: {i:04d}",
                (80, 250),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (80, 80, 80),
                2,
            )

            cv2.circle(img, (380, 120), 50, (150, 150, 150), -1)
            cv2.circle(img, (380, 120), 50, (50, 50, 50), 2)

            img_pil = Image.fromarray(img)
            path = cat_dir / f"{cat}_{i:03d}.jpg"
            img_pil.save(path, quality=95)
            print(f"Created: {path.name}")

    print(f"\nCreated 20 synthetic images for testing")


def download_sample():
    """Download real sample images from public sources"""

    urls = [
        (
            "id_card",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Generic_Italian_ID_card_front.jpg/480px-Generic_Italian_ID_card_front.jpg",
        ),
        (
            "id_card",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/European_National_ID_Card_%28Italy%29_-_specimen.jpg/480px-European_National_ID_Card_%28Italy%29_-_specimen.jpg",
        ),
        (
            "driver_license",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Driving_Licence_-_UK_specimen.jpg/480px-Driving_Licence_-_UK_specimen.jpg",
        ),
        (
            "driver_license",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Driving_licence_France_front.jpg/480px-Driving_licence_France_front.jpg",
        ),
        (
            "residence_permit",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Permesso_di_soggiorno_2014.jpg/480px-Permesso_di_soggiorno_2014.jpg",
        ),
        (
            "passport",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Sample_Biometric_Passport.jpg/480px-Sample_Biometric_Passport.jpg",
        ),
    ]

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0)"})

    for cat, url in urls:
        cat_dir = OUTPUT_DIR / cat
        cat_dir.mkdir(exist_ok=True)

        try:
            resp = session.get(url, timeout=10)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content))
                path = cat_dir / f"{cat}_{url[-8:]}.jpg"
                if not path.suffix:
                    path = path.with_suffix(".jpg")
                img.save(path, quality=90)
                print(f"Downloaded: {path.name}")
        except Exception as e:
            print(f"Failed: {url[:50]}...")


if __name__ == "__main__":
    print("Downloading sample images from Wikipedia...")
    download_sample()

    print("\nCreating synthetic samples...")
    create_synthetic_documents()

    print("\n" + "=" * 50)
    print("Next steps:")
    print("1. Take photos of your own documents")
    print("2. Annotate with LabelImg or Roboflow")
    print("3. Run: python src/train.py")
