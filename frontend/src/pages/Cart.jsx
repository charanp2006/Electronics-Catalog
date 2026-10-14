import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import { EmptyState } from '../components/States'
import { Frame } from '../components/ui/Frame'
import { createOrderApi } from '../services/api'
import { formatPrice } from '../lib/format'

export default function Cart() {
  const { user } = useAuth()
  const { cart, updateItem, removeItem, refresh } = useCart()
  const navigate = useNavigate()
  const [placing, setPlacing] = useState(false)
  const [error, setError] = useState(null)

  if (!user) {
    return (
      <EmptyState
        title="access denied"
        message="Authenticate to inspect your buffer."
        action={
          <Link to="/login" className="btn btn-primary">
            [ authenticate ]
          </Link>
        }
      />
    )
  }

  if (!cart.items.length) {
    return (
      <EmptyState
        title="buffer empty"
        message="No units queued. Load the catalog and add units to the buffer."
        action={
          <Link to="/products" className="btn btn-primary">
            [ browse catalog ]
          </Link>
        }
      />
    )
  }

  const checkout = async () => {
    setPlacing(true)
    setError(null)
    try {
      await createOrderApi({})
      await refresh()
      navigate('/orders')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not place order')
    } finally {
      setPlacing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="panel frame flex items-center justify-between p-5">
        <div>
          <span className="label text-phos">~/buffer</span>
          <h1 className="font-display text-4xl leading-none text-ink uppercase">Buffer</h1>
        </div>
        <span className="label">
          <span className="text-phos">{String(cart.count).padStart(2, '0')}</span> queued
        </span>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        <div className="panel divide-y divide-line">
          {cart.items.map((item) => (
            <div key={item.product_id} className="flex items-center gap-4 p-4">
              <Link
                to={`/products/${item.slug}`}
                className="img-phos h-16 w-16 shrink-0 overflow-hidden border border-line bg-bg"
              >
                <img src={item.image} alt={item.name} className="h-full w-full object-cover" />
              </Link>

              <div className="min-w-0 flex-1">
                <Link
                  to={`/products/${item.slug}`}
                  className="block truncate text-xs font-medium text-ink transition hover:text-phos"
                >
                  {item.name}
                </Link>
                <div className="mt-0.5 flex items-center gap-2 text-[11px] text-dim">
                  <span>{formatPrice(item.discount_price ?? item.price)}</span>
                  {item.discount_price && (
                    <span className="text-line-2 line-through">{formatPrice(item.price)}</span>
                  )}
                </div>
              </div>

              <div className="flex items-center border border-line-2">
                <button
                  type="button"
                  onClick={() => updateItem(item.product_id, item.quantity - 1)}
                  className="px-2.5 py-1.5 text-dim transition hover:text-phos"
                >
                  −
                </button>
                <span className="w-8 border-x border-line-2 py-1.5 text-center text-xs text-ink tabular-nums">
                  {String(item.quantity).padStart(2, '0')}
                </span>
                <button
                  type="button"
                  onClick={() => updateItem(item.product_id, item.quantity + 1)}
                  className="px-2.5 py-1.5 text-dim transition hover:text-phos"
                >
                  +
                </button>
              </div>

              <div className="w-24 text-right text-sm font-bold text-phos">
                {formatPrice((item.discount_price ?? item.price) * item.quantity)}
              </div>

              <button
                type="button"
                onClick={() => removeItem(item.product_id)}
                className="btn btn-danger !px-2.5"
                title="remove"
              >
                ×
              </button>
            </div>
          ))}
        </div>

        <Frame label="invoice" className="h-fit lg:sticky lg:top-24" bodyClassName="space-y-3 p-5">
          <div className="space-y-2 text-xs">
            <Row label="subtotal" value={formatPrice(cart.subtotal)} />
            {cart.discount > 0 && (
              <Row label="discount" value={`- ${formatPrice(cart.discount)}`} tone="sig" />
            )}
          </div>
          <div className="border-t border-dashed border-line-2" />
          <div className="flex items-baseline justify-between">
            <span className="label">total</span>
            <span className="font-display text-3xl leading-none text-phos">
              {formatPrice(cart.total)}
            </span>
          </div>
          {error && <p className="text-xs text-alert">{error}</p>}
          <button
            type="button"
            onClick={checkout}
            disabled={placing}
            className="btn btn-primary w-full"
          >
            {placing ? 'processing…' : '[ execute order ]'}
          </button>
          <p className="text-center text-[10px] tracking-[0.14em] text-line-2 uppercase">
            demo checkout — no real payment
          </p>
        </Frame>
      </div>
    </div>
  )
}

function Row({ label, value, tone = 'ink' }) {
  const tones = { ink: 'text-ink', sig: 'text-sig' }
  return (
    <div className="flex items-center justify-between">
      <span className="text-dim">{label}</span>
      <span className={tones[tone]}>{value}</span>
    </div>
  )
}
