'use client';
import { useMemo, useState } from 'react';
import type { Card } from '@/lib/data';
import { CardRows } from './CardSummary';

type Sort = 'total' | 'gem_high' | 'gem_low';

export function CardCatalog({ cards }: { cards: Card[] }) {
  const [q, setQ] = useState('');
  const [year, setYear] = useState('all');
  const [college, setCollege] = useState(false);
  const [sort, setSort] = useState<Sort>('total');
  const [limit, setLimit] = useState(100);
  const years = useMemo(() => [...new Set(cards.map((c) => c.year))].sort((a, b) => b - a), [cards]);
  const shown = useMemo(() => {
    const words = q.toLowerCase().split(/\s+/).filter(Boolean);
    const hay = (c: Card) => `${c.year} ${c.set} ${c.parallel} ${c.card_no} ${c.name}`.toLowerCase();
    const key: Record<Sort, (c: Card) => number> = {
      total: (c) => c.total,
      gem_high: (c) => c.gem?.post_mean ?? -1,
      gem_low: (c) => (c.gem ? -c.gem.post_mean : -2),
    };
    return cards
      .filter((c) => (year === 'all' || String(c.year) === year) && (college || c.pre_nfl !== true)
        && words.every((w) => hay(c).includes(w)))
      .sort((a, b) => key[sort](b) - key[sort](a));
  }, [cards, q, year, college, sort]);
  return (
    <>
      <div className="controls">
        <input type="search" placeholder="prizm silver 327" value={q} aria-label="Search cards"
          onChange={(e) => { setQ(e.target.value); setLimit(100); }} />
        <select value={year} onChange={(e) => setYear(e.target.value)} aria-label="Year">
          <option value="all">All years</option>
          {years.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value as Sort)} aria-label="Sort">
          <option value="total">Most graded</option>
          <option value="gem_high">Highest gem rate</option>
          <option value="gem_low">Lowest gem rate</option>
        </select>
        <label className="check"><input type="checkbox" checked={college} onChange={(e) => setCollege(e.target.checked)} /> Include college / pre-NFL</label>
        <span className="muted small">{shown.length.toLocaleString('en-US')} cards</span>
      </div>
      <CardRows cards={shown.slice(0, limit)} />
      {shown.length > limit && (
        <p><button className="seg" style={{ padding: '6px 12px', color: 'var(--chalk)', background: 'none', cursor: 'pointer' }}
          onClick={() => setLimit(limit + 200)}>Show 200 more</button></p>
      )}
    </>
  );
}
