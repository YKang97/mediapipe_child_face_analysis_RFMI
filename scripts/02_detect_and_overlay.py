from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps


RIGHT_EYE = {
    "outer": 33,
    "inner": 133,
    "vertical_pairs": [(159, 145), (158, 153), (160, 144)],
}
LEFT_EYE = {
    "outer": 263,
    "inner": 362,
    "vertical_pairs": [(386, 374), (385, 380), (387, 373)],
}
KEYPOINTS = {
    "face_left": 234,
    "face_right": 454,
    "nose_left": 98,
    "nose_right": 327,
    "mouth_left": 61,
    "mouth_right": 291,
    "jaw_left": 172,
    "jaw_right": 397,
}
POINT_GROUPS = {
    "eye": sorted(
        set(
            [
                RIGHT_EYE["outer"],
                RIGHT_EYE["inner"],
                LEFT_EYE["outer"],
                LEFT_EYE["inner"],
                *[p for pair in RIGHT_EYE["vertical_pairs"] for p in pair],
                *[p for pair in LEFT_EYE["vertical_pairs"] for p in pair],
            ]
        )
    ),
    "face": [KEYPOINTS["face_left"], KEYPOINTS["face_right"]],
    "nose": [KEYPOINTS["nose_left"], KEYPOINTS["nose_right"]],
    "mouth": [KEYPOINTS["mouth_left"], KEYPOINTS["mouth_right"]],
    "jaw": [KEYPOINTS["jaw_left"], KEYPOINTS["jaw_right"]],
}
COLORS = {
    "other": (245, 245, 245),
    "eye": (220, 40, 45),
    "face": (35, 95, 190),
    "nose": (245, 145, 35),
    "mouth": (140, 70, 180),
    "jaw": (20, 145, 135),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MediaPipe Face Landmarker and generate overlays.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root folder.")
    parser.add_argument("--manifest", type=Path, default=None, help="Optional manifest CSV path.")
    parser.add_argument("--model", type=Path, default=None, help="Optional face_landmarker.task path.")
    return parser.parse_args()


def ensure_dirs(root: Path) -> dict[str, Path]:
    paths = {
        "landmarks": root / "outputs_landmarks",
        "full": root / "outputs_overlay" / "full_face",
        "eye": root / "outputs_overlay" / "eye_zoom",
        "lines": root / "outputs_overlay" / "rfmi_lines",
        "logs": root / "logs",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def import_mediapipe():
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    return mp, python, vision


def load_detector(model_path: Path):
    if not model_path.exists():
        raise FileNotFoundError(f"MediaPipe model not found: {model_path}. Run 01_prepare_project.py first.")
    mp, python, vision = import_mediapipe()
    base_options = python.BaseOptions(model_asset_buffer=model_path.read_bytes())
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return mp, vision.FaceLandmarker.create_from_options(options)


def image_records(manifest: pd.DataFrame) -> list[dict]:
    records: list[dict] = []
    for _, row in manifest.iterrows():
        child_id = str(row["child_id"])
        path = str(row.get("open_analysis_path", "")).strip()
        if path:
            records.append(
                {
                    "child_id": child_id,
                    "state": "open",
                    "image_id": f"{child_id}_open",
                    "image_path": path,
                }
            )
    return records


def resolve_project_path(root: Path, path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else root / path


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def pil_to_mp_image(mp, path: Path):
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    arr = np.asarray(img)
    return img, mp.Image(image_format=mp.ImageFormat.SRGB, data=arr)


def coords_from_landmarks(landmarks, width: int, height: int) -> dict[int, tuple[float, float]]:
    return {i: (float(lm.x * width), float(lm.y * height)) for i, lm in enumerate(landmarks)}


def selected_points() -> set[int]:
    return {p for group in POINT_GROUPS.values() for p in group}


def draw_other_points(draw: ImageDraw.ImageDraw, coords: dict[int, tuple[float, float]], scale: float = 1.0) -> None:
    selected = selected_points()
    radius = 1.8 * scale
    for point, (x, y) in coords.items():
        if point in selected:
            continue
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*COLORS["other"], 170), outline=(80, 80, 80, 80))


def draw_key_points(draw: ImageDraw.ImageDraw, coords: dict[int, tuple[float, float]], scale: float = 1.0) -> None:
    for group, points in POINT_GROUPS.items():
        color = COLORS[group]
        radius = (5.0 if group == "eye" else 4.4) * scale
        for point in points:
            if point not in coords:
                continue
            x, y = coords[point]
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 255, 255, 235))
            draw.ellipse(
                (x - radius + 1.8, y - radius + 1.8, x + radius - 1.8, y + radius - 1.8),
                fill=(*color, 250),
                outline=(35, 35, 35, 180),
                width=1,
            )


