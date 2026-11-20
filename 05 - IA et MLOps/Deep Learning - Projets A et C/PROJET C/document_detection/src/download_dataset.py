import os
import zipfile
import shutil
from pathlib import Path
import urllib.request
import gdown

OUTPUT_DIR = Path("dataset/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PUBLIC_DATASETS = {
    "id_card": [
        "https://www.kaggle.com/api/v1/datasets/view",
    ],
}


def download_from_gdrive(file_id: str, output_path: Path) -> bool:
    try:
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, str(output_path), quiet=False)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def create_sample_dataset():
    print("Creating sample dataset structure...")

    categories = ["id_card", "driver_license", "residence_permit", "passport"]

    for cat in categories:
        cat_dir = OUTPUT_DIR / cat
        cat_dir.mkdir(exist_ok=True)

    print(f"\nFolders created: {OUTPUT_DIR}")
    print("\nCategories:")
    for cat in categories:
        print(f"  - {cat}")

    print("\n" + "=" * 50)
    print("MANUAL DOWNLOAD REQUIRED")
    print("=" * 50)
    print("""
Options:
1. Roboflow: https://roboflow.com
   - Search "ID card", "driver license", "passport"
   - Export YOLO format

2. Kaggle datasets:
   - https://www.kaggle.com/datasets (search document/ID)
   
3. Open Images:
   - https://storage.googleapis.com/openimages/web/index.html

4. Manual photos:
   - Take photos of your own documents
   - Save to corresponding folders

After adding images:
  - Split: 80% train / 20% val
  - Annotate with LabelImg
  - Run: python src/train.py
""")


if __name__ == "__main__":
    create_sample_dataset()
