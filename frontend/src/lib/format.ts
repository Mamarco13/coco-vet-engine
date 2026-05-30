export function clamp01(value: number) {
  return Math.min(1, Math.max(0, value));
}

export function formatPercent(value: number) {
  return `${Math.round(clamp01(value) * 100)}%`;
}

export function formatScore(value: number) {
  return clamp01(value).toFixed(2);
}