def draw_line(draw: ImageDraw.ImageDraw, coords: dict[int, tuple[float, float]], a: int, b: int, fill, width: int) -> None:
    if a in coords and b in coords:
        draw.line([coords[a], coords[b]], fill=fill, width=width)


def draw_rfmi_lines(draw: ImageDraw.ImageDraw, coords: dict[int, tuple[float, float]], scale: float = 1.0) -> None:
    draw_line(draw, coords, KEYPOINTS["face_left"], KEYPOINTS["face_right"], COLORS["face"], max(3, int(5 * scale)))
    draw_line(draw, coords, KEYPOINTS["nose_left"], KEYPOINTS["nose_right"], COLORS["nose"], max(3, int(4 * scale)))
    draw_line(draw, coords, KEYPOINTS["mouth_left"], KEYPOINTS["mouth_right"], COLORS["mouth"], max(3, int(4 * scale)))
    draw_line(draw, coords, KEYPOINTS["jaw_left"], KEYPOINTS["jaw_right"], COLORS["jaw"], max(3, int(4 * scale)))
    draw_line(draw, coords, RIGHT_EYE["outer"], RIGHT_EYE["inner"], COLORS["eye"], max(3, int(4 * scale)))
    draw_line(draw, coords, LEFT_EYE["outer"], LEFT_EYE["inner"], COLORS["eye"], max(3, int(4 * scale)))
    for a, b in RIGHT_EYE["vertical_pairs"] + LEFT_EYE["vertical_pairs"]:
        draw_line(draw, coords, a, b, COLORS["eye"], max(2, int(3 * scale)))


def draw_overlay(img: Image.Image, coords: dict[int, tuple[float, float]], out_path: Path, with_lines: bool = False) -> None:
    canvas = img.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw_other_points(draw, coords)
    if with_lines:
        draw_rfmi_lines(draw, coords)
    draw_key_points(draw, coords)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=95)


def draw_eye_zoom(img: Image.Image, coords: dict[int, tuple[float, float]], out_path: Path) -> None:
    eye_points = sorted(set(POINT_GROUPS["eye"]))
    pts = [coords[p] for p in eye_points if p in coords]
    if not pts:
        return
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    margin = max(40, int(0.08 * max(img.size)))
    left = max(0, int(min(xs) - margin))
    right = min(img.width, int(max(xs) + margin))
    top = max(0, int(min(ys) - margin))
    bottom = min(img.height, int(max(ys) + margin))
    crop = img.crop((left, top, right, bottom)).resize((max(1, (right - left) * 2), max(1, (bottom - top) * 2)))
    draw = ImageDraw.Draw(crop, "RGBA")

    for point, (x0, y0) in coords.items():
        x = (x0 - left) * 2
        y = (y0 - top) * 2
        if 0 <= x <= crop.width and 0 <= y <= crop.height and point not in POINT_GROUPS["eye"]:
            radius = 2.8
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*COLORS["other"], 160))

    for point in eye_points:
        if point not in coords:
            continue
        x = (coords[point][0] - left) * 2
        y = (coords[point][1] - top) * 2
        radius = 5.8
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 255, 255, 230))
        draw.ellipse((x - radius + 1.5, y - radius + 1.5, x + radius - 1.5, y + radius - 1.5), fill=(*COLORS["eye"], 250))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    crop.save(out_path, quality=95)


