from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


RFMI_METRICS = [
    ("eye_33_133_aperture_index", "33-133 eye-region aperture index", "Eye geometry"),
    ("eye_263_362_aperture_index", "263-362 eye-region aperture index", "Eye geometry"),
    ("mean_eye_aperture_index", "Mean eye aperture index", "Eye geometry"),
    ("eye_aperture_asymmetry_index", "Eye aperture asymmetry index", "Eye geometry"),
    ("nose_width_face_width_index", "Nose-width/face-width index", "Face ratio"),
    ("mouth_width_face_width_index", "Mouth-width/face-width index", "Face ratio"),
    ("jaw_width_face_width_index", "Jaw-width/face-width index", "Face ratio"),
    ("eyeBlinkLeft", "Eye blink auxiliary score: MediaPipe Left", "Eye-state auxiliary score"),
    ("eyeBlinkRight", "Eye blink auxiliary score: MediaPipe Right", "Eye-state auxiliary score"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create RFMI subject-level and summary tables.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root folder.")
    return parser.parse_args()


def summarize_metric(series: pd.Series) -> dict:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return {"n": 0, "mean": "", "sd": "", "median": "", "min": "", "max": "", "mean_sd": ""}
    mean = values.mean()
    sd = values.std(ddof=1) if len(values) > 1 else 0.0
    return {
        "n": int(values.count()),
        "mean": mean,
        "sd": sd,
        "median": values.median(),
        "min": values.min(),
        "max": values.max(),
        "mean_sd": f"{mean:.3f} +/- {sd:.3f}",
    }


def main() -> None:
    args = parse_args()
    root = args.root.expanduser().resolve()
    feature_dir = root / "outputs_features"
    table_dir = root / "outputs_stats" / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)

    image_path = feature_dir / "rfmi_image_level.csv"
    if not image_path.exists():
        raise FileNotFoundError(f"RFMI table not found: {image_path}. Run 04_compute_rfmi.py first.")

    image = pd.read_csv(image_path, dtype={"child_id": str})
    subject = image.sort_values(["child_id", "image_id"]).drop_duplicates("child_id").reset_index(drop=True)
    subject = subject.rename(columns={"child_id": "subject_id"})

    metric_rows = []
    for metric, label, category in RFMI_METRICS:
        if metric not in image.columns:
            continue
        row = {"metric": metric, "label": label, "category": category}
        row.update(summarize_metric(image[metric]))
        metric_rows.append(row)
    summary = pd.DataFrame(metric_rows)

    subject_out = table_dir / "rfmi_subject_indices.csv"
    summary_out = table_dir / "rfmi_summary.csv"
    workbook_out = table_dir / "rfmi_public_demo_tables.xlsx"

    subject.to_csv(subject_out, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_out, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(workbook_out, engine="openpyxl") as writer:
        subject.to_excel(writer, sheet_name="Subject_RFMI", index=False)
        summary.to_excel(writer, sheet_name="RFMI_Summary", index=False)

    print(f"Subject-level RFMI table: {subject_out}")
    print(f"RFMI summary table: {summary_out}")
    print(f"Workbook: {workbook_out}")


if __name__ == "__main__":
    main()
