# AI Image Disclosure

The example open-eye child facial image in `example_data/images/` is synthetic and AI-generated.

It is included only to demonstrate the public computational workflow:

1. run MediaPipe Face Landmarker;
2. export landmark coordinates;
3. draw coordinate-based full-face, eye-zoom, and RFMI-line overlays;
4. create a blank blinded manual quality-control template;
5. compute RFMI indices;
6. create subject-level and summary RFMI tables.

The synthetic image does not depict a real participant and should not be interpreted as study data. In a real study, statistical analyses should be performed on approved participant images and metadata according to the relevant ethics protocol and consent documents.

## Public-use limitations

- The image is a repository demonstration asset, not participant data.
- The image and derived outputs should not be used for identity inference, diagnosis, clinical decision-making, or claims about real child populations.
- The static preview tables generated from this image demonstrate file structure only; they are not statistical results from a study cohort.
- Real child facial images should not be substituted into the public workflow unless the user has appropriate ethics approval, consent, secure storage, and data-governance procedures.

## Provenance statement

The repository treats the included face image as a synthetic AI-generated demonstration asset supplied for code review and reproducibility testing. No claim is made that it depicts or is derived from a real child participant. If the repository is submitted with a manuscript, authors should retain any available generation records, prompts, dates, and tool-license information in their study documentation.
