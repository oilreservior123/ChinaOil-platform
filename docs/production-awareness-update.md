# Monitoring data, annotations and training coverage

## F-5 root cause and correction

The previous global time split placed Volve well15/9-F-5 only in evaluation, while Arps/CRM parameters are estimated per well. The error meant no historical fit existed, not an invalid well identifier.

Arps, CRM and Horner now default to chronological splitting within each well/test, with clear disclosure that cutoffs differ across wells. Global chronological and well-holdout modes remain available for appropriate experiments. Training coverage is shown before fitting. New/insufficient-history objects return a row with null prediction, a coverage status and an actionable reason; other objects continue. Null predictions are omitted from regression metrics but retained in result downloads. No test records are used to auto-fit missing parameters.

## Data and models

- Volve:9161 production records plus original workbook. Existing rule, Arps, CRM, TCN and STGNN/GDN modules.
- 3W: all1119 real event summaries,1040 complete for training. Genuine six-feature event classifier. Original source filenames, missingness and sensor fallback preserved; these are summaries, not the full high-frequency original series. Observed labels including transient offset and43 directory-label discrepancies preserved.
- ESPset: all6032 real feature rows; genuine seven-feature fault classifier. Original frequency/amplitude scales retained; full raw spectrum remains at official source.
- DST:16936 observations, with complete original ZIP. Per-test Horner pressure regression; only valid sufficiently long tests retained for default chronological evaluation. PINN still requires measured spatial coordinates and explicit normalization.
- Spraberry tracer: original data not acquired; real upload interfaces and one-dimensional pulse advection-dispersion fit provided. No synthetic values are presented as field measurements.

## Annotations

Red priority review, yellow attention, blue monitoring, green no selected-rule match, gray missing coverage. Node colors derive from real rule results in the final90-day window; connecting edges remain explicitly illustrative. Every chart has named color/line-style legends, axis and Chinese unit notes. Horner uses actual log-H x coordinates. Multi-well predictions are not concatenated into one misleading time curve. Unit table covers standard volumes, MPa/bar/psi, percent versus percentage points, minutes/days/metres, vibration frequency scaling, and metric meanings.

## Verification

Regression tests cover late-start well splitting, uncovered-object continuation, identity checks without fabricated dates, genuine neural training, no-truth inference, unknown classes and specialty fitting. Browser QA includes full six-well Arps evaluation,3W/ESP/Horner data loading/training and export. Field diagnosis and training metrics remain research outputs requiring independent validation.

## Resumed release verification (2026-11-01)

All 63 Node tests pass and all configured syntax checks pass. Full built-in Volve evaluation with per-well chronological 70/15/15 splitting covers six wells for both Arps and CRM, with 24 F-5 test predictions per model and no uncovered rows. Arps: 1379 test rows, RMSE 307.677 standard cubic metres/day, R² -1.89581. CRM: 1343 test rows, RMSE 1320.603 standard cubic metres/day, R² -0.09989. Negative R² is retained: these simplified fits do not establish adequate field prediction performance. Dataset counts verified: 1119 3W event summaries, 6032 ESP feature rows, 16936 DST observations.


2026-11-01轻量发布覆盖：四套可下载真实子集、公式参数注释和曲线颜色名称。新3W/ESP/DST完整文件及原始二进制不随本次轻量发布，改由原始来源提供。子集仅用于快速流程验证。
