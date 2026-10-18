import { Link } from 'react-router-dom'
import { useApi } from '../../hooks/useApi'
import { getOverview } from '../api'
import { Loader, ErrorState, PageHeader, Money, StatusChip } from '../ui'

function Stat({ label, value, hint }) {
  return (
    <div className="panel frame p-4">
      <p className="label">{label}</p>
      <p className="mt-1 font-display text-3xl text-phos">{value}</p>
      {hint && <p className="mt-0.5 text-[0.65rem] text-dim">{hint}</p>}
    </div>
  )
}

export default function Dashboard() {
  const { data, loading, error, refetch } = useApi(getOverview, [])

  return (
    <div className="space-y-6">
      <PageHeader title="dashboard" subtitle="system overview" />

      {loading && <Loader label="reading telemetry" />}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {data && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <Stat
              label="products"
              value={data.products.total}
              hint={`${data.products.active} active · ${data.products.out_of_stock} out`}
            />
            <Stat
              label="orders"
              value={data.orders.total}
              hint={`${data.orders.by_status?.pending || 0} pending`}
            />
            <Stat label="revenue" value={<Money value={data.orders.revenue} />} hint="excl. cancelled" />
            <Stat
              label="reviews"
              value={data.reviews.total}
              hint={`${data.reviews.hidden} hidden`}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <div className="panel frame p-4 lg:col-span-2">
              <p className="label mb-3">recent orders</p>
              <div className="space-y-2">
                {data.recent_orders.map((order) => (
                  <Link
                    key={order.id}
                    to={`/admin-cms/orders/${order.id}`}
                    className="flex items-center justify-between border border-line px-3 py-2 text-xs hover:border-phos/40"
                  >
                    <span className="font-mono text-dim">#{order.id.slice(-8)}</span>
                    <Money value={order.total} />
                    <StatusChip status={order.status} />
                  </Link>
                ))}
                {data.recent_orders.length === 0 && <p className="text-xs text-dim">no orders yet</p>}
              </div>
            </div>

            <div className="panel frame space-y-3 p-4">
              <p className="label">catalog</p>
              <div className="flex items-center justify-between text-xs">
                <span className="text-dim">categories</span>
                <span className="text-phos">{data.catalog.categories}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-dim">brands</span>
                <span className="text-phos">{data.catalog.brands}</span>
              </div>
              <div className="hairline" />
              <p className="label">stock alerts</p>
              <p className="text-xs text-dim">
                <span className="text-alert">{data.products.low_stock}</span> low ·{' '}
                {data.products.out_of_stock} out of stock
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
