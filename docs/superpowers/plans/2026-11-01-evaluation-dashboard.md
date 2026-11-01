# Model evaluation and forecast dashboard

Goal: Add a chart-rich, auditable training/validation/test result dashboard and future production scenarios to the existing decision platform.
Architecture: Pure evaluation calculations in evaluation.mjs, SVG charts and result views in evaluation-view.mjs, forecast adapter in forecast.mjs; integrate with studio state without changing model fitting or test selection.

- [x] Regression: MAE/MSE/RMSE/R²/MAPE/sMAPE/Bias, valid sample and prediction coverage. Classification: accuracy, macro precision/recall/F1, per-class metrics and confusion matrix; multi-label reported separately.
- [x] After fitting, evaluate all three sets once; preserve results by role. Show counts, metrics table, grouped comparison, per-set prediction curves, observed-vs-predicted scatter, residual curve/histogram, per-well error bars or confusion matrix. Do not mix incomparable metrics on one axis.
- [x] Dataset and well selectors; complete result and metric exports, with dataset identity, actual/prediction/error and source.
- [x] Future 7/30/60-day scenarios for compatible production predictors. Freeze model parameters and explicitly hold future exogenous inputs constant; exclude classification/profile/PINN from production extrapolation. Reference residual bands are not calibrated confidence intervals.
- [x] Test constant/zero targets, missing labels/predictions, unknown classes, multi-label membership, split boundaries and recursive forecasts. Re-run existing suite and browser flows, then publish through existing GitHub Pages workflow.

Source: user follow-up requesting evaluation metrics, results for all three datasets, predictions, and more charts. Scope authorized by original build/deploy request; continue on existing public GitHub route.

## Verification ledger
- 14 new numerical/flow tests observed failing before implementation then passing; includes missing labels, constant observations, macro/multilabel metrics, split context, recursive forecasting, validation loss and forecast selection race.
- Actual CPU smoke tests: 11 models each produced all 3 sets; 6 compatible predictors each produced 3 future days. Details: docs/decision-evaluation-verification.json.
- Independent review: fixed the active forecast well-selection race by disabling inputs while busy and guarding state mutation. Hardened scatter plot extent calculation against large argument lists.
- All model fit parameters remain fixed during evaluation and forecast. Validation residual references explicitly are not calibrated confidence intervals.
- GitHub publication and production browser checks performed in this same task.
