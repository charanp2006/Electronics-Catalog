import { useEffect, useState } from 'react'

function Option({ active, onClick, children, count }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full items-center gap-2 py-1 text-left text-xs transition hover:text-ink"
    >
      <span className={active ? 'text-phos' : 'text-line-2'}>{active ? '[x]' : '[ ]'}</span>
      <span className={active ? 'text-phos' : 'text-dim'}>{children}</span>
      {count !== undefined && count !== null && (
        <span className="ml-auto text-[10px] text-line-2 tabular-nums">{count}</span>
      )}
    </button>
  )
}

export default function FilterSidebar({ categories = [], brands = [], filters, onChange }) {
  const [minPrice, setMinPrice] = useState(filters.min_price || '')
  const [maxPrice, setMaxPrice] = useState(filters.max_price || '')

  useEffect(() => {
    setMinPrice(filters.min_price || '')
    setMaxPrice(filters.max_price || '')
  }, [filters.min_price, filters.max_price])

  const patch = (next) => onChange({ ...filters, ...next })

  const applyPrice = (e) => {
    e.preventDefault()
    patch({ min_price: minPrice || undefined, max_price: maxPrice || undefined })
  }

  const hasFilters = filters.category || filters.brand || filters.min_price || filters.max_price

  const clearAll = () =>
    onChange({ category: undefined, brand: undefined, min_price: undefined, max_price: undefined })

  return (
    <aside className="panel frame sticky top-24">
      <div className="flex items-center justify-between border-b border-line px-4 py-2.5">
        <span className="label text-phos">parameters</span>
        {hasFilters && (
          <button
            type="button"
            onClick={clearAll}
            className="text-[10px] tracking-[0.15em] text-alert uppercase hover:underline"
          >
            [reset]
          </button>
        )}
      </div>

      <div className="space-y-6 p-4">
        <div>
          <p className="label mb-2">category</p>
          <div className="space-y-0.5">
            <Option active={!filters.category} onClick={() => patch({ category: undefined })}>
              all
            </Option>
            {categories.map((c) => (
              <Option
                key={c.slug}
                active={filters.category === c.slug}
                onClick={() => patch({ category: c.slug })}
                count={c.product_count}
              >
                {c.name.toLowerCase()}
              </Option>
            ))}
          </div>
        </div>

        <div className="hairline" />

        <div>
          <p className="label mb-2">brand</p>
          <div className="max-h-52 space-y-0.5 overflow-y-auto pr-1">
            <Option active={!filters.brand} onClick={() => patch({ brand: undefined })}>
              all
            </Option>
            {brands.map((b) => (
              <Option
                key={b.slug}
                active={filters.brand === b.slug}
                onClick={() => patch({ brand: b.slug })}
              >
                {b.name.toLowerCase()}
              </Option>
            ))}
          </div>
        </div>

        <div className="hairline" />

        <form onSubmit={applyPrice}>
          <p className="label mb-2">price range (₹)</p>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min="0"
              placeholder="min"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              className="field"
            />
            <span className="text-line-2">–</span>
            <input
              type="number"
              min="0"
              placeholder="max"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              className="field"
            />
          </div>
          <button type="submit" className="btn mt-3 w-full">
            apply range
          </button>
        </form>
      </div>
    </aside>
  )
}
