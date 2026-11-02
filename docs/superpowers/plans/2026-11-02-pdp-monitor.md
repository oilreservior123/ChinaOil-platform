# Frozen year-end PDP monthly monitoring

Goal: Two reference-style charts in the decision platform's reserves area: frozen prior-year-end production baseline versus observed monthly production, then updated future forecasts with distinct 95% confidence and prediction intervals; automatic local expert assessment and next actions.

Data: default explicitly generated block monthly data, not the uploaded Xinjiang field figures. Support user monthly oil tonnes, average producing wells, water volume, pressure and optional actual issued baseline. Do not publish the supplied images. Preserve other routes and concurrent changes on GitHub.

Models: per-producing-well calendar-day exponential decline (log-linear OLS); seeded 3-month residual block bootstrap for conditional mean confidence intervals, and extra future lognormal residual for monthly prediction intervals. Use only pre-cutoff data for original baseline and data through as-of for updates. Fixed prior plan never refits on current-year actuals. Optional fixed gain scenario is conditional, not causal efficacy.

Alerts: configurable percentage deficit, consecutive months, lower prediction bound and one-sided approximate-normal tail with monthly multiplicity correction; CUSUM is supporting evidence. Missing months are not zero. Model forecast intervals are not PDP certification probabilities.

Expert: local evidence rules from well availability, water cut and pressure changes; compare source-labelled public Volve trend cases and report similarity, not success probabilities or causal proof. Output evidence gaps, candidate measures, priority and follow-up. Handoff a reviewable report into the existing analysis assistant.

Checks: RED→GREEN tests for calendar normalization, frozen baseline invariance, no future leakage, CI vs PI, externally supplied baseline, invalid and missing data, positive/negative warnings, source-labelled cases, and exports. Run full existing tests, browser flows, then publish to the existing GitHub Pages route.

## Verification ledger
- 13 new regression tests observed RED then GREEN, including frozen baseline invariance, no future leakage, month/well normalization, CI vs PI, multi-year issued plans, preserved plans on actuals upload, zero-well restoration gain, and standalone SVG legends.
- Independent review: fixed zero-well scenario gain omission and embedded full titles/series/band legends in SVG exports.
- Generated demonstration smoke check: 46 months, 24 frozen fit months, 6 updated fit months, 12 forecast months, all interval endpoints finite; 4 expert action candidates and 4 public Volve trend cases available.
- Original uploaded images are reference-only and are not published. Unrelated workspace temporary download file remains untouched.
- Remote source was re-read; concurrent monitoring-inbox code and remote documentation/styles preserved.
