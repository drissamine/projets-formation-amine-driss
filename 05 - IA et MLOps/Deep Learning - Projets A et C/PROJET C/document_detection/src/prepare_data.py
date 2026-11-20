import shutil
from pathlib import Path
import random

BASE = Path("dataset")
IMAGES_DIR = BASE / "images"
LABELS_DIR = BASE / "labels"

CLASS_MAP = {"id_card": 0, "driver_license": 1, "residence_permit": 2, "passport": 3}


def create_split():
    for split in ["train", "val"]:
        (IMAGES_DIR / split).mkdir(parents=True, exist_ok=True)
        (LABELS_DIR / split).mkdir(parents=True, exist_ok=True)

    for category in CLASS_MAP.keys():
        cat_images = list((IMAGES_DIR / category).glob("*.jpg"))
        random.shuffle(cat_images)

        split_idx = int(len(cat_images) * 0.8)
        train_imgs = cat_images[:split_idx]
        val_imgs = cat_images[split_idx:]

        for img in train_imgs:
            new_path = IMAGES_DIR / "train" / img.name
            shutil.copy(img, new_path)
            create_label(new_path, CLASS_MAP[category])

        for img in val_imgs:
            new_path = IMAGES_DIR / "val" / img.name
            shutil.copy(img, new_path)
            create_label(new_path, CLASS_MAP[category])

        print(f"{category}: train={len(train_imgs)}, val={len(val_imgs)}")

    print(f"\nTrain: {len(list((IMAGES_DIR / 'train').glob('*.jpg')))}")
    print(f"Val: {len(list((IMAGES_DIR / 'val').glob('*.jpg')))}")


def create_label(image_path: Path, class_id: int):
    img_w, img_h = 480, 640

    x_center = 0.5
    y_center = 0.45
    width = 0.75
    height = 0.65

    label_path = LABELS_DIR / image_path.parent.name / f"{image_path.stem}.txt"
    label_path.write_text(f"{class_id} {x_center} {y_center} {width} {height}\n")


def create_yaml():
    yaml_content = """path: D:/M2/Deep Learning/PROJET C/document_detection/dataset
train: images/train
val: images/val

nc: 4
names:
  0: id_card
  1: driver_license
  2: residence_permit
  3: passport
"""
    (BASE / "data.yaml").write_text(yaml_content)
    print("Created: dataset/data.yaml")


if __name__ == "__main__":
    create_split()
    create_yaml()
    print("\nDataset ready for training!")
