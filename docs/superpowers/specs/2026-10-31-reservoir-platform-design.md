# ChinaOil GeoTwin platform design

Goal: a polished Chinese browser platform covering every function in the supplied PPT pages1–25. Only the user's listed cleaning, knowledge, master/association, DFN/EDFM/DAG, production anomaly and decline-validation functions are implemented; others remain clearly identified entry buttons.

Architecture: buildless private Sites application, modular browser JavaScript, CSS and Canvas/SVG rendering; train heavy models offline in Python and include truthful frozen experiment results, provenance, parameters, checkpoints and scripts. Browser-native implementations run Arps fitting, property-graph queries, historical retrieval, rule quality control and any supported exported model inference. Frozen-model buttons replay verified outputs and are explicitly labelled; never claim server training or inference for those.

Design: dark scientific workbench, restrained teal/amber accents, readable Chinese interface, animated reservoir visualization, interactive graph and fracture diagrams, clear hierarchy. Navigation: overview, cleaning, knowledge graph, wells/groups, dynamics, fracture/simulation, workflow, model lab, PPT function catalogue. Responsive layouts, reduced-motion support, keyboard controls, chart tooltips, transparent data origin and model status.

Data: authoritative current attached archive is truncated at its final preview image. Recover76 complete local-header entries only after CRC and size checks. Core source data intact. Never treat FORCE GROUP as development well-group. Volve, FORCE and SPE9 retain separate namespaces. Supplemental well-layer/group and physical cases explicitly labelled generated or public benchmark, not original field truth.

Model scope: original requested model names retained with exact implementation status and compact-reproduction qualifier where necessary. Train/validation/test counts and ratios, actual evaluation metrics and dataset examples visible per model. No fabricated accuracy or causal diagnosis. Physical simulators present numerical residual, conservation error, validation reference rather than invented classification metrics.

Inputs/actions: source well selection, period, feature, quality-rule settings, model sample selector, knowledge query, graph filters, hierarchy drilldown, decline fitting/horizon settings, simulated-case selection/playback, DAG start/pause/reset, download experiment/result and dataset samples. No real review/permission/dispatch/business actions beyond declared scope.

Source of requirements: staging/ppt_pages_1_25.json and audit coverage JSON. Page-by-page catalogue includes source page, function, implementation status and destination. Preserve all 44-labelled catalogue assertions but record actual detailed list count if inconsistent.

Deployment: private owner Site by default per Sites workflow. No GitHub push to user's external repository requested in this message; Site's managed source repository used.
