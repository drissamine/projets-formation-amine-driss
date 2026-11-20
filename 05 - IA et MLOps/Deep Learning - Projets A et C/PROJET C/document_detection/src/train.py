from ultralytics import YOLO
import yaml
from pathlib import Path

PROJECT = "document_detector"
DATA_CONFIG = """path: dataset
train: images/train
val: images/val

nc: 4
names:
  0: id_card
  1: driver_license
  2: residence_permit
  3: passport
"""


def create_dataset_structure():
    base = Path("dataset")
    for split in ["train", "val"]:
        (base / "images" / split).mkdir(parents=True, exist_ok=True)
        (base / "labels" / split).mkdir(parents=True, exist_ok=True)

    config = base / "data.yaml"
    config.write_text(DATA_CONFIG)
    print(f"Created: {config}")
    return config


def train(model_name: str = "yolov8n", epochs: int = 100, imgsz: int = 640):
    config_path = create_dataset_structure()

    model = YOLO(f"{model_name}.pt")

    results = model.train(
        data=str(config_path),
        epochs=epochs,
        imgsz=imgsz,
        patience=20,
        batch=4,
        device="cpu",
        workers=2,
        project=PROJECT,
        name="exp",
        exist_ok=True,
        rect=False,
        mosaic=0.5,
        mixup=0.1,
        copy_paste=0.05,
        amp=False,
        plots=True,
        verbose=True,
    )

    best_model = Path(PROJECT) / "exp" / "weights" / "best.pt"
    if best_model.exists():
        final_path = Path("models") / "document_detector.pt"
        final_path.parent.mkdir(exist_ok=True)
        best_model.rename(final_path)
        print(f"Model saved: {final_path}")

    return results


def export_onnx():
    model_path = Path("models/document_detector.pt")
    if not model_path.exists():
        print("Model not found!")
        return

    model = YOLO(str(model_path))
    model.export(format="onnx", imgsz=640, dynamic=False)
    print(f"Exported ONNX: {model_path.with_suffix('.onnx')}")


def validate():
    model_path = Path("models/document_detector.pt")
    if not model_path.exists():
        print("Model not found!")
        return

    model = YOLO(str(model_path))
    metrics = model.val(data="dataset/data.yaml")
    print(f"mAP50: {metrics.box.map50}")
    print(f"mAP50-95: {metrics.box.map}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", default="yolov8n", help="Model (yolov8n, yolov8s, yolov8m)"
    )
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--export", action="store_true", help="Export ONNX")
    parser.add_argument("--validate", action="store_true", help="Validate")
    args = parser.parse_args()

    if args.export:
        export_onnx()
    elif args.validate:
        validate()
    else:
        train(args.model, args.epochs)
