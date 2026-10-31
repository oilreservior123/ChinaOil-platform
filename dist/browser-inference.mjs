export function averagePathLength(n) {
  if (n <= 1) return 0;
  if (n === 2) return 1;
  return 2 * (Math.log(n - 1) + 0.5772156649015329) - 2 * (n - 1) / n;
}
export function isolationScore(model, values) {
  const x = model.features.map((name, i) => {
    let raw = Array.isArray(values) ? values[i] : values[name];
    const missing = raw === null || raw === undefined || !Number.isFinite(Number(raw));
    raw = missing ? model.imputer_medians[i] : Number(raw);
    return Math.fround((raw - model.robust_center[i]) / model.robust_scale[i]);
  });
  let total = 0;
  for (const tree of model.trees) {
    let node = 0, depth = 0;
    while (tree.children_left[node] !== tree.children_right[node]) {
      const feature = tree.feature_map[tree.feature[node]];
      node = x[feature] <= tree.threshold[node] ? tree.children_left[node] : tree.children_right[node];
      depth += 1;
    }
    total += depth + averagePathLength(tree.n_node_samples[node]);
  }
  const score = Math.pow(2, -(total / model.trees.length) / averagePathLength(model.max_samples)) + model.offset;
  return { score, flag: score >= model.threshold, threshold: model.threshold };
}
export function rotateScore(model, headId, relationId, tailId) {
  const hi = model.entity_ids.indexOf(headId), ri = model.relation_ids.indexOf(relationId), ti = model.entity_ids.indexOf(tailId);
  if (hi < 0 || ri < 0 || ti < 0) return null;
  const h = model.entity_embeddings[hi], t = model.entity_embeddings[ti], phase = model.relation_phases[ri], d = model.dimension;
  let distance = 0;
  for (let k = 0; k < d; k++) {
    const real = h[k] * Math.cos(phase[k]) - h[k + d] * Math.sin(phase[k]) - t[k];
    const imag = h[k] * Math.sin(phase[k]) + h[k + d] * Math.cos(phase[k]) - t[k + d];
    distance += Math.sqrt(real * real + imag * imag + 1e-10);
  }
  return model.gamma - distance;
}
