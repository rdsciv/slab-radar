import { signed } from '@/lib/format';

/** Breakout score rendered like a grading-slab label: the one loud element on the page. */
export function Slab({ score, label = 'BRK', large = false }: { score: number; label?: string; large?: boolean }) {
  return (
    <span className={`slab${large ? ' lg' : ''}${score < 0.5 ? ' cold' : ''}`} title="Breakout score (MODEL)">
      <span className="k">{label}</span>
      <span className="v">{signed(score, 2)}</span>
    </span>
  );
}

export function Prov({ p }: { p: 'OBSERVED' | 'MODEL' | 'MARKET_IMPLIED' }) {
  const short = { OBSERVED: 'obs', MODEL: 'model', MARKET_IMPLIED: 'mkt' }[p];
  return <span className={`prov ${p}`} title={p}>{short}</span>;
}
