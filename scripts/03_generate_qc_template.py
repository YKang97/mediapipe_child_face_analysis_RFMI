from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


QC_DIMENSIONS = [
    {
        "field": "overall_score",
        "dimension": "Overall face",
        "score_0": "Not usable: major landmark displacement or unusable image.",
        "score_1": "Borderline: face detected but local mismatch requires review.",
        "score_2": "Usable: main landmarks align with the visible face region.",
    },
    {
        "field": "eye_region_score",
        "dimension": "Eye region",
        "score_0": "Not usable: eye landmarks clearly miss the visible eye region.",
        "score_1": "Borderline: mild local mismatch or partial ambiguity.",
        "score_2": "Usable: eye landmarks are consistent with the visible eye region.",
    },
    {
        "field": "nose_mouth_score",
        "dimension": "Nose-mouth region",
        "score_0": "Not usable: nose or mouth landmarks clearly miss the visible region.",
        "score_1": "Borderline: mild local mismatch or partial ambiguity.",
        "score_2": "Usable: nose and mouth landmarks are consistent with the visible region.",
    },
    {
        "field": "facial_outline_score",
        "dimension": "Facial outline",
        "score_0": "Not usable: facial outline landmarks are clearly displaced.",
        "score_1": "Borderline: mild outline mismatch or partial occlusion.",
        "score_2": "Usable: facial outline landmarks are consistent with the visible face boundary.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a blinded manual quality-control template for RFMI overlays.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root folder.")
    return parser.parse_args()


def relative_or_blank(root: Path, path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main() -> None:
    args = parse_args()
    root = args.root.expanduser().resolve()
    log_path = root / "outputs_landmarks" / "detection_log.csv"
    if not log_path.exists():
        raise FileNotFoundError(f"Detection log not found: {log_path}. Run 02_detect_and_overlay.py first.")

    qc_dir = root / "outputs_qc"
    qc_dir.mkdir(parents=True, exist_ok=True)

    detection = pd.read_csv(log_path, dtype={"child_id": str})
    rows: list[dict] = []
    for rec in detection.itertuples(index=False):
        image_id = str(rec.image_id)
        child_id = str(rec.child_id)
        detection_success = bool(rec.detection_success)
        rows.append(
            {
                "image_id": image_id,
                "subject_id": child_id,
                "state": str(rec.state),
                "detection_success": detection_success,
                "full_face_overlay": relative_or_blank(root, root / "outputs_overlay" / "full_face" / f"{image_id}_overlay.jpg"),
                "eye_zoom_overlay": relative_or_blank(root, root / "outputs_overlay" / "eye_zoom" / f"{image_id}_eye_zoom.jpg"),
                "rfmi_lines_overlay": relative_or_blank(root, root / "outputs_overlay" / "rfmi_lines" / f"{image_id}_rfmi_lines.jpg"),
                "rater_id": "",
                "overall_score": "",
                "eye_region_score": "",
                "nose_mouth_score": "",
                "facial_outline_score": "",
                "include_main_analysis": "",
                "comments": "",
            }
        )

    template = pd.DataFrame(rows)
    template_path = qc_dir / "qc_template.csv"
    template.to_csv(template_path, index=False, encoding="utf-8-sig")

    codebook = pd.DataFrame(QC_DIMENSIONS)
    codebook_path = qc_dir / "qc_score_codebook.csv"
    codebook.to_csv(codebook_path, index=False, encoding="utf-8-sig")

    print(f"QC template: {template_path}")
    print(f"QC score codebook: {codebook_path}")
    print("Scores are intentionally blank in the public template; real study ratings should not be shared with identifiable child data.")


if __name__ == "__main__":
    main()
