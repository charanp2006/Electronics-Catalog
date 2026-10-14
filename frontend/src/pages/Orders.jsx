import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getOrders } from '../services/api'
import { useApi } from '../hooks/useApi'
import { EmptyState, ErrorState, Loader } from '../components/States'
import { SecHead } from '../components/ui/Blocks'
import { formatDate, formatPrice } from '../lib/format'

export default function Orders() {
  const { user } = useAuth()
  const { data: orders, loading, error, refetch } = useApi(getOrders, [user])

  if (!user) {
    return (
      <EmptyState
        title="access denied"
        message="Authenticate to inspect the order log."
        action={
          <Link to="/login" className="btn btn-primary">
            [ authenticate ]
          </Link>
        }
      />
    )
  }

  if (loading) return <Loader label="reading order log" />
  if (error) return <ErrorState message={error} onRetry={refetch} />

  if (!orders?.length) {
    return (
      <EmptyState
        title="no orders logged"
        message="Executed orders will be recorded here."
        action={
          <Link to="/products" className="btn btn-primary">
            [ browse catalog ]
          </Link>
        }
      />
    )
  }

  return (
    <div className="space-y-6">
      <SecHead index={1} title="order log" count={orders.length} unit="ORD" />

      <div className="space-y-4">
        {orders.map((order) => (
          <div key={order._id} className="panel frame">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="font-display text-xl leading-none text-phos">
                  #{order._id.slice(-8).toUpperCase()}
                </span>
                <span className="text-[10px] tracking-[0.16em] text-line-2 uppercase">
                  {formatDate(order.created_at)}
                </span>
              </div>
              <span className="chip border-sig/50 text-sig">● {order.status}</span>
            </div>

            <div className="divide-y divide-line">
              {order.items.map((item) => (
                <div key={item.product_id} className="flex items-center gap-3 px-4 py-3">
                  <Link
                    to={`/products/${item.slug}`}
                    className="img-phos h-12 w-12 shrink-0 overflow-hidden border border-line bg-bg"
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
                    <p className="text-[11px] text-dim">
                      {String(item.quantity).padStart(2, '0')} × {formatPrice(item.price)}
                    </p>
                  </div>
                  <span className="text-sm font-bold text-phos">
                    {formatPrice((item.price || 0) * item.quantity)}
                  </span>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-end gap-3 border-t border-line px-4 py-3">
              <span className="label">total</span>
              <span className="font-display text-2xl leading-none text-phos">
                {formatPrice(order.total)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
