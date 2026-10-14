import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import SearchBar from './SearchBar'

const NAV = [
  { to: '/', label: 'home', end: true },
  { to: '/products', label: 'catalog' },
]

function CountLink({ to, label, count }) {
  return (
    <Link
      to={to}
      className="hidden items-center gap-1.5 border border-transparent px-2 py-1.5 text-[11px] tracking-[0.18em] text-dim uppercase transition hover:border-line-2 hover:text-phos sm:flex"
    >
      {label}
      <span className={count > 0 ? 'text-phos' : 'text-line-2'}>
        [{String(count).padStart(2, '0')}]
      </span>
    </Link>
  )
}

export default function Navbar({ cartCount = 0, compareCount = 0, wishCount = 0, user }) {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  const linkClass = ({ isActive }) =>
    `text-[11px] uppercase tracking-[0.2em] transition ${
      isActive ? 'text-phos' : 'text-dim hover:text-ink'
    }`

  const goSearch = (q) => {
    setOpen(false)
    navigate(`/products?q=${encodeURIComponent(q)}`)
  }

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-bg/90 backdrop-blur">
      <div className="mx-auto flex max-w-[1400px] items-center gap-4 px-4 py-3">
        <Link to="/" className="flex shrink-0 items-baseline gap-0.5">
          <span className="font-display text-2xl leading-none text-phos glow-soft">
            ELECTROHUB
          </span>
          <span className="blink text-phos">_</span>
        </Link>

        <nav className="ml-3 hidden items-center gap-5 md:flex">
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.end} className={linkClass}>
              <span className="text-phos/40">/</span>
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto hidden max-w-sm flex-1 md:block">
          <SearchBar onSubmit={goSearch} />
        </div>

        <div className="ml-auto flex items-center gap-1 md:ml-0">
          <CountLink to="/compare" label="cmp" count={compareCount} />
          <CountLink to="/wishlist" label="sav" count={wishCount} />
          <CountLink to="/cart" label="buf" count={cartCount} />
          <Link
            to={user ? '/account' : '/login'}
            className="btn ml-1 !py-1.5 !text-[10px]"
          >
            {user ? user.username : 'login'}
          </Link>
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            className="btn !px-2.5 !py-1.5 md:hidden"
            aria-label="Menu"
          >
            {open ? 'x' : '≡'}
          </button>
        </div>
      </div>

      {open && (
        <div className="space-y-4 border-t border-line px-4 py-4 md:hidden">
          <SearchBar onSubmit={goSearch} />
          <nav className="flex flex-col gap-3">
            {NAV.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.end}
                className={linkClass}
                onClick={() => setOpen(false)}
              >
                <span className="text-phos/40">/</span>
                {n.label}
              </NavLink>
            ))}
            <NavLink to="/compare" className={linkClass} onClick={() => setOpen(false)}>
              <span className="text-phos/40">/</span>compare
            </NavLink>
            <NavLink to="/wishlist" className={linkClass} onClick={() => setOpen(false)}>
              <span className="text-phos/40">/</span>saved
            </NavLink>
            <NavLink to="/cart" className={linkClass} onClick={() => setOpen(false)}>
              <span className="text-phos/40">/</span>buffer
            </NavLink>
          </nav>
        </div>
      )}
    </header>
  )
}
