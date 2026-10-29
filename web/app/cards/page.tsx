import Link from 'next/link';
import { cardsIndex } from '@/lib/data';

export default function CardsIndex() {
  const idx = cardsIndex();
  return (
    <>
      <h1>Cards</h1>
      <p className="lede">
        Population and gem rates from GemRate exports, one player per export. Sale prices arrive once a comp source is approved.
      </p>
      {idx.length === 0 ? <p className="muted">No GemRate exports loaded yet.</p> : (
        <div className="table-scroll">
          <table className="grid">
            <thead><tr><th>Player</th><th className="n">Cards</th><th className="n">Graded slabs</th></tr></thead>
            <tbody>
              {idx.map((p) => (
                <tr key={p.gsis_id}>
                  <td><Link className="who" href={`/cards/${p.gsis_id}/`}>{p.player}</Link> <Link className="small" href={`/player/${p.gsis_id}/`}>usage</Link></td>
                  <td className="n">{p.n_cards.toLocaleString('en-US')}</td>
                  <td className="n">{p.n_slabs.toLocaleString('en-US')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
