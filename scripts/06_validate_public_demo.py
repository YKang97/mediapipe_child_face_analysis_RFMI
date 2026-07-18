from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REQUIRED_FILES = [
    ".python-version",
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
    "notebooks/RFMI_Image_to_Indices_Demo.ipynb",
    "scripts/01_prepare_project.py",
    "scripts/02_detect_and_overlay.py",
    "scripts/03_generate_qc_template.py",
    "scripts/04_compute_rfmi.py",
    "scripts/05_summarize_rfmi.py",
    "scripts/06_validate_public_demo.py",
]

REQUIRED_PACKAGES = {
    "mediapipe",
    "pillow",
    "pandas",
    "numpy",
    "matplotlib",
    "openpyxl",
    "jupyter",
}

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
    "manual quality-control template for blinded assessment",
]


class ValidationError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the RFMI public demonstration repository.")
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


def validate_environment_specification(root: Path) -> None:
    python_version = (root / ".python-version").read_text(encoding="utf-8").strip()
    version_parts = python_version.split(".")
    if len(version_parts) != 3 or not all(part.isdigit() for part in version_parts):
        raise ValidationError(
            f".python-version must contain a three-part Python version: {python_version!r}."
        )

    pinned_requirements: dict[str, str] = {}
    for raw_line in (root / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            raise ValidationError(f"Requirement is not exactly pinned: {line}")
        package, version = line.split("==", maxsplit=1)
        pinned_requirements[package.strip().lower()] = version.strip()

    if set(pinned_requirements) != REQUIRED_PACKAGES:
        raise ValidationError(
            "requirements.txt does not contain the required set of pinned direct dependencies: "
            f"{sorted(pinned_requirements)}"
        )


def validate_readme_language(root: Path) -> None:
    readme = (root / "README.md").read_text(encoding="utf-8")
    missing = [phrase for phrase in REQUIRED_README_PHRASES if phrase not in readme]
    if missing:
        raise ValidationError(f"README.md is missing required cautionary language: {missing}")


def validate_notebook(root: Path) -> None:
    notebook_path = root / "notebooks" / "RFMI_Image_to_Indices_Demo.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    if notebook.get("nbformat") != 4:
        raise ValidationError("Notebook nbformat is not 4.")
    text = "\n".join("".join(cell.get("source", [])) for cell in notebook.get("cells", []))
    required_phrases = [
        "RFMI extraction framework",
        "Runtime environment",
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

    with (root / "docs" / "tables" / "demo_rfmi_summary.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        summary_rows = list(csv.DictReader(handle))
    for row in summary_rows:
        if row.get("n") == "1":
            if row.get("sd", "").strip():
                raise ValidationError("Sample SD must be blank when the synthetic demo has n = 1.")
            if not row.get("mean_sd", "").endswith("+/- NA"):
                raise ValidationError("The n = 1 summary must label sample SD as NA.")

    qc_header = read_csv_header(root / "docs" / "tables" / "demo_qc_template.csv")
    missing_qc = sorted(REQUIRED_QC_COLUMNS - qc_header)
    if missing_qc:
        raise ValidationError(f"QC demo template is missing columns: {missing_qc}")


def main() -> None:
    args = parse_args()
    root = args.root.expanduser().resolve()
    validate_required_files(root)
    validate_environment_specification(root)
    validate_readme_language(root)
    validate_notebook(root)
    validate_static_tables(root)
    print("Public demo validation passed.")


if __name__ == "__main__":
    main()
