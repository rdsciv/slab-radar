import { WeekView } from '@/components/WeekView';
import { meta } from '@/lib/data';

export const dynamicParams = false;
export function generateStaticParams() {
  return meta().weeks.map((w) => ({ week: String(w) }));
}

export default async function Week({ params }: { params: Promise<{ week: string }> }) {
  const { week } = await params;
  return <WeekView week={Number(week)} />;
}
