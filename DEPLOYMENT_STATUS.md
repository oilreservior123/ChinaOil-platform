# Deployment preparation

This branch contains the GeoTwin 2.0 application source, Python calculation service, tests and GitHub Pages workflow. It is not yet a complete runnable public deployment.

Publication of dist/assets/, dist/downloads/ and the existing trained model assets is pending explicit approval after an automatic approval review rejected a trained weight upload to this public repository. No uploaded user data or trained weights have been published by this change. Do not merge or deploy this branch until the required runtime assets are approved and added.

Prepared platform: 13 model interfaces, CSV/JSON/JSONL uploads, training/validation/test splits, inference and downloads. GitHub Pages serves the frontend only; the Python service must run independently.

Checks completed locally before source import: 23 frontend tests and 13 backend tests. Existing production platform remains available separately.
