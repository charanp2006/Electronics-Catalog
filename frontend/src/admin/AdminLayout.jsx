import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Package,
  LayoutGrid,
  Tags,
  ShoppingCart,
  Star,
  LogOut,
  ExternalLink,
} from 'lucide-react'
import { useAdminAuth } from './AdminAuthContext'

const NAV = [
  { to: '/admin-cms', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/admin-cms/products', label: 'Products', icon: Package },
  { to: '/admin-cms/categories', label: 'Categories', icon: LayoutGrid },
  { to: '/admin-cms/brands', label: 'Brands', icon: Tags },
  { to: '/admin-cms/orders', label: 'Orders', icon: ShoppingCart },
  { to: '/admin-cms/reviews', label: 'Reviews', icon: Star },
]

function NavItem({ item }) {
  const Icon = item.icon
  return (
    <NavLink
      to={item.to}
      end={item.end}
      className={({ isActive }) =>
        `flex items-center gap-2 border border-transparent px-3 py-2 text-xs uppercase tracking-widest ${
          isActive
            ? 'border-phos/40 bg-panel-2 text-phos'
            : 'text-dim hover:border-line-2 hover:text-ink'
        }`
      }
    >
      <Icon size={14} />
      {item.label}
    </NavLink>
  )
}

export default function AdminLayout() {
  const { admin, logout } = useAdminAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/admin-cms/login')
  }

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[220px_1fr]">
      <aside className="border-b border-line bg-panel lg:border-r lg:border-b-0">
        <div className="flex flex-col gap-3 p-4 lg:sticky lg:top-0 lg:h-screen">
          <div>
            <p className="font-display text-2xl tracking-wider text-phos uppercase glow">
              electrohub
            </p>
            <p className="label">control panel</p>
          </div>

          <nav className="flex flex-wrap gap-1 lg:flex-1 lg:flex-col lg:flex-nowrap">
            {NAV.map((item) => (
              <NavItem key={item.to} item={item} />
            ))}
          </nav>

          <div className="border-t border-line pt-3">
            <p className="truncate text-xs text-ink">{admin?.name || admin?.username}</p>
            <p className="truncate text-[0.65rem] text-dim">{admin?.email}</p>
            <div className="mt-2 flex gap-2">
              <a href="/" className="btn flex-1">
                <ExternalLink size={12} /> shop
              </a>
              <button type="button" onClick={handleLogout} className="btn btn-danger flex-1">
                <LogOut size={12} /> exit
              </button>
            </div>
          </div>
        </div>
      </aside>

      <main className="min-w-0 p-4 lg:p-6">
        <Outlet />
      </main>
    </div>
  )
}
