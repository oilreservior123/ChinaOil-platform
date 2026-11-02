# Reservoir Twin Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build and deploy the approved reservoir measures design and evaluation workbench.

**Architecture:** Independent buildless dist/twin application; pure physics, statistics and optimisation modules, DOM views and SVG charts. Reuse existing static datasets and optional decision gateway.

**Tech Stack:** JavaScript ES modules, HTML/CSS, node:test, GitHub Pages.

**Spec:** docs/superpowers/specs/2026-11-02-reservoir-twin-design.md

## Global Constraints
- Preserve existing platforms; publish only additive files under dist/twin plus documentation/tests.
- Explicitly identify synthetic data, physical approximations and unavailable external services.
- Default chronological split 70/15/15; no future or test observations in model fitting.
- Chinese unit annotations; no secrets in source or local storage.

## Review Focus
- Missing/zero production and undefined ratios must remain distinct.
- Duplicate well/date and overlapping independent splits must be rejected.
- Infeasible or nonfinite simulations must never enter recommended solution set.
- Case analogues without intervention labels cannot imply field causal evidence.
- All output must be invalidated after data/model/physics changes.

### Task 1: Computational core
Files: dist/twin/physics.mjs, statistics.mjs, optimise.mjs; tests/twin.test.mjs.
Interfaces: simulate(params, control, days, dt) -> rows and balance; train(rows, options, partitions) -> fitted models and split metrics; forecast(fit, rows, days) -> quantile curves; optimise(params, options) -> feasible archive/history.
- [x] Write failing tests for ratios, mass balance, physical bounds, chronological splits, overlap/missing validation, future isolation, seeded algorithms and infeasible rejection.
- [x] Run node --test tests/twin.test.mjs; expect missing modules.
- [x] Implement explicit-unit reduced oil/water tank, train-only ridge/decline/nearest-neighbour forecasts and residual sampling, constrained MOPSO/NSGA-II/GA.
- [x] Run tests to PASS and commit core.

### Task 2: Views and model documentation
Files: dist/twin/index.html, styles.css, charts.mjs, catalog.mjs, app.mjs, README.md.
Interfaces consume Task 1; graph and table views show provenance, formulas, controls and computed metrics.
- [x] Build seven linked views, editable scheme comparison, 5 forecast charts, quantitative conclusions, Pareto selections, refinement check, all-model cards and memory-only imports/downloads.
- [x] Validate ES module syntax and render browser; exercise split/train/forecast/optimise/export; correct observed errors.
- [x] Commit UI and docs.

### Task 3: Review and publication
Files: tests/twin-ui.test.mjs and documentation.
- [x] Run full relevant core/UI checks. Review formulas, units, invalidation and model claims independently of authoring pass.
- [ ] Push additive Git tree using current main as base with expected head lease.
- [ ] Verify GitHub Actions terminal result and Pages URL. Report external service status accurately.

## Verification ledger
- 15/15 targeted tests pass, including all seven rendered views.
- Independent review found four Important issues (partition provenance/origin, invalid domains, validation recovery, stale reports); fixed with regression tests.
- Browser checked synthetic/Volve switching, all five curves, NSGA-II Pareto, preference selection and step refinement.
- Gateway source contract verified: POST health returns llm_configured; chat evidence must be an object. Payload fixed and tested. Live gateway unavailable: remote model inference not claimed.
- Publication is additive; preview-only dist/index.html and .openai/hosting.json excluded.
