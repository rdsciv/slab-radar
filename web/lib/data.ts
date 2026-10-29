// Build-time readers for the ETL's JSON (web/public/data). Pages are statically exported; nothing is fetched at runtime.
import fs from 'node:fs';
import path from 'node:path';

const DATA = path.join(process.cwd(), 'public', 'data');
const read = <T,>(rel: string): T => JSON.parse(fs.readFileSync(path.join(DATA, rel), 'utf8'));
const exists = (rel: string) => fs.existsSync(path.join(DATA, rel));

export type MetricKey = 'ts' | 'ays' | 'snap' | 'carry' | 'rz' | 'xfp' | 'dropbacks' | 'designed_rush';

export interface MetricWindow {
  last1: number | null; last1_num: number; last1_den: number; base1: number | null; base1_games: number;
  z_self1: number | null; z_pos1: number | null;
  last3: number | null; last3_num: number; last3_den: number; base3: number | null; base3_games: number;
  z_self3: number | null; z_pos3: number | null;
}

export interface ShareUp {
  p: number; recent_mean: number; recent_ci80: [number, number]; base_mean: number; base_ci80: [number, number];
  n_recent: number; n_base: number; metric: 'ts' | 'carry'; window: 1 | 3;
}

export interface Flag { flag: 'td_driven' | 'team_change' | 'qb_change' | 'vacated_opportunity'; detail: string }

export interface RadarRow {
  gsis_id: string; name: string; position: string; team: string; opponent: string; games: number;
  passes_min_snaps: boolean; fp_ppr: number;
  metrics: Record<MetricKey, MetricWindow> & { wopr: { last1: number | null; last3: number | null } };
  z: { last1: Partial<Record<MetricKey, number | null>>; last3: Partial<Record<MetricKey, number | null>> };
  contrib: Partial<Record<MetricKey, number>>; last1_term: number;
  score: number; flags: Flag[]; td_driven: boolean; p_share_up: ShareUp | null; badge: 'signal' | 'noise' | null;
}

export interface Meta {
  generated_ts: string; season: number; weeks: number[]; latest_week: number;
  weights: { version: string; weights: Record<string, Record<string, number>>; flags: Record<string, number>; p_td: number;
             nu: number; min_snap_share: number; signal_p: number; noise_p: number };
  priors: Record<string, [number, number] | null>;
  warnings: { kind: string; week: number; player: string; team: string; offense_snaps: number }[];
  nflreadpy: string;
}

export interface GameRow {
  week: number; team: string; opponent_team: string; targets: number; team_targets: number;
  carries: number; team_carries: number; offense_snaps: number; team_offense_snaps: number;
  rz_opps: number; team_rz_opps: number; dropbacks: number; designed_rushes: number;
  receptions: number; receiving_yards: number; rushing_yards: number; passing_yards: number;
  receiving_tds: number; rushing_tds: number; passing_tds: number; fantasy_points_ppr: number;
  xfp: number | null; ts: number | null; ays: number | null; snap: number | null; carry: number | null; rz: number | null;
}

export interface PlayerFile {
  gsis_id: string; name: string; position: string; team: string; season: number; games: GameRow[];
  radar: { week: number; score: number; rank: number | null; badge: string | null; flags: string[]; p_share_up: number | null }[];
}

export interface Gem {
  raw_rate: number; n: number; post_mean: number; ci95: [number, number]; prior_level: string;
  prior_mu: number; prior_kappa: number; scope: string;
}

export interface Card {
  card_key: string; year: number; set: string; name: string; parallel: string; card_no: string;
  gems: number; total: number; one_of_one: boolean; flags: string[]; pre_nfl: boolean | null;
  license: { status: string; label: string; source: string; tag: string } | null; gem: Gem | null;
}

export interface CardsFile { gsis_id: string; player: string; source: string; exported: string; cards: Card[] }

export const meta = (): Meta => read<Meta>('meta.json');
export const radarWeek = (season: number, week: number) =>
  read<{ season: number; week: number; rows: RadarRow[] }>(`radar/${season}-${String(week).padStart(2, '0')}.json`);
export const playerIds = (): string[] =>
  fs.readdirSync(path.join(DATA, 'players')).filter((f) => f.endsWith('.json')).map((f) => f.replace('.json', ''));
export const player = (id: string) => read<PlayerFile>(`players/${id}.json`);
export const cardsIndex = (): { gsis_id: string; player: string; n_cards: number; n_slabs: number }[] =>
  exists('cards/index.json') ? read('cards/index.json') : [];
export const cards = (id: string): CardsFile | null => (exists(`cards/${id}.json`) ? read(`cards/${id}.json`) : null);
