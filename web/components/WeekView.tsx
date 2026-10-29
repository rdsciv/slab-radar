import Link from 'next/link';
import { meta, radarWeek, type RadarRow } from '@/lib/data';
import { RadarTable, type RadarLine } from './RadarTable';

function line(r: RadarRow): RadarLine {
  const m = r.metrics;
  return {
    id: r.gsis_id, name: r.name, pos: r.position, team: r.team, opp: r.opponent, score: r.score,
    qualifies: r.passes_min_snaps, badge: r.badge, flags: r.flags,
    ts: m.ts.last1, tsNum: m.ts.last1_num, tsDen: m.ts.last1_den,
    tsDelta: m.ts.last1 != null && m.ts.base1 != null ? m.ts.last1 - m.ts.base1 : null,
    ays: m.ays.last1, snap: m.snap.last1, snapNum: m.snap.last1_num, snapDen: m.snap.last1_den,
    carry: m.carry.last1, carryNum: m.carry.last1_num, carryDen: m.carry.last1_den,
    xfp: m.xfp.last1, xfpBase: m.xfp.base1, dropbacks: m.dropbacks.last1,
    p: r.p_share_up ? { p: r.p_share_up.p, window: r.p_share_up.window, metric: r.p_share_up.metric, n: r.p_share_up.n_recent } : null,
  };
}

export function WeekView({ week }: { week: number }) {
  const m = meta();
  const data = radarWeek(m.season, week);
  return (
    <>
      <h1>Breakout radar, {m.season} week {week}</h1>
      <p className="lede">
        Players whose usage jumped this week, ranked by breakout score. Shares are this week&apos;s counts over the team&apos;s
        (n shown under each). &ldquo;vs baseline&rdquo; compares with the player&apos;s earlier games this season. Score, xFP and
        P(share rose) are model outputs; how they are built is on the <Link href="/methodology/">methodology page</Link>.
      </p>
      <nav className="weeks" aria-label="Week">
        {m.weeks.map((w) => (
          <Link key={w} href={w === m.latest_week ? '/' : `/week/${w}/`} aria-current={w === week ? 'page' : undefined}>
            {w}
          </Link>
        ))}
      </nav>
      <div style={{ height: 12 }} />
      <RadarTable rows={data.rows.map(line)} />
    </>
  );
}
