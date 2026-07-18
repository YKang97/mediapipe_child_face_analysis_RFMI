# RFMI Methods and Landmark Definitions

This document defines the relative facial morphology indices (RFMI) used in the public demonstration. It records the coordinate source, landmark groups, formulas, and interpretation limits without implying that these variables are official MediaPipe clinical or medical measurements.

## Scope of the public demo

- The repository demonstrates an RFMI extraction framework and reproducible workflow using one synthetic, AI-generated, open-eye frontal child face image.
- The public repository does not include real child participant photographs, participant metadata, diagnostic labels, clinical scores, or study-level records.
- RFMI variables are within-image proportional indices. They are not centimeter or millimeter measurements because the input image is distance-uncalibrated and has no physical scale reference.
- Landmark coordinates are produced by MediaPipe Face Landmarker. RFMI formulas and landmark groupings are study-defined analysis choices.

## Coordinate source

Before detection, `scripts/01_prepare_project.py` applies embedded EXIF orientation, converts the input to RGB, and saves a JPEG copy at quality 95 in `data/images_analysis/`. All downstream coordinates and RFMI values are derived from this prepared analysis copy.

`scripts/02_detect_and_overlay.py` runs MediaPipe Face Landmarker in image mode with one face requested. For each detected face, it exports normalized coordinates and pixel coordinates for every landmark row in `outputs_landmarks/landmarks_raw.csv`.

| Exported field | Meaning |
|---|---|
| `image_id` | Analysis image identifier, such as `SYN_open`. |
| `child_id` | Public demo subject identifier. For the included synthetic image this is `SYN`. |
| `state` | Image state. The public workflow uses `open`. |
| `landmark_index` | Zero-based MediaPipe landmark index. |
| `x_norm`, `y_norm`, `z_norm` | MediaPipe normalized landmark coordinates. |
| `x_px`, `y_px` | Pixel coordinates obtained by multiplying normalized x/y values by image width/height. |

## Landmark groups used by the demo

The landmark indices below are hard-coded in the scripts so that overlay figures and RFMI tables are reproducible. The two eye-region variables are named by landmark index groups rather than anatomical left/right labels to avoid ambiguity caused by image mirroring, camera perspective, and viewer orientation.

| Group | Landmark indices | Demo role |
|---|---:|---|
| 33-133 eye-region horizontal width | 33, 133 | Denominator for `eye_33_133_aperture_index`. |
| 33-133 eye-region vertical pairs | 159-145, 158-153, 160-144 | Three upper-lower eyelid distances averaged for the 33-133 aperture index. |
| 263-362 eye-region horizontal width | 263, 362 | Denominator for `eye_263_362_aperture_index`. |
| 263-362 eye-region vertical pairs | 386-374, 385-380, 387-373 | Three upper-lower eyelid distances averaged for the 263-362 aperture index. |
| Face width | 234, 454 | Denominator for face-ratio indices. |
| Nose width | 98, 327 | Numerator for nose-width/face-width index. |
| Mouth width | 61, 291 | Numerator for mouth-width/face-width index. |
| Jaw width | 172, 397 | Numerator for jaw-width/face-width index. |

## Distance calculation

All geometric distances are two-dimensional Euclidean pixel distances calculated from `x_px` and `y_px`:

```text
distance(a, b) = sqrt((x_a - x_b)^2 + (y_a - y_b)^2)
```

Because each RFMI is expressed as a ratio, the values are intended to describe within-image facial proportions rather than absolute size.

## RFMI formulas

| Output column | Formula | Interpretation in this demo |
|---|---|---|
| `face_width_px` | `distance(234, 454)` | Pixel face-width reference used for ratio normalization. |
| `eye_33_133_aperture_index` | `mean(distance(159,145), distance(158,153), distance(160,144)) / distance(33,133)` | Relative opening of the 33-133 eye-region group within the detected face image. |
| `eye_263_362_aperture_index` | `mean(distance(386,374), distance(385,380), distance(387,373)) / distance(263,362)` | Relative opening of the 263-362 eye-region group within the detected face image. |
| `mean_eye_aperture_index` | `mean(eye_33_133_aperture_index, eye_263_362_aperture_index)` | Average relative eye-region opening. |
| `eye_aperture_asymmetry_index` | `abs(eye_33_133_aperture_index - eye_263_362_aperture_index)` | Absolute difference between the two eye-region aperture indices. |
| `nose_width_face_width_index` | `distance(98,327) / distance(234,454)` | Nose-width proportion relative to face width. |
| `mouth_width_face_width_index` | `distance(61,291) / distance(234,454)` | Mouth-width proportion relative to face width. |
| `jaw_width_face_width_index` | `distance(172,397) / distance(234,454)` | Jaw-width proportion relative to face width. |

## Eye-state auxiliary scores

When MediaPipe returns face blendshapes, the demo keeps selected eye-related scores such as `eyeBlinkLeft`, `eyeBlinkRight`, `eyeWideLeft`, `eyeWideRight`, `eyeSquintLeft`, and `eyeSquintRight`.

These are MediaPipe model outputs. In this repository they are included as descriptive auxiliary columns only and should not be interpreted as diagnostic or clinical scores.

## Visual quality control

`scripts/03_generate_qc_template.py` creates a blank manual quality-control template from the generated overlay paths. The template is intended to support blinded assessment of whether landmark overlays align with visible facial regions before RFMI values are used in a real study dataset. The template does not implement blinding automatically. Studies should mask identifiers, randomize image order, and keep rater files separate according to a prespecified protocol.

The public demo does not contain real human ratings. In real child image studies, QC scoring should be performed under the study ethics approval and data-protection plan.

The calculation script produces RFMI rows for successfully detected images. It does not read completed QC scores or apply study-specific inclusion decisions. Researchers using real data should complete the QC process and apply prespecified inclusion criteria before statistical analysis.

## Interpretation limits

RFMI outputs should be described as image-derived, relative, and model-dependent. They should not be interpreted as:

- physical measurements in centimeters or millimeters;
- validated clinical biomarkers;
- diagnostic scores;
- population estimates, because the public demo uses only one synthetic example image;
- proof that the same workflow is valid for uncontrolled real-world child photographs without separate validation.

## Suggested methods description

A study using this workflow may describe the method as follows:

> We used MediaPipe Face Landmarker to export facial landmark coordinates from frontal open-eye images. We then computed study-defined relative facial morphology indices from selected landmark distance ratios. These RFMI variables are within-image proportional indices and are not official MediaPipe medical measurements.
