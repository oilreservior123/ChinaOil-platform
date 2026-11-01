# Production decision platform implementation plan

Goal: Deliver a GitHub Pages workbench implementing PPT 32–47 with auditable calculations and a configurable LLM service.
Architecture: Independent /decision/ application, shared existing /agent/ data and neural model engine; pure JS decision calculations; optional server-side LLM gateway.
Tech: buildless HTML/CSS/ES modules, local TensorFlow.js, FastAPI gateway.
Spec: User request and attached PPT pages 32–47. Preserve existing /agent/ and root routes.

## Global constraints
- CNPC red/white/gold branding; Chinese field and unit annotations; responsive keyboard-accessible controls.
- Every model has formula, architecture, parameter notes, matching sample schema, split counts and measured duration.
- Real Volve/3W/ESP/DST reuse existing published samples; synthetic block/profile/measure/evolution data clearly labeled.
- Time-based split by default. Independent test data never used for model selection.
- GitHub Pages cannot host Python/LLM inference: ship gateway integration and expose connection state honestly.
- PPT constraints corrected dimensionally: injection pressure compared to fracture pressure; reservoir-volume injection/withdrawal balance requires PVT.
- SEC area is research forecasting, not a certified reserves assessment or guaranteed reserve growth.

## Review focus
- Missing/invalid CSV and overlapping split records rejected with an actionable error.
- Synthetic and real datasets never silently merged; selecting a different model clears incompatible experiment state.
- Layer fractions conserve total volume; optimisation never violates configured supply/handling/pressure bounds.
- Calculation and model evaluation do not invent metrics, causal labels, or measured training times.
- User-supplied text escaped; no API secret stored in public source or browser persistence.

## Tasks
- [x] 1. Add failing numerical tests: balance volume basis, layer conservation, lag direction, constrained allocation, incremental effect vs baseline, reserve economic limit, split validation.
- [x] 2. Implement decision engine, gradient boosted/forest regression and isolation forest; generate labeled small synthetic datasets and PPT mapping.
- [x] 3. Build dashboard, connectivity, profiles, optimisation, measures, evolution, reserves, model studio and copilot pages, with upload/export and shared real model engine.
- [x] 4. Add secure optional LLM gateway, tests and setup guide; no credentials in frontend.
- [x] 5. Verify existing suite, new numerical tests, module syntax and browser flows; publish via existing GitHub Pages workflow and check run status.

## Verification and review ledger

- Fresh clone isolated on feat/production-decision. Existing baseline: 65 tests green.
- Numerical tools, CSV numeric coercion, lag feature isolation, busy state guard, provenance: 15 new tests pass.
- Independent reviewer found three important issues. Fixed numeric CSV cutpoints, blocked active-training mutations, attached independent-tool provenance and inputs, and cleared reports on production scope changes. Regression tests were observed red then green.
- 17 model paths completed actual training/prediction smoke checks; report in docs/decision-model-verification.json. XGBoost not run: optional external package/service not configured. Existing rules model covered by prior tests.
- Optional gateway: 3 standard-library unit tests pass; no live upstream LLM credentials supplied.
- Decisions: use independent new /decision/ route in authorized existing public repository; browser models run locally; LLM/XGBoost require external service and are labeled disconnected.
- Browser loopback preview was inaccessible from separate cloud browser; production browser QA follows GitHub deployment.
