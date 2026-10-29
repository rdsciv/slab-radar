import Link from 'next/link';
import type { CardsFile } from '@/lib/data';
import { GemCell } from './GemCell';

export function CardSummary({ file }: { file: CardsFile }) {
  const cs = file.cards;
  const slabs = cs.reduce((a, c) => a + c.total, 0);
  const top = [...cs].filter((c) => !c.one_of_one).sort((a, b) => b.total - a.total).slice(0, 12);
  return (
    <>
      <p className="lede">
        {cs.length.toLocaleString('en-US')} cards and {slabs.toLocaleString('en-US')} graded slabs in the GemRate export.
        The 12 most-graded are below; the <Link href={`/cards/${file.gsis_id}/`}>full catalog</Link> has filters.
      </p>
      <CardRows cards={top} />
      <p className="note small">
        Gem rates come from the GemRate export, and whether its counts are PSA-only or all graders is not yet confirmed.
        The shrunk rate pulls thin cards toward similar cards (same product, then same year) so a 3-for-4 card doesn&apos;t
        read as 75%. No sale prices yet: no comp source has been approved.
      </p>
    </>
  );
}

export function CardRows({ cards }: { cards: CardsFile['cards'] }) {
  return (
    <div className="table-scroll">
      <table className="grid">
        <thead>
          <tr><th className="n">Year</th><th>Card</th><th className="n">#</th><th className="n">Graded</th><th>Gem rate (shrunk, 95% interval)</th><th>Notes</th></tr>
        </thead>
        <tbody>
          {cards.map((c) => (
            <tr key={c.card_key}>
              <td className="n">{c.year}</td>
              <td>
                <span className="who">{c.set}</span>
                <span className="sub">{c.parallel}{c.name.includes('/') ? `, ${c.name}` : ''}</span>
              </td>
              <td className="n">{c.card_no || '—'}</td>
              <td className="n">{c.total.toLocaleString('en-US')}<span className="sub">{c.gems.toLocaleString('en-US')} gem</span></td>
              <td><GemCell c={c} /></td>
              <td>
                {c.pre_nfl === true && <span className="tag">College / pre-NFL</span>}
                {c.pre_nfl === null && <span className="tag">League status unknown</span>}
                {c.one_of_one && <span className="tag">1/1, not in priors</span>}
                {c.license?.status === 'unlicensed' && <span className="tag">Unlicensed</span>}
                {c.flags.includes('no_gemrate_id') && <span className="tag" title="No GemRate id in the export; keyed by name">No GemRate id</span>}
                {c.flags.includes('gemrate_id_mismatch') && <span className="tag" title="Card Ladder id differs from the universal id">Id mismatch</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
