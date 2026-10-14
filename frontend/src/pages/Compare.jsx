import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useCompare } from '../context/CompareContext'
import { getProduct } from '../services/api'
import { EmptyState, Loader } from '../components/States'
import { formatPrice } from '../lib/format'

export default function Compare() {
  const { items, remove, clear } = useCompare()
  const [details, setDetails] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let active = true
    if (!items.length) {
      setDetails([])
      return
    }
    setLoading(true)
    Promise.all(items.map((i) => getProduct(i.slug)))
      .then((res) => active && setDetails(res))
      .catch(() => active && setDetails([]))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [items])

  if (items.length === 0) {
    return (
      <EmptyState
        title="nothing to compare"
        message="Queue up to 4 units to diff their specifications side by side."
        action={
          <Link to="/products" className="btn btn-primary">
            [ browse catalog ]
          </Link>
        }
      />
    )
  }

  const specKeys = [...new Set(details.flatMap((d) => (d.specifications || []).map((s) => s.key)))]

  const rows = [
    { label: 'brand', render: (d) => d.brand?.name?.toLowerCase() },
    { label: 'price', render: (d) => formatPrice(d.discount_price ?? d.price), tone: 'phos' },
    { label: 'rating', render: (d) => (d.average_rating ? `${d.average_rating.toFixed(1)} ★` : '—') },
    { label: 'stock', render: (d) => d.stock },
  ]

  return (
    <div className="space-y-6">
      <div className="panel frame flex items-center justify-between p-5">
        <div>
          <span className="label text-phos">~/compare</span>
          <h1 className="font-display text-4xl leading-none text-ink uppercase">Compare matrix</h1>
        </div>
        <button type="button" onClick={clear} className="btn btn-danger">
          [ clear all ]
        </button>
      </div>

      {loading && <Loader label="diffing units" />}

      {!loading && (
        <div className="panel overflow-x-auto">
          <table className="w-full min-w-[680px] border-collapse text-xs">
            <thead>
              <tr className="border-b border-line">
                <th className="w-32 p-4 text-left align-bottom">
                  <span className="label">field</span>
                </th>
                {details.map((d) => (
                  <th key={d._id} className="p-4 align-top">
                    <div className="relative">
                      <button
                        type="button"
                        onClick={() => remove(d._id)}
                        className="absolute -right-1 -top-1 z-10 border border-line-2 bg-bg px-1.5 text-[11px] text-dim transition hover:border-alert hover:text-alert"
                      >
                        ×
                      </button>
                      <Link to={`/products/${d.slug}`} className="img-phos block overflow-hidden border border-line bg-bg">
                        <img
                          src={d.image}
                          alt={d.name}
                          className="h-28 w-full object-cover"
                        />
                      </Link>
                      <Link
                        to={`/products/${d.slug}`}
                        className="mt-2 block text-left text-xs font-medium text-ink transition hover:text-phos"
                      >
                        {d.name}
                      </Link>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.label} className="border-b border-line">
                  <td className="p-4 text-dim">{row.label}</td>
                  {details.map((d) => (
                    <td
                      key={d._id}
                      className={`p-4 ${row.tone === 'phos' ? 'font-bold text-phos' : 'text-ink'}`}
                    >
                      {row.render(d)}
                    </td>
                  ))}
                </tr>
              ))}
              {specKeys.map((key) => (
                <tr key={key} className="border-b border-line last:border-b-0">
                  <td className="p-4 text-dim">{key}</td>
                  {details.map((d) => (
                    <td key={d._id} className="p-4 text-ink">
                      {d.specifications?.find((s) => s.key === key)?.value || '—'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
