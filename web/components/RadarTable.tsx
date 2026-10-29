'use client';
import Link from 'next/link';
import { useMemo, useState } from 'react';
import { Slab } from './Slab';
import { FLAG_TEXT } from './flags';
import { num, pct, signedPts } from '@/lib/format';

export interface RadarLine {
  id: string; name: string; pos: string; team: string; opp: string; score: number; qualifies: boolean;
  badge: 'signal' | 'noise' | null; flags: { flag: string; detail: string }[];
  ts: number | null; tsNum: number; tsDen: number; tsDelta: number | null;
  ays: number | null; snap: number | null; snapNum: number; snapDen: number;
  carry: number | null; carryNum: number; carryDen: number;
  xfp: number | null; xfpBase: number | null; dropbacks: number | null;
  p: { p: number; window: number; metric: string; n: number } | null;
}

const POS = ['All', 'QB', 'RB', 'WR', 'TE'] as const;
type SortKey = 'score' | 'ts' | 'tsDelta' | 'xfp' | 'p';

export function RadarTable({ rows }: { rows: RadarLine[] }) {
  const [pos, setPos] = useState<(typeof POS)[number]>('All');
  const [all, setAll] = useState(false);
  const [sort, setSort] = useState<SortKey>('score');
  const shown = useMemo(() => {
    const val = (r: RadarLine) => (sort === 'p' ? r.p?.p : r[sort]) ?? -Infinity;
    return rows
      .filter((r) => (all || r.qualifies) && (pos === 'All' || r.pos === pos))
      .sort((a, b) => val(b) - val(a));
  }, [rows, pos, all, sort]);
  const head = (k: SortKey, text: string, cls = 'n') => (
    <th className={cls} aria-sort={sort === k ? 'descending' : 'none'}>
      <button onClick={() => setSort(k)}>{text}{sort === k ? ' ▾' : ''}</button>
    </th>
  );
  return (
    <>
      <div className="controls">
        <div className="seg" role="group" aria-label="Position">
          {POS.map((p) => (
            <button key={p} aria-pressed={pos === p} onClick={() => setPos(p)}>{p}</button>
          ))}
        </div>
        <label className="check">
          <input type="checkbox" checked={all} onChange={(e) => setAll(e.target.checked)} />
          Include players under 25% snap share
        </label>
        <span className="muted small">{shown.length} players</span>
      </div>
      <div className="table-scroll">
        <table className="grid">
          <thead>
            <tr>
              <th className="n">#</th>
              <th>Player</th>
              {head('score', 'Score', '')}
              {head('ts', 'Target share')}
              {head('tsDelta', 'vs baseline')}
              <th className="n hide-sm">Air yards</th>
              <th className="n">Snaps</th>
              <th className="n hide-sm">Carries</th>
              {head('xfp', 'xFP')}
              {head('p', 'P(share rose)')}
              <th>Flags</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((r, i) => (
              <tr key={r.id}>
                <td className="n muted">{i + 1}</td>
                <td>
                  <Link href={`/player/${r.id}/`} className="who">{r.name}</Link>
                  <span className="sub">{r.pos}, {r.team} vs {r.opp}</span>
                </td>
                <td><Slab score={r.score} /></td>
                <td className="n">{pct(r.ts)}<span className="sub">{r.tsNum}/{r.tsDen}</span></td>
                <td className="n">{signedPts(r.tsDelta)}</td>
                <td className="n hide-sm">{pct(r.ays)}</td>
                <td className="n">{pct(r.snap)}<span className="sub">{r.snapNum}/{r.snapDen}</span></td>
                <td className="n hide-sm">{pct(r.carry)}<span className="sub">{r.carryNum}/{r.carryDen}</span></td>
                <td className="n">{num(r.xfp)}<span className="sub">base {num(r.xfpBase)}</span></td>
                <td className="n">
                  {r.p ? <>{pct(r.p.p)}<span className="sub">last {r.p.window} wk, n={r.p.n}</span></> : <span className="muted">—</span>}
                </td>
                <td>
                  {r.badge === 'signal' && <span className="tag signal">Signal</span>}
                  {r.badge === 'noise' && <span className="tag noise">Noise?</span>}
                  {r.flags.map((f, j) => (
                    <span key={j} className={`tag${f.flag === 'td_driven' ? ' td' : ''}`} title={f.detail}>{FLAG_TEXT[f.flag] ?? f.flag}</span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
