import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, Pencil, Trash2, Eye, EyeOff } from 'lucide-react'
import { useApi } from '../../hooks/useApi'
import { listProducts, deleteProduct } from '../api'
import { Loader, ErrorState, EmptyState, PageHeader, Money } from '../ui'

export default function Products() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState({ q: '', stock: '', sort: 'newest', page: 1 })
  const [busy, setBusy] = useState(null)

  const { data, loading, error, refetch } = useApi(
    () =>
      listProducts({
        q: filters.q || undefined,
        stock: filters.stock || undefined,
        sort: filters.sort,
        page: filters.page,
        limit: 20,
      }),
    [filters]
  )

  const patch = (value) => setFilters((f) => ({ ...f, ...value, page: value.page ?? 1 }))

  const remove = async (product, hard) => {
    const prompt = hard
      ? `Permanently delete "${product.name}"? This cannot be undone.`
      : `Deactivate "${product.name}"?`
    if (!window.confirm(prompt)) return
    setBusy(product._id)
    try {
      await deleteProduct(product._id, hard)
      refetch()
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="products"
        subtitle="catalog units"
        actions={
          <Link to="/admin-cms/products/new" className="btn btn-primary">
            <Plus size={14} /> new product
          </Link>
        }
      />

      <div className="panel frame flex flex-wrap items-end gap-3 p-4">
        <label className="block grow">
          <span className="label mb-1.5 block">search</span>
          <input
            value={filters.q}
            onChange={(e) => patch({ q: e.target.value })}
            placeholder="name, brand, category…"
            className="field"
          />
        </label>
        <label className="block w-40">
          <span className="label mb-1.5 block">stock</span>
          <select
            value={filters.stock}
            onChange={(e) => patch({ stock: e.target.value })}
            className="field"
          >
            <option value="">any</option>
            <option value="low">low (≤5)</option>
            <option value="out">out of stock</option>
          </select>
        </label>
        <label className="block w-40">
          <span className="label mb-1.5 block">sort</span>
          <select
            value={filters.sort}
            onChange={(e) => patch({ sort: e.target.value })}
            className="field"
          >
            <option value="newest">newest</option>
            <option value="name">name</option>
            <option value="price">price</option>
            <option value="stock">stock</option>
          </select>
        </label>
      </div>

      {loading && <Loader label="loading catalog" />}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {data && data.items.length === 0 && <EmptyState title="no products" />}

      {data && data.items.length > 0 && (
        <div className="panel frame overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-xs">
            <thead>
              <tr className="border-b border-line text-dim">
                <th className="p-3 font-normal">unit</th>
                <th className="p-3 font-normal">brand</th>
                <th className="p-3 font-normal">price</th>
                <th className="p-3 font-normal">stock</th>
                <th className="p-3 font-normal">state</th>
                <th className="p-3 text-right font-normal">actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((p) => (
                <tr key={p._id} className="border-b border-line/60 hover:bg-panel-2/50">
                  <td className="p-3">
                    <div className="flex items-center gap-3">
                      <img
                        src={p.image || p.images?.[0]}
                        alt=""
                        className="h-9 w-9 border border-line object-cover"
                      />
                      <div>
                        <p className="text-ink">{p.name}</p>
                        <p className="text-[0.65rem] text-dim">{p.category?.name}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-3 text-dim">{p.brand?.name}</td>
                  <td className="p-3">
                    <Money value={p.discount_price || p.price} />
                    {p.discount_price && (
                      <span className="ml-2 text-[0.65rem] text-dim line-through">
                        <Money value={p.price} />
                      </span>
                    )}
                  </td>
                  <td className={`p-3 ${p.stock <= 5 ? 'text-alert' : 'text-dim'}`}>{p.stock}</td>
                  <td className="p-3">
                    <span className="chip">{p.is_active ? 'active' : 'hidden'}</span>
                    {p.is_featured && <span className="chip ml-1 border-phos text-phos">featured</span>}
                  </td>
                  <td className="p-3">
                    <div className="flex justify-end gap-1">
                      <button
                        type="button"
                        onClick={() => navigate(`/admin-cms/products/${p._id}`)}
                        className="btn px-2 py-1"
                        title="edit"
                      >
                        <Pencil size={13} />
                      </button>
                      <button
                        type="button"
                        disabled={busy === p._id}
                        onClick={() => remove(p, false)}
                        className="btn px-2 py-1"
                        title={p.is_active ? 'deactivate' : 'deactivate'}
                      >
                        {p.is_active ? <EyeOff size={13} /> : <Eye size={13} />}
                      </button>
                      <button
                        type="button"
                        disabled={busy === p._id}
                        onClick={() => remove(p, true)}
                        className="btn btn-danger px-2 py-1"
                        title="delete"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
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
            page {data.page} · {data.total} units
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
