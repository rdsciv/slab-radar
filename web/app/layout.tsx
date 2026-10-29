import type { Metadata } from 'next';
import Link from 'next/link';
import { Barlow_Condensed, Source_Sans_3 } from 'next/font/google';
import { meta } from '@/lib/data';
import './globals.css';

const barlow = Barlow_Condensed({ subsets: ['latin'], weight: ['500', '600', '700'], variable: '--font-barlow' });
const source = Source_Sans_3({ subsets: ['latin'], variable: '--font-source' });

export const metadata: Metadata = {
  title: 'Slab Radar',
  description: 'Weekly NFL usage breakouts next to card population and gem rates.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const m = meta();
  return (
    <html lang="en" className={`${barlow.variable} ${source.variable}`}>
      <body>
        <header className="site">
          <div className="wrap">
            <Link href="/" className="brand">Slab Radar</Link>
            <nav className="site" aria-label="Main">
              <Link href="/">This week</Link>
              <Link href="/cards/">Cards</Link>
              <Link href="/methodology/">Methodology</Link>
            </nav>
          </div>
        </header>
        <main><div className="wrap">{children}</div></main>
        <footer className="site">
          <div className="wrap">
            Personal research tool — not financial advice. NFL data from nflverse (nflreadpy {m.nflreadpy}), {m.season} weeks{' '}
            {m.weeks[0]}–{m.latest_week}, built {m.generated_ts.replace('T', ' ').replace('+00:00', ' UTC')}.
            No sale prices yet: no comp source has been approved.
          </div>
        </footer>
      </body>
    </html>
  );
}
