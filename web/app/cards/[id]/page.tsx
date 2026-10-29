import Link from 'next/link';
import { cards, cardsIndex } from '@/lib/data';
import { CardCatalog } from '@/components/CardCatalog';

export const dynamicParams = false;
export function generateStaticParams() {
  return cardsIndex().map((p) => ({ id: p.gsis_id }));
}

export default async function Catalog({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const f = cards(id)!;
  return (
    <>
      <h1>{f.player} cards</h1>
      <p className="lede">
        Every card in the GemRate export with graded population and gem rate. The bar is the shrunk rate&apos;s 95% interval,
        the white line its estimate, the amber tick the raw rate. <Link href={`/player/${id}/`}>Usage and radar history</Link>.
      </p>
      <CardCatalog cards={f.cards} />
    </>
  );
}
