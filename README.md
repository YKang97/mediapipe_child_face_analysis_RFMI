# RFMI Extraction Framework for Child Facial Images

This repository provides an executable demonstration of a relative facial morphology index (RFMI) extraction framework for distance-uncalibrated, open-eye frontal child facial photographs.

The workflow converts an input image into MediaPipe Face Landmarker coordinates, coordinate-based overlay figures, a blank blinded manual quality-control template, study-defined RFMI variables, and descriptive output tables. The included example uses one synthetic, AI-generated image. No real child participant photographs, participant metadata, or human QC ratings are included.

## Scope

The repository contains two connected components:

1. **Core executable workflow**: image manifest creation, MediaPipe detection, landmark export, coordinate overlays, blank QC materials, RFMI calculation, and tabular output.
2. **Study-level validation steps**: researchers review the overlays, complete the QC template, apply prespecified inclusion rules, and perform validation analyses appropriate to their own dataset.

The scripts calculate RFMI values for successfully detected images. They do not convert blank QC fields into automated inclusion decisions. Transformation-based sensitivity analyses, test-retest reliability, and comparisons with manual or three-dimensional measurements are also outside this synthetic demonstration and should be implemented separately when required by a study protocol.

RFMI variables are within-image proportions. They are not centimeter measurements or clinical biomarkers, and they are not official MediaPipe medical measurements.

## Workflow

![Six-part RFMI workflow overview](docs/figures/rfmi_six_part_overview.png)

| Part | Operation | Main output |
|---|---|---|
| 1 | Verify the runtime and prepare the synthetic input | Image manifest and fixed model file |
| 2 | Run MediaPipe Face Landmarker | Landmark coordinates, eye-state auxiliary scores, and detection log |
| 3 | Draw coordinate-based overlays | Full-face, eye-region, and RFMI reference-line figures |
| 4 | Create blank blinded QC materials | QC template and scoring codebook |
| 5 | Calculate RFMI variables | Image-level and subject-level tables |
| 6 | Create descriptive outputs | RFMI subject table and summary table |

All points and lines in the overlay figures are generated from exported MediaPipe landmark coordinates; no landmarks are manually placed.

## Example Input and Outputs

### Synthetic input

![Synthetic open-eye image](docs/figures/demo_synthetic_input.jpg)

### Full-face landmark overlay

![Full-face landmark overlay](docs/figures/demo_full_face_overlay.jpg)

### Eye-region landmark overlay

![Eye-region landmark overlay](docs/figures/demo_eye_zoom_overlay.jpg)

### RFMI distance-line overlay

![RFMI distance-line overlay](docs/figures/demo_rfmi_lines_overlay.jpg)

### Subject-level RFMI table

![Subject-level RFMI table preview](docs/figures/demo_rfmi_subject_table.png)

### Descriptive RFMI summary

![RFMI summary table preview](docs/figures/demo_rfmi_summary_table.png)

Machine-readable previews are available in [`docs/tables/`](docs/tables/). Because all previews come from one synthetic image, they demonstrate output structure only and are not research estimates.

## Repository Contents

| Path | Purpose |
|---|---|
| `example_data/images/` | Synthetic input image |
| `notebooks/RFMI_Image_to_Indices_Demo.ipynb` | Step-by-step executable demonstration |
| `scripts/` | Six command-line workflow scripts |
| `docs/methods_rfmi.md` | Landmark groups, formulas, and interpretation limits |
| `docs/reproducibility.md` | Environment, generated outputs, and validation checklist |
| `docs/figures/` | Static visual previews |
| `docs/tables/` | Static machine-readable previews |
| `AI_IMAGE_DISCLOSURE.md` | Synthetic image provenance and use limitations |
| `CITATION.cff` | Software citation metadata |

Generated folders such as `outputs_manifest/`, `outputs_landmarks/`, `outputs_overlay/`, `outputs_qc/`, `outputs_features/`, `outputs_stats/`, `models/`, and `logs/` are ignored by Git and are created when the workflow runs.

