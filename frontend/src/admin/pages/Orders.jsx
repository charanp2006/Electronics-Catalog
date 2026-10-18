import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useApi } from '../../hooks/useApi'
import { listOrders } from '../api'
import { Loader, ErrorState, EmptyState, PageHeader, Money, StatusChip } from '../ui'

const STATUSES = ['', 'pending', 'processing', 'shipped', 'delivered', 'cancelled']

export default function Orders() {
  const [filters, setFilters] = useState({ status: '', q: '', page: 1 })
  const { data, loading, error, refetch } = useApi(
    () =>
      listOrders({
        status: filters.status || undefined,
        q: filters.q || undefined,
        page: filters.page,
        limit: 20,
      }),
    [filters]
  )

  const patch = (value) => setFilters((f) => ({ ...f, ...value, page: value.page ?? 1 }))

  return (
    <div className="space-y-6">
      <PageHeader title="orders" subtitle="fulfilment queue" />

      <div className="panel frame flex flex-wrap items-end gap-3 p-4">
        <label className="block grow">
          <span className="label mb-1.5 block">search</span>
          <input
            value={filters.q}
            onChange={(e) => patch({ q: e.target.value })}
            placeholder="order id, email, username…"
            className="field"
          />
        </label>
        <label className="block w-48">
          <span className="label mb-1.5 block">status</span>
          <select
            value={filters.status}
            onChange={(e) => patch({ status: e.target.value })}
            className="field"
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s || 'all'}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading && <Loader label="loading orders" />}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {data && data.items.length === 0 && <EmptyState title="no orders" />}

      {data && data.items.length > 0 && (
        <div className="panel frame overflow-x-auto">
          <table className="w-full min-w-[680px] text-left text-xs">
            <thead>
              <tr className="border-b border-line text-dim">
                <th className="p-3 font-normal">order</th>
                <th className="p-3 font-normal">customer</th>
                <th className="p-3 font-normal">items</th>
                <th className="p-3 font-normal">total</th>
                <th className="p-3 font-normal">status</th>
                <th className="p-3 font-normal">date</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((order) => (
                <tr key={order.id} className="border-b border-line/60 hover:bg-panel-2/50">
                  <td className="p-3">
                    <Link to={`/admin-cms/orders/${order.id}`} className="link-underline text-phos">
                      #{order.id.slice(-8)}
                    </Link>
                  </td>
                  <td className="p-3 text-dim">{order.user?.email || order.user?.username || '—'}</td>
                  <td className="p-3 text-dim">{order.items?.length || 0}</td>
                  <td className="p-3">
                    <Money value={order.total} />
                  </td>
                  <td className="p-3">
                    <StatusChip status={order.status} />
                  </td>
                  <td className="p-3 text-dim">
                    {order.created_at ? new Date(order.created_at).toLocaleDateString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && data.total > data.limit && (
        <div className="flex items-center justify-between text-xs text-dim">
          <button
            type="button"
            disabled={filters.page <= 1}
            onClick={() => patch({ page: filters.page - 1 })}
            className="btn"
          >
            prev
          </button>
          <span>
            page {data.page} · {data.total} orders
          </span>
          <button
            type="button"
            disabled={filters.page * data.limit >= data.total}
            onClick={() => patch({ page: filters.page + 1 })}
            className="btn"
          >
            next
          </button>
        </div>
      )}
    </div>
  )
}
