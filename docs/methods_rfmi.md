# RFMI Methods and Landmark Definitions

This document defines the public demonstration's relative facial morphology indices (RFMI) and the MediaPipe Face Landmarker output fields used to compute them. It is intended to make the repository auditable by reviewers without implying that these variables are official MediaPipe clinical or medical measurements.

## Scope of the public demo

- The public repository demonstrates a computational workflow on one synthetic, AI-generated, open-eye frontal child face image.
- The public repository does not include real child participant photographs, participant metadata, diagnostic labels, clinical scores, or study-level records.
- The RFMI variables are within-image proportional indices. They are not centimeter measurements because the demo image is distance-uncalibrated and has no physical scale reference.
- The landmark coordinates are produced by MediaPipe Face Landmarker. The RFMI formulas and landmark groupings are study-defined analysis choices.

## Coordinate source

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

The landmark indices below are hard-coded in the scripts so that overlay figures and RFMI tables are reproducible. They are selected MediaPipe landmark output indices used as geometric anchors for this public demo.

| Group | Landmark indices | Demo role |
|---|---:|---|
| Right eye horizontal width | 33, 133 | Denominator for right eye aperture index. |
| Right eye vertical pairs | 159-145, 158-153, 160-144 | Three upper-lower eyelid distances averaged for right eye aperture. |
| Left eye horizontal width | 263, 362 | Denominator for left eye aperture index. |
| Left eye vertical pairs | 386-374, 385-380, 387-373 | Three upper-lower eyelid distances averaged for left eye aperture. |
| Face width | 234, 454 | Denominator for face-ratio indices. |
| Nose width | 98, 327 | Numerator for nose-width/face-width index. |
| Mouth width | 61, 291 | Numerator for mouth-width/face-width index. |
| Jaw width | 172, 397 | Numerator for jaw-width/face-width index. |

## Distance calculation

All geometric distances are two-dimensional Euclidean pixel distances calculated from `x_px` and `y_px`:

```text
distance(a, b) = sqrt((x_a - x_b)^2 + (y_a - y_b)^2)
```

This means RFMI values are sensitive to the accuracy of MediaPipe landmark placement, image quality, face pose, occlusion, and the appropriateness of the selected landmark anchors.

## RFMI formulas

| Output column | Formula | Interpretation in this demo |
|---|---|---|
| `face_width_px` | `distance(234, 454)` | Pixel face-width reference used for ratio normalization. |
| `right_eye_aperture_index` | `mean(distance(159,145), distance(158,153), distance(160,144)) / distance(33,133)` | Relative right eye opening within the detected face image. |
| `left_eye_aperture_index` | `mean(distance(386,374), distance(385,380), distance(387,373)) / distance(263,362)` | Relative left eye opening within the detected face image. |
| `mean_eye_aperture_index` | `mean(right_eye_aperture_index, left_eye_aperture_index)` | Average relative eye opening. |
| `eye_aperture_asymmetry_index` | `abs(right_eye_aperture_index - left_eye_aperture_index)` | Absolute left-right difference in relative eye aperture. |
| `nose_width_face_width_index` | `distance(98,327) / distance(234,454)` | Nose-width proportion relative to face width. |
| `mouth_width_face_width_index` | `distance(61,291) / distance(234,454)` | Mouth-width proportion relative to face width. |
| `jaw_width_face_width_index` | `distance(172,397) / distance(234,454)` | Jaw-width proportion relative to face width. |

## Blendshape fields

When MediaPipe returns face blendshapes, the demo keeps selected eye-related scores:

- `eyeBlinkLeft`
- `eyeBlinkRight`
- `eyeWideLeft`
- `eyeWideRight`
- `eyeSquintLeft`
- `eyeSquintRight`

These are MediaPipe model outputs. In this repository they are included as descriptive demo columns only and should not be interpreted as diagnostic or clinical scores.

## Interpretation limits

RFMI outputs should be described as image-derived, relative, and model-dependent. They should not be interpreted as:

- physical measurements in centimeters or millimeters;
- validated clinical biomarkers;
- diagnostic scores;
- population estimates, because the public demo uses only one synthetic example image;
- proof that the same workflow is valid for uncontrolled real-world child photographs without separate validation.

## Recommended reporting language

For manuscripts or public repository descriptions, use language such as:

> We used MediaPipe Face Landmarker to export facial landmark coordinates from frontal open-eye images. We then computed study-defined relative facial morphology indices from selected landmark distances. These RFMI variables are within-image proportional indices and are not official MediaPipe medical measurements.
