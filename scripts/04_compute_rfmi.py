from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute open-eye RFMI indices from MediaPipe landmarks.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root folder.")
    return parser.parse_args()


def dist(coords: dict[int, tuple[float, float]], a: int, b: int) -> float:
    ax, ay = coords[a]
    bx, by = coords[b]
    return float(np.hypot(ax - bx, ay - by))


def eye_aperture(coords: dict[int, tuple[float, float]], spec: dict) -> float:
    width = dist(coords, spec["outer"], spec["inner"])
    vertical = np.mean([dist(coords, a, b) for a, b in spec["vertical_pairs"]])
    return float(vertical / width) if width else np.nan


def load_coords(root: Path) -> dict[str, dict[int, tuple[float, float]]]:
    landmarks_path = root / "outputs_landmarks" / "landmarks_raw.csv"
    if not landmarks_path.exists():
        raise FileNotFoundError(f"Landmark file not found: {landmarks_path}. Run 02_detect_and_overlay.py first.")
    lm = pd.read_csv(landmarks_path, dtype={"child_id": str})
    coords: dict[str, dict[int, tuple[float, float]]] = {}
    for image_id, grp in lm.groupby("image_id"):
        coords[str(image_id)] = {
            int(row.landmark_index): (float(row.x_px), float(row.y_px))
            for row in grp.itertuples(index=False)
        }
    return coords


def included_image_ids(root: Path) -> tuple[set[str], str]:
    det = pd.read_csv(root / "outputs_landmarks" / "detection_log.csv", dtype={"child_id": str})
    ids = set(det.loc[det["detection_success"].astype(bool), "image_id"].astype(str))
    return ids, "detection_success"


def compute_image_features(root: Path) -> pd.DataFrame:
    coords_by_image = load_coords(root)
    det = pd.read_csv(root / "outputs_landmarks" / "detection_log.csv", dtype={"child_id": str})
    det = det.loc[det["state"].astype(str).eq("open")].copy()
    blend_path = root / "outputs_landmarks" / "blendshapes_raw.csv"
    blend = pd.read_csv(blend_path, dtype={"child_id": str}) if blend_path.exists() else pd.DataFrame()
    include_ids, include_source = included_image_ids(root)

    rows: list[dict] = []
    for rec in det.itertuples(index=False):
        image_id = str(rec.image_id)
        if image_id not in include_ids or image_id not in coords_by_image:
            continue
        coords = coords_by_image[image_id]
        try:
            face_width = dist(coords, KEYPOINTS["face_left"], KEYPOINTS["face_right"])
            right_eai = eye_aperture(coords, RIGHT_EYE)
            left_eai = eye_aperture(coords, LEFT_EYE)
            rows.append(
                {
                    "image_id": image_id,
                    "child_id": str(rec.child_id),
                    "state": "open",
                    "include_source": include_source,
                    "face_width_px": face_width,
                    "right_eye_aperture_index": right_eai,
                    "left_eye_aperture_index": left_eai,
                    "mean_eye_aperture_index": np.nanmean([right_eai, left_eai]),
                    "eye_aperture_asymmetry_index": abs(right_eai - left_eai),
                    "nose_width_face_width_index": dist(coords, KEYPOINTS["nose_left"], KEYPOINTS["nose_right"]) / face_width if face_width else np.nan,
                    "mouth_width_face_width_index": dist(coords, KEYPOINTS["mouth_left"], KEYPOINTS["mouth_right"]) / face_width if face_width else np.nan,
                    "jaw_width_face_width_index": dist(coords, KEYPOINTS["jaw_left"], KEYPOINTS["jaw_right"]) / face_width if face_width else np.nan,
                }
            )
        except KeyError as exc:
            rows.append({"image_id": image_id, "child_id": str(rec.child_id), "state": "open", "error": f"missing landmark {exc}"})

    features = pd.DataFrame(rows)
    if not blend.empty and not features.empty:
        keep_blend = [
            c
            for c in [
                "image_id",
                "eyeBlinkLeft",
                "eyeBlinkRight",
                "eyeWideLeft",
                "eyeWideRight",
                "eyeSquintLeft",
                "eyeSquintRight",
            ]
            if c in blend.columns
        ]
        features = features.merge(blend[keep_blend], on="image_id", how="left")
    return features


def main() -> None:
    args = parse_args()
    root = args.root.expanduser().resolve()
    feature_dir = root / "outputs_features"
    feature_dir.mkdir(parents=True, exist_ok=True)

    image_features = compute_image_features(root)
    child_features = image_features.sort_values(["child_id", "image_id"]).drop_duplicates("child_id").reset_index(drop=True)

    image_features.to_csv(feature_dir / "rfmi_image_level.csv", index=False, encoding="utf-8-sig")
    child_features.to_csv(feature_dir / "rfmi_subject_level.csv", index=False, encoding="utf-8-sig")
    child_features.to_csv(feature_dir / "rfmi_child_level.csv", index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(feature_dir / "rfmi_workbook.xlsx", engine="openpyxl") as writer:
        image_features.to_excel(writer, sheet_name="ImageLevel_OpenOnly", index=False)
        child_features.to_excel(writer, sheet_name="SubjectLevel_OpenOnly", index=False)
        eye_cols = [c for c in image_features.columns if "eye" in c or "Blink" in c or c in ["image_id", "child_id", "state", "include_source"]]
        face_cols = [c for c in image_features.columns if c.endswith("_index") or c in ["image_id", "child_id", "state", "include_source"]]
        image_features[eye_cols].to_excel(writer, sheet_name="EyeIndices", index=False)
        image_features[face_cols].to_excel(writer, sheet_name="FaceRatioIndices", index=False)

    print(f"Image-level RFMI: {feature_dir / 'rfmi_image_level.csv'}")
    print(f"Subject-level RFMI: {feature_dir / 'rfmi_subject_level.csv'}")
    print(f"n open-eye rows: {len(image_features)}, n subject rows: {len(child_features)}")


if __name__ == "__main__":
    main()
