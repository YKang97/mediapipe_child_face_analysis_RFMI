from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "AI_IMAGE_DISCLOSURE.md",
    "requirements.txt",
    "docs/README.md",
    "docs/methods_rfmi.md",
    "docs/reproducibility.md",
    "docs/figures/rfmi_six_part_overview.png",
    "docs/figures/demo_synthetic_input.jpg",
    "docs/figures/demo_full_face_overlay.jpg",
    "docs/figures/demo_eye_zoom_overlay.jpg",
    "docs/figures/demo_rfmi_lines_overlay.jpg",
    "docs/figures/demo_rfmi_subject_table.png",
    "docs/figures/demo_rfmi_summary_table.png",
    "docs/tables/demo_qc_template.csv",
    "docs/tables/demo_qc_score_codebook.csv",
    "docs/tables/demo_rfmi_subject_indices.csv",
    "docs/tables/demo_rfmi_summary.csv",
    "example_data/images/SYN_open.jpg",
    "notebooks/BIBE_RFMI_Image_to_Indices_Demo.ipynb",
    "scripts/01_prepare_project.py",
    "scripts/02_detect_and_overlay.py",
    "scripts/03_generate_qc_template.py",
    "scripts/04_compute_rfmi.py",
    "scripts/05_summarize_rfmi.py",
    "scripts/06_validate_public_demo.py",
]

REQUIRED_SUBJECT_COLUMNS = {
    "image_id",
    "subject_id",
    "state",
    "include_source",
    "face_width_px",
    "eye_33_133_aperture_index",
    "eye_263_362_aperture_index",
    "mean_eye_aperture_index",
    "eye_aperture_asymmetry_index",
    "nose_width_face_width_index",
    "mouth_width_face_width_index",
    "jaw_width_face_width_index",
    "eyeBlinkLeft",
    "eyeBlinkRight",
}

REQUIRED_SUMMARY_COLUMNS = {
    "metric",
    "label",
    "category",
    "n",
    "mean",
    "sd",
    "median",
    "min",
    "max",
    "mean_sd",
}

REQUIRED_QC_COLUMNS = {
    "image_id",
    "subject_id",
    "state",
    "detection_success",
    "full_face_overlay",
    "eye_zoom_overlay",
    "rfmi_lines_overlay",
    "rater_id",
    "overall_score",
    "eye_region_score",
    "nose_mouth_score",
    "facial_outline_score",
    "include_main_analysis",
    "comments",
}

REQUIRED_README_PHRASES = [
    "synthetic",
    "No real child participant photographs",
    "not centimeter measurements",
    "not official MediaPipe medical measurements",
    "ethics approval",
    "blinded manual quality-control template",
]


class ValidationError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate public demo files and reviewer-facing documentation.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root folder.")
    return parser.parse_args()


def require_file(root: Path, relative_path: str) -> Path:
    path = root / relative_path
    if not path.exists():
        raise ValidationError(f"Required file is missing: {relative_path}")
    if path.is_file() and path.stat().st_size == 0:
        raise ValidationError(f"Required file is empty: {relative_path}")
    return path


def read_csv_header(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
    if not header:
        raise ValidationError(f"CSV has no header: {path}")
    return set(header)


def validate_required_files(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        require_file(root, relative_path)


def validate_readme_language(root: Path) -> None:
    readme = (root / "README.md").read_text(encoding="utf-8")
    missing = [phrase for phrase in REQUIRED_README_PHRASES if phrase not in readme]
    if missing:
        raise ValidationError(f"README.md is missing required cautionary language: {missing}")


def validate_notebook(root: Path) -> None:
    notebook_path = root / "notebooks" / "BIBE_RFMI_Image_to_Indices_Demo.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    if notebook.get("nbformat") != 4:
        raise ValidationError("Notebook nbformat is not 4.")
    text = "\n".join("".join(cell.get("source", [])) for cell in notebook.get("cells", []))
    required_phrases = [
        "RFMI extraction framework",
        "Coordinate-Based Overlay Figures and QC Template",
        "03_generate_qc_template.py",
        "eye_33_133_aperture_index",
        "eye_263_362_aperture_index",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in text]
    if missing:
        raise ValidationError(f"Notebook is missing required public-workflow text: {missing}")


def validate_static_tables(root: Path) -> None:
    subject_header = read_csv_header(root / "docs" / "tables" / "demo_rfmi_subject_indices.csv")
    missing_subject = sorted(REQUIRED_SUBJECT_COLUMNS - subject_header)
    if missing_subject:
        raise ValidationError(f"Subject demo table is missing columns: {missing_subject}")

    summary_header = read_csv_header(root / "docs" / "tables" / "demo_rfmi_summary.csv")
    missing_summary = sorted(REQUIRED_SUMMARY_COLUMNS - summary_header)
    if missing_summary:
        raise ValidationError(f"Summary demo table is missing columns: {missing_summary}")

    qc_header = read_csv_header(root / "docs" / "tables" / "demo_qc_template.csv")
    missing_qc = sorted(REQUIRED_QC_COLUMNS - qc_header)
    if missing_qc:
        raise ValidationError(f"QC demo template is missing columns: {missing_qc}")


def main() -> None:
    args = parse_args()
    root = args.root.expanduser().resolve()
    validate_required_files(root)
    validate_readme_language(root)
    validate_notebook(root)
    validate_static_tables(root)
    print("Public demo validation passed.")


if __name__ == "__main__":
    main()
