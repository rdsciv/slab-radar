import { WeekView } from '@/components/WeekView';
import { meta } from '@/lib/data';

export default function Home() {
  return <WeekView week={meta().latest_week} />;
}