## Installation

Use Python 3.13.9 in a clean environment and install the exactly pinned direct dependencies:

~~~bash
python -m pip install -r requirements.txt
~~~

The tested versions are recorded in [`.python-version`](.python-version) and [`requirements.txt`](requirements.txt). The notebook reads these files and verifies the active environment before running.

On Windows systems without long-path support, create the virtual environment in a short location such as `C:\venvs\rfmi`. On minimal Linux systems, MediaPipe/OpenCV may also require `libegl1`, `libgl1`, `libgles2`, and `libglib2.0-0`. Platform-specific instructions are provided in [`docs/reproducibility.md`](docs/reproducibility.md).

## Run the Workflow

### Jupyter notebook

Open [`notebooks/RFMI_Image_to_Indices_Demo.ipynb`](notebooks/RFMI_Image_to_Indices_Demo.ipynb) and run all cells from top to bottom.

The notebook searches the current working directory and its parents for the repository root. If this fails, set `ROOT_OVERRIDE` in the first code cell to the cloned repository path.

### Command line

From the repository root:

~~~bash
python scripts/01_prepare_project.py --root . --open-image example_data/images/SYN_open.jpg --child-id SYN
python scripts/02_detect_and_overlay.py --root .
python scripts/03_generate_qc_template.py --root .
python scripts/04_compute_rfmi.py --root .
python scripts/05_summarize_rfmi.py --root .
python scripts/06_validate_public_demo.py --root .
~~~

## Fixed MediaPipe Model

The preparation script downloads or verifies this Face Landmarker model:

~~~text
https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
~~~

Expected SHA256:

~~~text
64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff
~~~

The fixed URL and file hash prevent an unrecorded model change from altering the workflow.

## RFMI Outputs

The demonstration calculates:

- 33-133 eye-region aperture index;
- 263-362 eye-region aperture index;
- mean eye aperture index;
- eye aperture asymmetry index;
- nose-width/face-width index;
- mouth-width/face-width index;
- jaw-width/face-width index;
- selected MediaPipe eye-state auxiliary scores.

Single-eye variables are named by MediaPipe landmark index groups instead of anatomical left/right labels. This avoids ambiguity caused by image mirroring and viewer perspective.

All geometric RFMI values are computed from MediaPipe landmark coordinates. The formulas and landmark groupings are study-defined analysis choices. See [`docs/methods_rfmi.md`](docs/methods_rfmi.md) for the exact definitions.

## Quality Control

The repository creates a blank QC template linked to the generated overlays. Researchers can use it to record whether landmarks align with visible facial regions before including RFMI values in a study dataset.

The synthetic demonstration does not contain completed ratings and does not automatically filter RFMI output by QC score. Studies using real images should prespecify rater training, scoring rules, disagreement resolution, and inclusion criteria under the applicable ethics and data-protection plan.

## Data, Ethics, and Limitations

The included demonstration image is synthetic and does not depict a real participant. Real child facial images and metadata require appropriate ethics approval, consent, secure storage, privacy protection, and data-governance procedures.

RFMI outputs are two-dimensional, image-derived, relative, and model-dependent. They do not correct automatically for yaw, pitch, roll, perspective shortening, camera intrinsics, expression, lighting, or occlusion. The demonstration does not establish clinical validity, diagnostic accuracy, or population reference values.

## Citation

If you use this repository, cite it using [`CITATION.cff`](CITATION.cff) and cite MediaPipe Face Landmarker using the official documentation. Describe RFMI variables as study-defined relative image indices and disclose the use of a synthetic image when referring to the included demonstration.

## License

The source code is released under the MIT License. See [`LICENSE`](LICENSE). The synthetic image and derived previews are demonstration assets; their provenance and use limitations are described in [`AI_IMAGE_DISCLOSURE.md`](AI_IMAGE_DISCLOSURE.md).
