# Genuine monitoring datasets and reproducible browser exports

All built-in measurements and identifiers come from the downloaded public sources listed below. No dates, fault labels, coordinates, observations, or unavailable tracer records are fabricated. Run `scripts/build-agent-monitoring-data.py --source-root /path/to/reservoir_datasets` using Python with pandas, NumPy and pyarrow to reproduce the three monitoring JSON arrays and catalog. JSON nonfinite numbers are forbidden; missing numeric values are `null`.

## Source and downloadable assets

| Dataset | Official source | Embedded original download | License / scope |
| --- | --- | --- | --- |
| Volve | https://www.equinor.com/energy/volve-data-sharing | `downloads/Volve_production_data.xlsx` | Equinor Open Data Licence; production workbook only |
| 3W 2.0.0 | https://github.com/petrobras/3W/tree/8aaa303f9b9d6ced690d136218d141624b10558d/dataset | `threew-events.json` (derived summaries) | CC BY 4.0; all 1119 genuine `WELL-*.parquet` files in directories 0–9 |
| Sweetwater DST V2 | https://data.mendeley.com/datasets/px455bwjg2/2 | `downloads/Sweetwater_DST_V2_original.zip` | CC BY 4.0; full downloaded archive |
| ESPset V3 | https://data.mendeley.com/datasets/m268jsw339/3 | `downloads/ESPset_features.csv` | CC BY 4.0; complete original semicolon-separated feature table |
| Spraberry tracer | https://oaktrust.library.tamu.edu/items/3eb9a1e3-2dba-486c-9c04-d25a2e95d270/full | None | Website security verification blocked retrieval; upload interface only |

The actual Volve workbook download was the disclosed third-party mirror https://raw.githubusercontent.com/Yuv7145/oil-well-production-analytics/main/data/Volve%20production%20data.xlsx . Full official raw archives are linked separately in catalog `raw_download_url`: DST https://data.mendeley.com/public-api/zip/px455bwjg2/download/2 and ESPset https://data.mendeley.com/public-api/zip/m268jsw339/download/3 . The 515,965,508 bytes of 3W parquet and approximately 115 MB ESP archive are deliberately not embedded. This repository contains the browser-sized derived JSON, downloadable 3W summaries, the small DST archive, and ESP feature CSV. Source attribution and licenses still apply to downloaded files.

## 3W: one record per real event file

`threew-events.json` has **1119 records**, one for every genuine real file, including incomplete records. Simulated and hand-drawn files are excluded. It contains file summaries, not the original full-resolution time series. Original directory event counts: 0:594, 1:4, 2:22, 3:32, 4:343, 5:11, 6:6, 7:36, 8:14, 9:57.

Each record contains real `well_id` (`WELL-xxxxx`), original filename `event_id`, relative `source_filename`, full `sample_count`, `event_code` (0–9), original English `event_label` from dataset.ini, binary `label` (normal 0/event 1), `source_event_code`, `class_values`, `stable_class_count`, `label_basis`, `transient_only`, `summary_complete`, `training_eligible` and `missing_features`. Event labels are confirmed against source class observations. Prefer the observed stable event class even where normal observations are more numerous. **59 events contain their event only as a transient class**; the documented `TRANSIENT_OFFSET=100` maps e.g. 102 to event 2. For these, `label_basis=transient_class_offset` and `transient_only=true`; their exact source class values remain available. No file is relabeled normal merely because only normal stable observations precede the transient event. Separately, **43 directory-9 files have only observed class 0** (no class 9 or 109); these retain Normal Operation / event_code 0, label_basis=stable_class_mode, and source_event_code=9. Directory placement is preserved but does not override the actual recorded class. Derived observed class counts are 0:637, 1:4, 2:22, 3:32, 4:343, 5:11, 6:6, 7:36, 8:14, 9:14.

Numeric features are `p_mean`, `p_std`, `p_delta` in **MPa** and `t_mean`, `t_std`, `t_delta` in **°C**. Mean/std use all finite observations; std is population standard deviation (`ddof=0`), delta is last minus first finite observation in original sample order. No source timestamps or invented dates are exported. Source pressure is Pa and is divided by 1,000,000.

Pressure uses P-PDG, falling back **only if wholly missing/nonfinite** in this order: P-TPT, PT-P, P-MON-CKP, P-JUS-CKP. Temperature uses T-TPT, then T-PDG, T-MON-CKP, T-JUS-CKP. These are actual but differently located sensors: fallback summaries must not be interpreted as measurements at the original sensor location. `pressure_sensor`/`temperature_sensor` and finite sensor counts disclose the selection. Finite zeros remain zeros; this export does not infer that a zero is an invalid measurement.

Pressure selection counts: P-PDG 827; P-TPT 136; P-MON-CKP 99; missing 57. Temperature selection: T-TPT 1035; T-PDG 4; T-MON-CKP 1; missing 79. **79 records lack one or more numeric features** and are retained with nulls, missing-feature lists and `training_eligible=false`; 1040 have complete features. Of the 79, 57 lack both pressure and temperature. Models must explicitly filter complete records and report exclusions, never zero-fill them. Original filename and well grouping permit leakage-aware evaluation.

## ESPset: complete original features

`esp-features.json` has **6032 records** and preserves all feature rows. `well_id=ESP-{esp_id}`, numeric `esp_id`, `sample_id` equals original `id`, and `fault` equals the original label. No dates are added. There are no missing features in the source table.

| Browser field | Exact original column |
| --- | --- |
| f_low | median(8,13) |
| f_rms | rms(98,102) |
| f_near | median(98,102) |
| f_1x | peak1x |
| f_2x | peak2x |
| f_a | a |
| f_b | b |

Values retain their original scales. The CSV does not declare a physical unit per feature; none is invented. Fault counts: Normal 4801; Unbalance 576; Faulty sensor 295; Rubbing 290; Misalignment 70. These are measured vibration experiment features associated with ESP identifiers, not oilfield daily production samples. Evaluation should group by ESP where possible to disclose transfer limitations.

## DST: real pressure recovery observations

`dst.json` combines **338 `DST_Data*.csv` files, 16,936 records, 192 API well IDs, and 966 phase-specific test IDs**. Overview and analysis files are excluded (the extracted archive has 677 CSV files in total). All original Data rows are retained, including missing cells. `well_id` is the API directory name; `test_id=API:file_stem:Period` keeps formations/test phases separate, `test_phase` preserves Period, and `sample_id=API:file_stem:original_row_number` is unique. `source_filename` preserves the relative file path.

`log_horner` is the **original `Log time`, interpreted as log10(H)**, not recomputed from elapsed time. `time_min` is `Time (min)` and `pressure` is `Pressure (psi) × 0.006894757` in MPa. Missing values: time_min 73; log_horner 3448; pressure 53. No values are imputed. Each Horner fit must select one test ID and use only finite log_horner/pressure pairs; source shut-in phases stay separate.

The source contains **no measured spatial coordinate x**. Mapping DST to the PINN card indicates subject relevance, not immediate trainability: actual x and appropriately normalized t must be supplied before that model can run. No spatial pressure field or coordinate is inferred from API or sample index.

## Catalog

`catalog.json` is an array of five records: volve, threew, dst, esp, tracer. Each declares title, description, availability, static path, actual row count, unit notes, source URL, download URL, full raw-source URL and relevant model IDs. Tracer has `available=false`, `path=null`, `count=0`, `download_url=null`; it must not offer a generated sample dataset. Volve limitations and model eligibility follow the existing `SOURCES.md`: no ground-truth root_cause, no measured x coordinate, and field-total injection rather than pairwise allocation.
