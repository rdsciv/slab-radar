import type { Card } from '@/lib/data';
import { interval, pct, type Labeled } from '@/lib/format';
import { Prov } from './Slab';

export function gemLabeled(c: Card): Labeled | null {
  if (!c.gem) return null;
  return { value: c.gem.post_mean, provenance: 'MODEL', n: c.gem.n, lo: c.gem.ci95[0], hi: c.gem.ci95[1] };
}

/** Shrunk gem rate (MODEL) with its 95% interval as a bar; the raw rate (OBSERVED) is the amber tick. */
export function GemCell({ c }: { c: Card }) {
  const l = gemLabeled(c);
  if (!l || !c.gem) return <span className="muted">no slabs</span>;
  const x = (v: number) => `${Math.max(0, Math.min(100, v * 100))}%`;
  const thin = c.gem.n < 30;
  return (
    <span title={`Raw ${c.gems}/${c.total} = ${pct(c.gem.raw_rate)}; shrunk toward the ${c.gem.prior_level.replaceAll('_', ' ')} pool`}>
      <span className="ci" aria-hidden="true">
        <span className="band" style={{ left: x(l.lo!), width: `calc(${x(l.hi!)} - ${x(l.lo!)})` }} />
        <span className="mid" style={{ left: x(l.value!) }} />
        <span className="raw" style={{ left: `calc(${x(c.gem.raw_rate)} - 3px)` }} />
      </span>{' '}
      <b className="num">{pct(l.value)}</b><Prov p={l.provenance} />
      <span className="sub">{interval(l)}, n={l.n}{thin ? ', raw greyed' : `, raw ${pct(c.gem.raw_rate)}`}</span>
    </span>
  );
}
