import { Link, useNavigate } from 'react-router-dom'
import Rating from './Rating'
import { useCart } from '../context/CartContext'
import { useWishlist } from '../context/WishlistContext'
import { useCompare } from '../context/CompareContext'
import { useAuth } from '../context/AuthContext'
import { discountPercent, formatPrice } from '../lib/format'

export default function ProductList({ products = [] }) {
  const navigate = useNavigate()
  const { addItem } = useCart()
  const { isWished, toggle } = useWishlist()
  const { add: addCompare } = useCompare()
  const { user } = useAuth()

  const requireAuth = (action) => {
    if (!user) {
      navigate('/login', { state: { from: window.location.pathname } })
      return
    }
    action()
  }

  return (
    <div className="panel">
      {products.map((p, i) => {
        const off = discountPercent(p.price, p.discount_price)
        const inStock = p.stock > 0
        const specs = (p.specifications || []).slice(0, 3)
        const wished = user && isWished(p)

        return (
          <div
            key={p._id}
            className="group flex items-center gap-3 border-b border-line px-3 py-3 transition last:border-b-0 hover:bg-panel-2 sm:gap-4"
          >
            <span className="hidden w-8 shrink-0 font-display text-lg leading-none text-line-2 transition group-hover:text-phos sm:block">
              {String(i + 1).padStart(3, '0')}
            </span>

            <Link
              to={`/products/${p.slug}`}
              className="img-phos h-14 w-14 shrink-0 overflow-hidden border border-line bg-bg"
            >
              <img src={p.image} alt={p.name} loading="lazy" className="h-full w-full object-cover" />
            </Link>

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2 text-[10px] tracking-[0.18em] uppercase">
                <span className="text-dim">{p.brand?.name?.toLowerCase()}</span>
                {off > 0 && <span className="text-phos">-{off}%</span>}
                {!inStock && <span className="text-alert">out</span>}
              </div>
              <Link
                to={`/products/${p.slug}`}
                className="mt-0.5 block truncate text-xs font-medium text-ink transition hover:text-phos"
              >
                {p.name}
              </Link>
              <div className="mt-1">
                <Rating value={p.average_rating} count={p.total_reviews} />
              </div>
            </div>

            <div className="hidden max-w-[230px] flex-wrap gap-1 xl:flex">
              {specs.map((s) => (
                <span key={s.key} className="chip">
                  {s.value}
                </span>
              ))}
            </div>

            <div className="w-24 shrink-0 text-right">
              <div className="text-sm font-bold text-phos">
                {formatPrice(p.discount_price ?? p.price)}
              </div>
              {off > 0 && (
                <div className="text-[10px] text-line-2 line-through">
                  {formatPrice(p.price)}
                </div>
              )}
            </div>

            <div className="flex shrink-0 items-center gap-1">
              <button
                type="button"
                onClick={() => requireAuth(() => addItem(p, 1))}
                disabled={!inStock}
                title="add to buffer"
                className="btn btn-primary !px-2.5"
              >
                +
              </button>
              <button
                type="button"
                onClick={() => requireAuth(() => toggle(p))}
                title="save"
                className={`btn hidden !px-2.5 sm:flex ${wished ? '!border-phos !text-phos' : ''}`}
              >
                ♥
              </button>
              <button
                type="button"
                onClick={() => addCompare(p)}
                title="compare"
                className="btn hidden !px-2.5 sm:flex"
              >
                ⇄
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
