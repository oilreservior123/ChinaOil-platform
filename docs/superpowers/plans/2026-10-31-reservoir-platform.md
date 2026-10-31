# Reservoir platform implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Deliver the specified functional reservoir demonstration with PPT1–25 coverage, reproducible model assets and truthful metrics.
**Architecture:** Buildless static Sites shell; scientific asset preparation isolated from browser implementation; pure calculation modules with tests; source-backed JSON datasets.
**Tech Stack:** HTML/CSS, ES modules, SVG/Canvas, Python numpy/scipy/sklearn and available model runtime.
**Spec:** docs/superpowers/specs/2026-10-31-reservoir-platform-design.md

## Global constraints
- All functionality outside user-selected scope is an entry button only.
- Dataset origin, generated labels and frozen-run versus live-calculation status visible.
- Avoid train/test leakage; keep source namespaces and meaningful units.
- No unconfirmed natural-anomaly, root-cause, real hydraulic connectivity or production-grade fracture claims.
- Reduced motion and narrow-screen layout supported.

## Review focus
- Missing/zero/negative observations must retain meaningful missingness and avoid division errors.
- Empty search, unmatched graph targets and invalid dates show clear empty states.
- Rapid navigation/selection must not leave stale selected-well results or animation leaks.
- Test targets never enter browser model training inputs.
- Scope-only entry buttons must report unavailable status, not fake completion.

## Tasks
- [ ] Recover validated data and build source/requirement contracts; assert checksum correctness and all25pages mapped.
- [ ] Test calculation interfaces first: arpsRate/fitting, rule checks, graph search, time aggregation, topological execution gating. Run tests failing, implement minimal routines, rerun.
- [ ] Produce scientific model assets with actual split/metric records; validate contracts and no false status.
- [ ] Build navigation, charts, table filters, animated reservoir/graph/fractures and responsive panels.
- [ ] Connect live analysis and frozen experiment result selection; export JSON/CSV evidence and sample data.
- [ ] Audit all PPT functions and source badges; browser smoke test core routes, controls and mobile, then meaningful calculation tests.
- [ ] Package exact pushed source and deploy private Site; report URL and any model/runtime limits.
