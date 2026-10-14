import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useWishlist } from '../context/WishlistContext'
import { useCompare } from '../context/CompareContext'
import { EmptyState } from '../components/States'
import { Frame } from '../components/ui/Frame'
import { SecHead } from '../components/ui/Blocks'

export default function Account() {
  const { user, logout } = useAuth()
  const { count: wishCount } = useWishlist()
  const { count: compareCount } = useCompare()
  const navigate = useNavigate()

  if (!user) {
    return (
      <EmptyState
        title="access denied"
        message="Authenticate to view the operator profile."
        action={
          <Link to="/login" className="btn btn-primary">
            [ authenticate ]
          </Link>
        }
      />
    )
  }

  const initials = (user.name || user.username || '??')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  const links = [
    { to: '/orders', label: 'order log', meta: 'view →' },
    { to: '/wishlist', label: 'saved units', meta: `${String(wishCount).padStart(2, '0')} →` },
    { to: '/compare', label: 'compare matrix', meta: `${String(compareCount).padStart(2, '0')} →` },
    { to: '/cart', label: 'buffer', meta: 'view →' },
  ]

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <Frame label="operator://profile" bodyClassName="p-6">
        <div className="flex items-center gap-4">
          <span className="grid h-16 w-16 shrink-0 place-items-center border border-phos/40 font-display text-2xl text-phos">
            {initials}
          </span>
          <div>
            <span className="label text-phos">authenticated</span>
            <h1 className="font-display text-3xl leading-none text-ink uppercase">
              {user.name || user.username}
            </h1>
            <p className="text-xs text-dim">
              @{user.username} · {user.email}
            </p>
          </div>
        </div>
      </Frame>

      <SecHead index={1} title="operator console" />
      <div className="panel grid sm:grid-cols-2">
        {links.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            className="group flex items-center justify-between border-b border-line px-4 py-4 transition hover:bg-panel-2 sm:odd:border-r"
          >
            <span className="text-xs text-ink transition group-hover:text-phos">{l.label}</span>
            <span className="text-[10px] tracking-[0.14em] text-line-2 uppercase transition group-hover:text-phos">
              {l.meta}
            </span>
          </Link>
        ))}
      </div>

      <button
        type="button"
        onClick={() => {
          logout()
          navigate('/')
        }}
        className="btn btn-danger"
      >
        [ sign out ]
      </button>
    </div>
  )
}
