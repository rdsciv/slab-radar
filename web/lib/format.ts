// Display rules (CLAUDE.md): rates whole percent with n beside them; prices whole dollars ($5 steps above $500).
// Half-up rounding (GemRate's convention; JS Math.round is half-up only for positives, so handle sign explicitly).

export type Provenance = 'OBSERVED' | 'MODEL' | 'MARKET_IMPLIED';

/** Every card-side number must carry its label, sample size and interval — the type makes omission a compile error. */
export interface Labeled {
  value: number | null;
  provenance: Provenance;
  n: number;
  lo: number | null;
  hi: number | null;
}

export function roundHalfUp(x: number, digits = 0): number {
  const f = 10 ** digits;
  const r = Math.sign(x) * Math.floor(Math.abs(x) * f + 0.5 + 1e-9) / f;
  return r === 0 ? 0 : r; // no "-0"
}

export function pct(x: number | null | undefined): string {
  return x == null ? '—' : `${roundHalfUp(x * 100)}%`;
}

export function signedPts(x: number | null | undefined): string {
  if (x == null) return '—';
  const v = roundHalfUp(x * 100);
  return `${v > 0 ? '+' : ''}${v} pts`;
}

export function num(x: number | null | undefined, digits = 1): string {
  return x == null ? '—' : roundHalfUp(x, digits).toFixed(digits);
}

export function signed(x: number | null | undefined, digits = 2): string {
  if (x == null) return '—';
  const v = roundHalfUp(x, digits);
  return `${v > 0 ? '+' : ''}${v.toFixed(digits)}`;
}

export function dollars(x: number | null | undefined): string {
  if (x == null) return '—';
  const v = x > 500 ? roundHalfUp(x / 5) * 5 : roundHalfUp(x);
  return `$${v.toLocaleString('en-US')}`;
}

export function interval(l: Labeled, fmt: (v: number) => string = (v) => pct(v)): string {
  return l.lo == null || l.hi == null ? 'no interval' : `${fmt(l.lo)}–${fmt(l.hi)}`;
}
