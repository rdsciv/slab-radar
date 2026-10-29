import { num, pct } from '@/lib/format';

/** Per-week bars for one metric (server-rendered SVG). Highlighted weeks = top-10 radar finishes. */
export function WeekBars({ title, points, kind, highlight, note }: {
  title: string; points: { week: number; value: number | null; n?: string }[];
  kind: 'pct' | 'num'; highlight: Set<number>; note?: string;
}) {
  const W = 300, H = 112, padB = 18, padT = 18;
  const vals = points.map((p) => p.value ?? 0);
  const max = Math.max(...vals, kind === 'pct' ? 0.3 : 1);
  const bw = W / Math.max(points.length, 1);
  const fmt = (v: number | null) => (kind === 'pct' ? pct(v) : num(v));
  const label = `${title} by week: ` + points.map((p) => `week ${p.week} ${fmt(p.value)}`).join(', ');
  return (
    <figure className="chart" style={{ margin: 0 }}>
      <h3>{title}</h3>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={label}>
        {points.map((p, i) => {
          const h = p.value == null ? 0 : ((H - padB - padT) * p.value) / max;
          const x = i * bw + bw * 0.18, w = bw * 0.64, y = H - padB - h;
          const hot = highlight.has(p.week);
          return (
            <g key={p.week}>
              <rect x={x} y={y} width={w} height={Math.max(h, p.value == null ? 0 : 1)} rx={1.5}
                fill={hot ? 'var(--silver)' : '#4d6a61'} />
              <text x={x + w / 2} y={y - 4} textAnchor="middle" fontSize="11" fill="var(--chalk)"
                style={{ fontVariantNumeric: 'tabular-nums' }}>{p.value == null ? '—' : fmt(p.value)}</text>
              <text x={x + w / 2} y={H - 4} textAnchor="middle" fontSize="11" fill="var(--sage)">{p.week}</text>
            </g>
          );
        })}
      </svg>
      {note && <figcaption className="muted small">{note}</figcaption>}
    </figure>
  );
}
