import { WeekView } from '@/components/WeekView';
import { meta } from '@/lib/data';

export const dynamicParams = false;
export function generateStaticParams() {
  const weeks = meta().weeks;
  // Static export needs at least one path; 'none' renders the no-complete-week message.
  return weeks.length ? weeks.map((w) => ({ week: String(w) })) : [{ week: 'none' }];
}

export default async function Week({ params }: { params: Promise<{ week: string }> }) {
  const { week } = await params;
  return <WeekView week={Number(week)} />;
}