def landmark_rows(image_id: str, child_id: str, state: str, landmarks, width: int, height: int) -> list[dict]:
    rows = []
    for i, lm in enumerate(landmarks):
        rows.append(
            {
                "image_id": image_id,
                "child_id": child_id,
                "state": state,
                "landmark_index": i,
                "x_norm": lm.x,
                "y_norm": lm.y,
                "z_norm": lm.z,
                "x_px": lm.x * width,
                "y_px": lm.y * height,
            }
        )
    return rows


def blendshape_row(image_id: str, child_id: str, state: str, result) -> dict:
    row = {"image_id": image_id, "child_id": child_id, "state": state}
    if result.face_blendshapes:
        for category in result.face_blendshapes[0]:
            row[category.category_name] = category.score
    return row


def main() -> None:
    args = parse_args()
    root = args.root.expanduser().resolve()
    paths = ensure_dirs(root)
    manifest_path = args.manifest or (root / "outputs_manifest" / "manifest.csv")
    model_path = args.model or (root / "models" / "face_landmarker.task")

    manifest = pd.read_csv(manifest_path, dtype={"child_id": str})
    records = image_records(manifest)
    mp, detector = load_detector(model_path)

    all_landmarks: list[dict] = []
    blendshape_rows: list[dict] = []
    detection_rows: list[dict] = []

    for rec in records:
        image_path = resolve_project_path(root, rec["image_path"])
        image_id = rec["image_id"]
        print(f"Processing {image_id}: {image_path}")
        try:
            img, mp_image = pil_to_mp_image(mp, image_path)
            result = detector.detect(mp_image)
            n_faces = len(result.face_landmarks)
            success = n_faces >= 1
            width, height = img.size
            full_path = paths["full"] / f"{image_id}_overlay.jpg"
            eye_path = paths["eye"] / f"{image_id}_eye_zoom.jpg"
            line_path = paths["lines"] / f"{image_id}_rfmi_lines.jpg"
            detection_rows.append(
                {
                    **rec,
                    "width": width,
                    "height": height,
                    "n_faces": n_faces,
                    "detection_success": success,
                    "error": "",
                    "full_overlay_path": rel(root, full_path),
                    "eye_zoom_path": rel(root, eye_path),
                    "rfmi_line_overlay_path": rel(root, line_path),
                }
            )
            if not success:
                continue
            landmarks = result.face_landmarks[0]
            coords = coords_from_landmarks(landmarks, width, height)
            all_landmarks.extend(landmark_rows(image_id, rec["child_id"], rec["state"], landmarks, width, height))
            blendshape_rows.append(blendshape_row(image_id, rec["child_id"], rec["state"], result))
            draw_overlay(img, coords, full_path, with_lines=False)
            draw_overlay(img, coords, line_path, with_lines=True)
            draw_eye_zoom(img, coords, eye_path)
        except Exception as exc:
            detection_rows.append(
                {
                    **rec,
                    "width": "",
                    "height": "",
                    "n_faces": 0,
                    "detection_success": False,
                    "error": str(exc),
                    "full_overlay_path": "",
                    "eye_zoom_path": "",
                    "rfmi_line_overlay_path": "",
                }
            )

    detector.close()

    pd.DataFrame(all_landmarks).to_csv(paths["landmarks"] / "landmarks_raw.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(blendshape_rows).to_csv(paths["landmarks"] / "blendshapes_raw.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(detection_rows).to_csv(paths["landmarks"] / "detection_log.csv", index=False, encoding="utf-8-sig")

    with (paths["logs"] / "02_detect_and_overlay_summary.txt").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n_images", len(records)])
        writer.writerow(["n_detection_success", sum(bool(r["detection_success"]) for r in detection_rows)])
        writer.writerow(["n_landmark_rows", len(all_landmarks)])
        writer.writerow(["n_blendshape_rows", len(blendshape_rows)])

    print("Detection and overlay generation complete.")
    print(f"Landmarks: {paths['landmarks'] / 'landmarks_raw.csv'}")
    print(f"Full overlays: {paths['full']}")
    print(f"Eye zooms: {paths['eye']}")
    print(f"RFMI line overlays: {paths['lines']}")


if __name__ == "__main__":
    main()
