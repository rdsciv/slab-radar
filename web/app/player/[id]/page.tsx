import Link from 'next/link';
import { cards, meta, player, playerIds, type GameRow } from '@/lib/data';
import { Slab, Prov } from '@/components/Slab';
import { WeekBars } from '@/components/WeekBars';
import { FLAG_TEXT } from '@/components/flags';
import { num, pct } from '@/lib/format';
import { CardSummary } from '@/components/CardSummary';

export const dynamicParams = false;
export function generateStaticParams() {
  return playerIds().map((id) => ({ id }));
}
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return { title: `${player(id).name} | Slab Radar` };
}

const sum = (g: GameRow[], k: keyof GameRow) => g.reduce((a, r) => a + ((r[k] as number) ?? 0), 0);
function share(g: GameRow[], n: keyof GameRow, d: keyof GameRow) {
  const den = sum(g, d);
  return { v: den > 0 ? sum(g, n) / den : null, n: `${sum(g, n)}/${den}` };
}

export default async function Player({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const p = player(id);
  const m = meta();
  const g = p.games;
  const last = p.radar.at(-1);
  const hot = new Set(p.radar.filter((r) => r.rank != null && r.rank <= 10).map((r) => r.week));
  const qb = p.position === 'QB';
  const ts = share(g, 'targets', 'team_targets');
  const snap = share(g, 'offense_snaps', 'team_offense_snaps');
  const carry = share(g, 'carries', 'team_carries');
  const rz = share(g, 'rz_opps', 'team_rz_opps');
  const xg = g.filter((r) => r.xfp != null);
  const pts = (k: keyof GameRow) => g.map((r) => ({ week: r.week, value: r[k] as number | null }));
  const c = cards(id);
  return (
    <>
      <div className="player-head">
        <div>
          <h1>{p.name}</h1>
          <div className="muted">{p.position}, {p.team}. {g.length} games in {p.season}.</div>
        </div>
        {last && (
          <div>
            <Slab score={last.score} label={`WK ${last.week}`} large />
            <div className="muted small" style={{ marginTop: 4 }}>
              {last.rank ? `Rank ${last.rank} that week` : 'Under the snap filter that week'}{last.badge === 'signal' ? ', signal' : last.badge === 'noise' ? ', noise?' : ''}
            </div>
          </div>
        )}
      </div>

      <div className="facts">
        {!qb && <Fact label="Target share, season" value={pct(ts.v)} n={ts.n} />}
        <Fact label="Snap share, season" value={pct(snap.v)} n={snap.n} />
        {(p.position === 'RB' || qb) && <Fact label="Carry share, season" value={pct(carry.v)} n={carry.n} />}
        <Fact label="Red-zone opportunity share" value={pct(rz.v)} n={rz.n} />
        {qb && <Fact label="Dropbacks per game" value={num(sum(g, 'dropbacks') / g.length)} n={`${sum(g, 'dropbacks')} in ${g.length} games`} />}
        <Fact label="xFP per game" value={num(xg.length ? sum(xg, 'xfp') / xg.length : null)} n={`${xg.length} games`} model />
      </div>

      <h2>Usage by week</h2>
      <p className="muted small">Highlighted weeks finished in the radar&apos;s top 10.</p>
      <div className="charts">
        {!qb && <WeekBars title="Target share" points={pts('ts')} kind="pct" highlight={hot} />}
        {!qb && <WeekBars title="Air-yards share" points={pts('ays')} kind="pct" highlight={hot} note="Denominator: team passer air yards (nflverse)" />}
        <WeekBars title="Snap share" points={pts('snap')} kind="pct" highlight={hot} />
        {(p.position === 'RB' || qb) && <WeekBars title="Carry share" points={pts('carry')} kind="pct" highlight={hot} />}
        {qb && <WeekBars title="Dropbacks" points={pts('dropbacks')} kind="num" highlight={hot} />}
        <WeekBars title="xFP (model)" points={pts('xfp')} kind="num" highlight={hot} note="nflverse ffopportunity expected PPR points" />
      </div>

      {p.radar.length > 0 && (
        <>
          <h2>Radar history</h2>
          <div className="table-scroll">
            <table className="grid">
              <thead><tr><th className="n">Week</th><th>Score</th><th className="n">Rank</th><th className="n">P(share rose)</th><th>Flags</th></tr></thead>
              <tbody>
                {[...p.radar].reverse().map((r) => (
                  <tr key={r.week}>
                    <td className="n"><Link href={r.week === m.latest_week ? '/' : `/week/${r.week}/`}>{r.week}</Link></td>
                    <td><Slab score={r.score} /></td>
                    <td className="n">{r.rank ?? <span className="muted" title="Under 25% snap share">—</span>}</td>
                    <td className="n">{pct(r.p_share_up)}{r.p_metric && <span className="sub">{r.p_metric === 'carry' ? 'carry' : 'target'} share, n={r.p_n}</span>}</td>
                    <td>
                      {r.badge === 'signal' && <span className="tag signal">Signal</span>}
                      {r.badge === 'noise' && <span className="tag noise">Noise?</span>}
                      {r.flags.map((f) => <span key={f} className={`tag${f === 'td_driven' ? ' td' : ''}`}>{FLAG_TEXT[f] ?? f}</span>)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="muted small">Rank among players with at least 25% snap share that week, the same ranking as the radar table.</p>
        </>
      )}

      <h2>Game log</h2>
      <div className="table-scroll">
        <table className="grid">
          <thead>
            <tr>
              <th className="n">Wk</th><th>Opp</th><th className="n">Snaps</th><th className="n">Tgt</th><th className="n">Rec</th>
              <th className="n">Rec yd</th><th className="n">Car</th><th className="n">Rush yd</th>
              {qb && <><th className="n">Dropbacks</th><th className="n">Pass yd</th></>}
              <th className="n">TD</th><th className="n">PPR</th><th className="n">xFP</th>
            </tr>
          </thead>
          <tbody>
            {[...g].reverse().map((r) => (
              <tr key={r.week}>
                <td className="n">{r.week}</td><td>{r.opponent_team}</td>
                <td className="n">{r.offense_snaps}/{r.team_offense_snaps}</td>
                <td className="n">{r.targets}/{r.team_targets}</td><td className="n">{r.receptions}</td>
                <td className="n">{r.receiving_yards}</td><td className="n">{r.carries}</td><td className="n">{r.rushing_yards}</td>
                {qb && <><td className="n">{r.dropbacks}</td><td className="n">{r.passing_yards}</td></>}
                <td className="n">{r.receiving_tds + r.rushing_tds + r.passing_tds}</td>
                <td className="n">{num(r.fantasy_points_ppr)}</td><td className="n">{num(r.xfp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Cards</h2>
      {c ? <CardSummary file={c} /> : (
        <p className="muted">No GemRate export loaded for {p.name}. Export the player page from GemRate and add it to the card data to see population and gem rates here.</p>
      )}
    </>
  );
}

function Fact({ label, value, n, model }: { label: string; value: string; n: string; model?: boolean }) {
  return (
    <div className="fact">
      <div className="label">{label}{model && <Prov p="MODEL" />}</div>
      <div className="value">{value}</div>
      <div className="n">n = {n}</div>
    </div>
  );
}
