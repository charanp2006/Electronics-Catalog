import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useApi } from '../../hooks/useApi'
import { getOrderById, setOrderStatus, extractError } from '../api'
import { Loader, ErrorState, PageHeader, Money, StatusChip } from '../ui'

const ALLOWED = {
  pending: ['processing', 'cancelled'],
  processing: ['shipped', 'cancelled'],
  shipped: ['delivered', 'cancelled'],
  delivered: [],
  cancelled: [],
}

export default function OrderDetail() {
  const { id } = useParams()
  const { data: order, loading, error, setData } = useApi(() => getOrderById(id), [id])
  const [busy, setBusy] = useState(false)
  const [actionError, setActionError] = useState(null)

  const change = async (status) => {
    if (!window.confirm(`Set status to "${status}"?`)) return
    setBusy(true)
    setActionError(null)
    try {
      setData(await setOrderStatus(order.id, status))
    } catch (err) {
      setActionError(extractError(err))
    } finally {
      setBusy(false)
    }
  }

  if (loading) return <Loader label="loading order" />

  return (
    <div className="space-y-6">
      <PageHeader
        title={`order #${order?.id?.slice(-8) || '????'}`}
        subtitle="order detail"
        actions={
          <Link to="/admin-cms/orders" className="btn">
            back
          </Link>
        }
      />

      {error && <ErrorState message={error} />}
      {actionError && (
        <p className="border border-alert/40 bg-alert/5 px-3 py-2 text-xs text-alert">
          {actionError}
        </p>
      )}

      {order && (
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="panel frame space-y-3 p-4 lg:col-span-2">
            <p className="label">items</p>
            {order.items?.map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-3 border border-line px-3 py-2 text-xs"
              >
                {item.image && (
                  <img src={item.image} alt="" className="h-9 w-9 border border-line object-cover" />
                )}
                <span className="grow text-ink">{item.name}</span>
                <span className="text-dim">× {item.quantity}</span>
                <Money value={item.price * item.quantity} />
              </div>
            ))}
            <div className="space-y-1 border-t border-line pt-3 text-xs">
              <div className="flex justify-between text-dim">
                <span>subtotal</span>
                <Money value={order.subtotal} />
              </div>
              <div className="flex justify-between text-dim">
                <span>discount</span>
                <span>
                  − <Money value={order.discount} />
                </span>
              </div>
              <div className="flex justify-between text-sm text-phos">
                <span className="label">total</span>
                <Money value={order.total} />
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="panel frame space-y-3 p-4">
              <p className="label">status</p>
              <StatusChip status={order.status} />
              <div className="flex flex-wrap gap-2">
                {(ALLOWED[order.status] || []).map((status) => (
                  <button
                    key={status}
                    type="button"
                    disabled={busy}
                    onClick={() => change(status)}
                    className="btn"
                  >
                    → {status}
                  </button>
                ))}
                {(ALLOWED[order.status] || []).length === 0 && (
                  <span className="text-[0.65rem] text-dim">terminal state</span>
                )}
              </div>
            </div>

            <div className="panel frame space-y-2 p-4">
              <p className="label">customer</p>
              <p className="text-xs text-ink">{order.user?.name || order.user?.username || '—'}</p>
              <p className="text-[0.65rem] text-dim">{order.user?.email || '—'}</p>
            </div>

            <div className="panel frame p-4">
              <p className="label mb-2">history</p>
              <div className="space-y-1.5">
                {(order.status_history || []).map((entry, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between text-[0.65rem] text-dim"
                  >
                    <StatusChip status={entry.status} />
                    <span>{new Date(entry.at).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
