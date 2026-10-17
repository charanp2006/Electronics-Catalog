import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { AnimatePresence, motion } from 'motion/react'
import { getBrands, getCategories, getProducts } from '../services/api'
import { useApi } from '../hooks/useApi'
import { EASE } from '../components/ui/Reveal'
import FilterSidebar from '../components/FilterSidebar'
import SortDropdown from '../components/SortDropdown'
import SearchBar from '../components/SearchBar'
import Pagination from '../components/Pagination'
import ProductList from '../components/ProductList'
import { EmptyState, ErrorState, Loader } from '../components/States'

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [showFilters, setShowFilters] = useState(false)

  const filters = {
    q: searchParams.get('q') || '',
    category: searchParams.get('category') || undefined,
    brand: searchParams.get('brand') || undefined,
    min_price: searchParams.get('min_price') || undefined,
    max_price: searchParams.get('max_price') || undefined,
    sort: searchParams.get('sort') || 'newest',
    page: Number(searchParams.get('page') || 1),
  }

  const { data: categories } = useApi(getCategories, [])
  const { data: brands } = useApi(getBrands, [])

  const { data, loading, error, refetch } = useApi(
    () =>
      getProducts({
        q: filters.q || undefined,
        category: filters.category,
        brand: filters.brand,
        min_price: filters.min_price,
        max_price: filters.max_price,
        sort: filters.sort,
        page: filters.page,
        limit: 12,
      }),
    [searchParams]
  )

  const update = (patch) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(patch).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') next.delete(key)
      else next.set(key, value)
    })
    if (!('page' in patch)) next.delete('page')
    setSearchParams(next)
  }

  const title = filters.q
    ? `query: "${filters.q}"`
    : filters.category
      ? categories?.find((c) => c.slug === filters.category)?.name || 'catalog'
      : 'all units'

  return (
    <div className="space-y-6">
      <div className="panel frame flex flex-wrap items-end justify-between gap-4 p-5">
        <div>
          <span className="label text-phos">~/catalog</span>
          <h1 className="font-display text-4xl leading-none text-ink uppercase sm:text-5xl">
            {title}
          </h1>
        </div>
        <div className="min-w-[240px] flex-1 sm:max-w-md">
          <SearchBar initial={filters.q} onSubmit={(q) => update({ q })} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <div className="hidden lg:block">
          <FilterSidebar
            categories={categories || []}
            brands={brands || []}
            filters={filters}
            onChange={update}
          />
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => setShowFilters(true)}
              className="btn lg:hidden"
            >
              [ params ]
            </button>
            <span className="label">
              {data ? (
                <>
                  <span className="text-phos">{String(data.total).padStart(3, '0')}</span> results
                </>
              ) : (
                '—'
              )}
            </span>
            <SortDropdown value={filters.sort} onChange={(sort) => update({ sort })} />
          </div>

          {loading && <Loader label="executing query" />}
          {error && <ErrorState message={error} onRetry={refetch} />}

          {data && data.items.length === 0 && (
            <EmptyState
              title="no matches"
              message="No products matched this query. Adjust the parameters and run again."
              action={
                <button type="button" onClick={() => setSearchParams({})} className="btn btn-primary">
                  reset query
                </button>
              }
            />
          )}

          {data && data.items.length > 0 && (
            <>
              <ProductList products={data.items} />
              <Pagination
                page={data.page}
                limit={data.limit}
                total={data.total}
                onPageChange={(page) => update({ page })}
              />
            </>
          )}
        </div>
      </div>

      <AnimatePresence>
        {showFilters && (
          <motion.div
            className="fixed inset-0 z-[65] flex lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="absolute inset-0 bg-black/70" onClick={() => setShowFilters(false)} />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ duration: 0.3, ease: EASE }}
              className="relative ml-auto h-full w-80 max-w-[85%] overflow-y-auto border-l border-line bg-bg p-4"
            >
              <button
                type="button"
                onClick={() => setShowFilters(false)}
                className="btn mb-3 w-full"
              >
                [ close ]
              </button>
              <FilterSidebar
                categories={categories || []}
                brands={brands || []}
                filters={filters}
                onChange={(patch) => {
                  update(patch)
                  setShowFilters(false)
                }}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
