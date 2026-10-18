import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Eye, EyeOff, Trash2 } from 'lucide-react'
import { useApi } from '../../hooks/useApi'
import { listReviews, moderateReview, deleteReview, extractError } from '../api'
import { Loader, EmptyState, PageHeader, StatusChip } from '../ui'

export default function Reviews() {
  const [filters, setFilters] = useState({ status: '', rating: '', q: '', page: 1 })
  const [error, setError] = useState(null)
  const { data, loading, error: loadError, refetch } = useApi(
    () =>
      listReviews({
        status: filters.status || undefined,
        rating: filters.rating || undefined,
        q: filters.q || undefined,
        page: filters.page,
        limit: 20,
      }),
    [filters]
  )

  const patch = (value) => setFilters((f) => ({ ...f, ...value, page: value.page ?? 1 }))

  const setStatus = async (review, status) => {
    setError(null)
    try {
      await moderateReview(review.product_id, review.review_id, { status })
      refetch()
    } catch (err) {
      setError(extractError(err))
    }
  }

  const remove = async (review) => {
    if (!window.confirm('Delete this review permanently?')) return
    setError(null)
    try {
      await deleteReview(review.product_id, review.review_id)
      refetch()
    } catch (err) {
      setError(extractError(err))
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="reviews" subtitle="moderation queue" />

      {(error || loadError) && (
        <p className="border border-alert/40 bg-alert/5 px-3 py-2 text-xs text-alert">
          {error || loadError}
        </p>
      )}

      <div className="panel frame flex flex-wrap items-end gap-3 p-4">
        <label className="block grow">
          <span className="label mb-1.5 block">search</span>
          <input
            value={filters.q}
            onChange={(e) => patch({ q: e.target.value })}
            placeholder="comment or username…"
            className="field"
          />
        </label>
        <label className="block w-40">
          <span className="label mb-1.5 block">status</span>
          <select
            value={filters.status}
            onChange={(e) => patch({ status: e.target.value })}
            className="field"
          >
            <option value="">all</option>
            <option value="published">published</option>
            <option value="hidden">hidden</option>
          </select>
        </label>
        <label className="block w-32">
          <span className="label mb-1.5 block">rating</span>
          <select
            value={filters.rating}
            onChange={(e) => patch({ rating: e.target.value })}
            className="field"
          >
            <option value="">any</option>
            {[5, 4, 3, 2, 1].map((r) => (
              <option key={r} value={r}>
                {r} ★
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading && <Loader label="loading reviews" />}
      {data && data.items.length === 0 && <EmptyState title="no reviews" />}

      {data && data.items.length > 0 && (
        <div className="panel frame divide-y divide-line/60">
          {data.items.map((review) => (
            <div key={`${review.product_id}-${review.review_id}`} className="flex gap-4 p-4">
              <div className="w-32 shrink-0">
                <p className="label">rating</p>
                <p className="font-display text-2xl text-phos">{review.rating}★</p>
              </div>
              <div className="grow">
                <div className="mb-1 flex flex-wrap items-center gap-2 text-xs">
                  <StatusChip status={review.status} />
                  <span className="text-ink">{review.username}</span>
                  <Link
                    to={`/admin-cms/products/${review.product_id}`}
                    className="link-underline text-dim"
                  >
                    {review.product_name}
                  </Link>
                </div>
                <p className="text-xs text-dim">{review.comment}</p>
              </div>
              <div className="flex flex-col gap-1">
                {review.status === 'published' ? (
                  <button
                    type="button"
                    onClick={() => setStatus(review, 'hidden')}
                    className="btn px-2 py-1"
                    title="hide"
                  >
                    <EyeOff size={13} />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => setStatus(review, 'published')}
                    className="btn px-2 py-1"
                    title="publish"
                  >
                    <Eye size={13} />
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => remove(review)}
                  className="btn btn-danger px-2 py-1"
                  title="delete"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            </div>
          ))}
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
            page {data.page} · {data.total} reviews
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
