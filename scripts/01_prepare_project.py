from __future__ import annotations

import argparse
import hashlib
import shutil
import urllib.request
from pathlib import Path

import pandas as pd
from PIL import Image, ImageOps


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)
MODEL_SHA256 = "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare folders, one open-eye image, manifest, and MediaPipe model.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root folder.")
    parser.add_argument("--open-image", type=Path, default=None, help="Open-eye frontal image path.")
    parser.add_argument("--child-id", default="SYN", help="Image identifier, e.g. SYN or C01.")
    parser.add_argument("--model-source", type=Path, default=None, help="Optional local face_landmarker.task to copy.")
    parser.add_argument("--skip-model", action="store_true", help="Skip model copy/download.")
    parser.add_argument("--force-model", action="store_true", help="Overwrite existing model file.")
    return parser.parse_args()


def normalize_root(root: Path) -> Path:
    return root.expanduser().resolve()


def ensure_dirs(root: Path) -> dict[str, Path]:
    paths = {
        "data": root / "data" / "images_analysis",
        "manifest": root / "outputs_manifest",
        "models": root / "models",
        "logs": root / "logs",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def default_example_image(root: Path) -> Path:
    return root / "example_data" / "images" / "SYN_open.jpg"


def save_rgb_image(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    img.save(dst, quality=95)


def prepare_image(root: Path, args: argparse.Namespace) -> Path:
    data_dir = root / "data" / "images_analysis"
    image_dst = data_dir / f"{args.child_id}_open.jpg"
    image_src = args.open_image or default_example_image(root)
    if not image_src.exists():
        raise FileNotFoundError(f"Open-eye image not found: {image_src}")
    save_rgb_image(image_src, image_dst)
    return image_dst


def ensure_model(root: Path, model_source: Path | None, skip_model: bool, force: bool) -> Path:
    model_path = root / "models" / "face_landmarker.task"
    if skip_model:
        return model_path
    if model_path.exists() and model_path.stat().st_size > 1_000_000 and not force:
        verify_model_hash(model_path)
        return model_path
    model_path.parent.mkdir(parents=True, exist_ok=True)

    if model_source is not None:
        if not model_source.exists():
            raise FileNotFoundError(f"Model source not found: {model_source}")
        shutil.copy2(model_source, model_path)
        verify_model_hash(model_path)
        return model_path

    print(f"Downloading MediaPipe Face Landmarker model to {model_path}")
    urllib.request.urlretrieve(MODEL_URL, model_path)
    verify_model_hash(model_path)
    return model_path


def verify_model_hash(model_path: Path) -> None:
    actual = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if actual.lower() != MODEL_SHA256:
        raise ValueError(
            "face_landmarker.task does not match the expected SHA256 hash. "
            f"Expected {MODEL_SHA256}, got {actual}."
        )


def write_manifest(root: Path, child_id: str, open_path: Path) -> Path:
    out_dir = root / "outputs_manifest"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = pd.DataFrame(
        [
            {
                "child_id": child_id,
                "state": "open",
                "open_analysis_path": str(open_path.relative_to(root)),
                "has_open": open_path.exists(),
            }
        ]
    )
    manifest_path = out_dir / "manifest.csv"
    manifest.to_csv(manifest_path, index=False, encoding="utf-8-sig")
    summary = pd.DataFrame(
        [
            {
                "n_images": len(manifest),
                "n_open_images": int(manifest["has_open"].sum()),
                "n_missing_open": int((~manifest["has_open"]).sum()),
            }
        ]
    )
    summary.to_csv(out_dir / "manifest_summary.csv", index=False, encoding="utf-8-sig")
    return manifest_path


def main() -> None:
    args = parse_args()
    root = normalize_root(args.root)
    ensure_dirs(root)
    open_path = prepare_image(root, args)
    manifest_path = write_manifest(root, args.child_id, open_path)
    model_path = ensure_model(root, args.model_source, args.skip_model, args.force_model)

    print("Project prepared.")
    print(f"Root: {root}")
    print(f"Manifest: {manifest_path}")
    print(f"Open image: {open_path}")
    print(f"Model path: {model_path}")


if __name__ == "__main__":
    main()
