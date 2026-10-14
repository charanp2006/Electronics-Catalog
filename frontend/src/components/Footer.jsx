import { Link } from 'react-router-dom'
import Marquee from './ui/Marquee'

const YEAR = new Date().getFullYear()

const COLS = [
  {
    title: 'catalog',
    links: [
      { to: '/products', label: 'all units' },
      { to: '/products?category=smartphones', label: 'smartphones' },
      { to: '/products?category=laptops', label: 'laptops' },
      { to: '/products?category=audio', label: 'audio' },
    ],
  },
  {
    title: 'operator',
    links: [
      { to: '/account', label: 'profile' },
      { to: '/orders', label: 'order log' },
      { to: '/wishlist', label: 'saved units' },
      { to: '/compare', label: 'compare matrix' },
    ],
  },
]

export default function Footer() {
  return (
    <footer className="border-t border-line bg-panel/40">
      <Marquee
        items={['ELECTROHUB', 'NOSQL EDITION', 'FASTAPI', 'MONGODB', 'REACT', 'PYMONGO', 'VITE']}
        speed={30}
        className="border-b border-line py-2 font-display text-xl tracking-[0.3em] text-dim uppercase"
      />

      <div className="mx-auto grid max-w-[1400px] gap-10 px-4 py-10 sm:grid-cols-2 lg:grid-cols-4">
        <div className="sm:col-span-2">
          <div className="flex items-baseline gap-1">
            <span className="font-display text-3xl leading-none text-phos">ELECTROHUB</span>
            <span className="blink text-phos">_</span>
          </div>
          <p className="mt-3 max-w-sm text-xs leading-relaxed text-dim">
            An electronics catalog rendered as a lab terminal. Documents served straight from
            MongoDB, assembled for the ABA NoSQL project.
          </p>
          <p className="mt-4 text-[10px] tracking-[0.2em] text-dim uppercase">
            <span className="text-sig">●</span> all systems nominal
          </p>
        </div>

        {COLS.map((col) => (
          <div key={col.title}>
            <p className="label mb-3 text-phos">{col.title}</p>
            <ul className="space-y-2">
              {col.links.map((l) => (
                <li key={l.label}>
                  <Link
                    to={l.to}
                    className="link-underline text-xs text-dim transition hover:text-ink"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="border-t border-line">
        <div className="mx-auto flex max-w-[1400px] flex-wrap items-center justify-between gap-2 px-4 py-4 text-[10px] tracking-[0.2em] text-dim uppercase">
          <span>© {YEAR} electrohub — abA project</span>
          <span className="text-phos">
            [EOF]<span className="blink">_</span>
          </span>
        </div>
      </div>
    </footer>
  )
}
