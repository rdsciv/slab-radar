import { meta } from '@/lib/data';
import { Prov } from '@/components/Slab';

const METRIC_NAMES: Record<string, string> = {
  ts: 'Target share', ays: 'Air-yards share', snap: 'Snap share', carry: 'Carry share', rz: 'Red-zone share',
  xfp: 'xFP', dropbacks: 'Dropbacks', designed_rush: 'Designed rushes', last1: 'Last-week term',
};

export default function Methodology() {
  const m = meta();
  const w = m.weights;
  const metrics = ['ts', 'ays', 'snap', 'carry', 'rz', 'xfp', 'dropbacks', 'designed_rush', 'last1'];
  return (
    <div className="prose">
      <h1>Methodology</h1>
      <p className="lede">
        Every number on this site is one of three kinds: <b>observed</b> <Prov p="OBSERVED" /> (counted from a source),{' '}
        <b>model</b> <Prov p="MODEL" /> (an estimate with its assumptions listed here), or <b>market-implied</b>{' '}
        <Prov p="MARKET_IMPLIED" /> (backed out of prices; none yet). Rates are whole percent with n beside them.
      </p>

      <h2>Usage metrics</h2>
      <p>
        All NFL inputs are recorded data from nflverse: weekly player stats, play-by-play, PFR snap counts and the
        ffopportunity model. Routes, TPRR and YPRR are not used: nflverse has no in-season route data, and estimates of them
        are excluded on purpose.
      </p>
      <ul>
        <li><b>Target share</b> = targets / team targets. Matches nflverse <code>target_share</code> exactly (tested).</li>
        <li><b>Air-yards share</b> = receiving air yards / team <i>passer</i> air yards, nflverse&apos;s denominator. Matches nflverse <code>air_yards_share</code> exactly (tested).</li>
        <li><b>WOPR</b> = 1.5 × target share + 0.7 × air-yards share. Shown, not weighted separately, since it repeats both inputs.</li>
        <li><b>Snap share</b> = offensive snaps / team offensive snaps (PFR). Snap rows are matched to players through nflverse&apos;s PFR id map; unmatched rows are listed below, and those players stay on the radar with snap share unknown.</li>
        <li><b>Carry share</b> = carries / team carries.</li>
        <li><b>Red-zone share</b> = (red-zone targets + carries) / team red-zone targets + carries, inside the opponent 20 (<code>yardline_100 ≤ 20</code>).</li>
        <li><b>Dropbacks</b> count pass attempts (including spikes), sacks and scrambles. <b>Designed rushes</b> are QB runs that are not scrambles; kneel-downs are excluded.</li>
        <li><b>xFP</b> <Prov p="MODEL" /> is nflverse ffopportunity&apos;s expected PPR points, an nflverse model output. A game with snaps but no targets, carries or attempts has no ffopportunity row and counts as 0.</li>
      </ul>
      <p>
        Play-by-play counts use the standard offensive-play filter (pass or run, with EPA and a possession team, regular
        season); two-point tries are excluded. A window&apos;s rate is the sum of its numerators over the sum of its denominators
        across the player&apos;s games with at least one offensive snap. Byes and inactive weeks are skipped, not counted as zeros.
      </p>

      <h2>Breakout score <Prov p="MODEL" /></h2>
      <p>
        For each metric the radar compares the last game and the last three games with the player&apos;s earlier games this
        season (at least two needed), and with other players at the position that week.
      </p>
      <ul>
        <li><b>Self z</b> = change vs baseline / (sd × √(1/k + 1/n<sub>base</sub>)), where sd is the player&apos;s game-to-game sd shrunk toward the position&apos;s (ν = {w.nu} pseudo-games).</li>
        <li><b>Position z</b> = (value − position median) / (1.4826 × MAD), among players with at least {Math.round(w.min_snap_share * 100)}% snap share in that window.</li>
        <li>Each metric&apos;s z is the average of the two, clipped to ±3. The score is the weighted sum over the last three games, plus a smaller last-game term that uses the same weights rescaled.</li>
        <li>Flags add a fixed amount once per flag type: {Object.entries(w.flags).map(([k, v]) => `${k.replaceAll('_', ' ')} ${v >= 0 ? '+' : ''}${v}`).join(', ')}. TD-driven weeks subtract {w.p_td}.</li>
      </ul>
      <div className="table-scroll">
        <table className="grid">
          <thead><tr><th>Position</th>{metrics.map((k) => <th key={k} className="n">{METRIC_NAMES[k]}</th>)}</tr></thead>
          <tbody>
            {Object.entries(w.weights).map(([pg, ws]) => (
              <tr key={pg}><td>{pg}</td>{metrics.map((k) => <td key={k} className="n">{ws[k] != null ? ws[k].toFixed(2) : '—'}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted small">Weights version {w.version}. These are starting values; a backtest against later xFP has not been run yet.</p>

      <h2>P(share rose) <Prov p="MODEL" /></h2>
      <p>
        Targets (carries for running backs) are treated as binomial draws from the team&apos;s total. Recent and baseline shares
        get a Beta prior fitted by method of moments to last season&apos;s per-player shares (players with 8+ games), and the
        probability that the recent share is higher is estimated from 20,000 seeded draws. It uses the last three games when
        two earlier games exist, otherwise the last game. Signal: P ≥ {Math.round(w.signal_p * 100)}% with snap share not
        falling. Noise?: P &lt; {Math.round(w.noise_p * 100)}%.
      </p>
      <div className="table-scroll">
        <table className="grid">
          <thead><tr><th>Prior</th><th className="n">α</th><th className="n">β</th><th className="n">Mean</th></tr></thead>
          <tbody>
            {Object.entries(m.priors).map(([k, v]) => (
              <tr key={k}><td>{k.replace(':ts', ' target share').replace(':carry', ' carry share')}</td>
                <td className="n">{v ? v[0].toFixed(2) : '—'}</td><td className="n">{v ? v[1].toFixed(2) : '—'}</td>
                <td className="n">{v ? `${Math.round((100 * v[0]) / (v[0] + v[1]))}%` : '—'}</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Flags</h2>
      <ul>
        <li><b>TD-driven</b>: PPR points beat xFP by at least max(6, 1.5 × the position&apos;s sd of that gap) while xFP itself did not jump (self z &lt; 1).</li>
        <li><b>Teammate out</b>: a teammate at the same position who played the team&apos;s previous game, with at least 15% target share (carry share for RBs) over 2+ games, has no snaps this week. Only the first missed game is flagged. The injury-report status is shown when listed.</li>
        <li><b>New starting QB</b>: the team&apos;s most-dropbacks QB changed from the previous game.</li>
        <li><b>New team</b>: the player&apos;s team changed from his previous game.</li>
      </ul>
      <p className="muted small">Depth-chart promotions are not flagged yet: nflverse depth charts since 2025 are timestamped snapshots without a week column.</p>

      <h2>Gem rates <Prov p="MODEL" /></h2>
      <p>
        Counts come from GemRate player exports. The site recomputes each rate from the counts and never uses GemRate&apos;s
        rounded string. Whether the export counts PSA only or all graders is not confirmed yet, so it is labeled
        &ldquo;scope unconfirmed&rdquo; rather than &ldquo;PSA 10 rate&rdquo;.
      </p>
      <p>
        Each card&apos;s rate is shrunk with a hierarchical beta-binomial model. Cards are pooled by year, product and parallel,
        then by year and product, then by year, then all cards. A pool is used only with 3+ cards and 100+ slabs; otherwise its
        parent&apos;s fit applies, and the card says which level it used. Each level&apos;s mean and concentration are fitted by
        maximum marginal likelihood, nudged toward the parent mean. Intervals are 95% equal-tailed; the raw rate gets an exact (Clopper–Pearson) interval and is greyed under 30 slabs. 1/1s stay in the catalog
        but are left out of every pool.
      </p>
      <p>
        Card ids: GemRate&apos;s universal id when present, otherwise the PSA-scoped id from the export&apos;s Card Ladder links,
        otherwise a hash of year, set, name, parallel and card number. The middle step is pending approval: the universal
        link reads &ldquo;None&rdquo; on 1,114 of the 1,877 rows in the current export, including Prizm Silver #327.
        College and pre-NFL products come from an explicit product list, never from the manufacturer. Rookie status is never
        inferred from the year.
      </p>

      <h2>Not built yet</h2>
      <ul>
        <li>Sale prices, multiples, trends and price lag: they wait on an approved comp source.</li>
        <li>Cross-grade estimates, gem killers and strategy cards: later milestones.</li>
        <li>Prior-season baseline for players with fewer than two earlier games, and the breakout-score backtest.</li>
      </ul>

      <h2>Data quality this build</h2>
      {m.warnings.length === 0 ? <p className="muted">No warnings.</p> : (
        <>
          <p>{m.warnings.length} snap-count rows could not be matched to an nflverse player id and are left out of snap share (the players stay on the radar):</p>
          <div className="table-scroll">
            <table className="grid">
              <thead><tr><th className="n">Week</th><th>Player (PFR)</th><th>Team</th><th className="n">Snaps</th></tr></thead>
              <tbody>{m.warnings.map((x, i) => <tr key={i}><td className="n">{x.week}</td><td>{x.player}</td><td>{x.team}</td><td className="n">{x.offense_snaps}</td></tr>)}</tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
