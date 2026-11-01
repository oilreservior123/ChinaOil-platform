# Production situation agent implementation plan
Goal: Deliver an independent Chinese production surveillance workbench under dist/agent and deploy through the existing GitHub Pages pipeline.
Architecture: Buildless browser app, local CSV/JSON/XLSX import, TensorFlow.js training and classical numerical fitting. Per-model state owns train/validation/test/inference, measured duration, metrics, model structure and export. Source data stays local. Backend-free Pages deployment.
Spec: User requirements and PPT slides 26–30, inspected in conversation.
Constraints: Preserve existing platform, ChinaOil red/gold/light styling, Chinese unit notes; no fabricated labels or metrics; explicit simplified-model assumptions.
Tasks:
- [x] Data contracts, deterministic split, metrics, rules and validation with tests first.
- [x] Eight model engines: rules, Arps, CRM, TCN, CRM-constrained GraphSAGE–TCN, pressure PINN, graph residual detector, multilabel diagnostic MLP. Numerical/neural smoke tests.
- [x] Dashboard, model workbench with five upload modes, visual architectures, charts, experiment tracking and evidence-backed recommendations.
- [x] Browser interaction QA, full regression suite, GitHub atomic publication and Pages deployment verification.
Review focus: missing values and invalid numbers; event/time leakage; absent labels; unavailable libraries; unsafe imported content and CSV export.
Ruling: Work in a fresh feature branch of the isolated new clone; user explicitly authorizes deployment to GitHub. No additional design gate.

Verification: 8 model engines trained/predicted; held-out neural smoke tests; browser graph model training, subtab navigation and evaluation verified. Review findings fixed: whitespace numeric inputs; inference target schema; unknown diagnosis labels; overlap canonicalization; training DOM lifetime. No backend or LLM connection is represented as live.
