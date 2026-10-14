import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { addReviewApi, getProduct, getRelated } from '../services/api'
import { useApi } from '../hooks/useApi'
import Rating, { RatingInput } from '../components/Rating'
import ProductGrid from '../components/ProductGrid'
import { ErrorState, Loader } from '../components/States'
import { Frame } from '../components/ui/Frame'
import { SecHead, Leader } from '../components/ui/Blocks'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import { useWishlist } from '../context/WishlistContext'
import { useCompare } from '../context/CompareContext'
import { discountPercent, formatDate, formatPrice } from '../lib/format'

function Stepper({ value, min = 1, max = 99, onChange }) {
  return (
    <div className="flex items-center border border-line-2">
      <button
        type="button"
        onClick={() => onChange(Math.max(min, value - 1))}
        className="px-3 py-2 text-dim transition hover:text-phos"
      >
        −
      </button>
      <span className="w-10 border-x border-line-2 py-2 text-center text-sm text-ink tabular-nums">
        {String(value).padStart(2, '0')}
      </span>
      <button
        type="button"
        onClick={() => onChange(Math.min(max, value + 1))}
        className="px-3 py-2 text-dim transition hover:text-phos"
      >
        +
      </button>
    </div>
  )
}

export default function ProductDetail() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { addItem } = useCart()
  const { isWished, toggle } = useWishlist()
  const { add: addCompare } = useCompare()

  const [quantity, setQuantity] = useState(1)
  const [activeImage, setActiveImage] = useState(0)
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' })
  const [reviewError, setReviewError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const { data: product, loading, error, refetch } = useApi(() => getProduct(slug), [slug])
  const { data: related } = useApi(() => getRelated(slug, 4), [slug])

  useEffect(() => {
    setQuantity(1)
    setActiveImage(0)
  }, [slug])

  if (loading) return <Loader label="retrieving document" />
  if (error) return <ErrorState message={error} onRetry={refetch} />
  if (!product) return null

  const off = discountPercent(product.price, product.discount_price)
  const wished = user && isWished(product)
  const images = product.images?.length ? product.images : [product.image]
  const inStock = product.stock > 0
  const requireAuth = (action) => {
    if (!user) return navigate('/login', { state: { from: `/products/${slug}` } })
    action()
  }

  const submitReview = async (e) => {
    e.preventDefault()
    setReviewError(null)
    setSubmitting(true)
    try {
      await addReviewApi(slug, reviewForm)
      setReviewForm({ rating: 5, comment: '' })
      await refetch()
    } catch (err) {
      setReviewError(err?.response?.data?.detail || 'Could not submit review')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-12">
      {/* breadcrumb */}
      <nav className="flex flex-wrap items-center gap-2 text-[11px] tracking-[0.14em] text-dim uppercase">
        <Link to="/" className="hover:text-phos">
          ~/home
        </Link>
        <span className="text-line-2">/</span>
        <Link to="/products" className="hover:text-phos">
          catalog
        </Link>
        <span className="text-line-2">/</span>
        <Link to={`/products?category=${product.category?.slug || ''}`} className="hover:text-phos">
          {product.category?.name?.toLowerCase()}
        </Link>
        <span className="text-line-2">/</span>
        <span className="truncate text-phos">{product.slug}</span>
      </nav>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* gallery */}
        <div className="space-y-3">
          <Frame
            label={`img ${String(activeImage + 1).padStart(2, '0')} / ${String(images.length).padStart(2, '0')}`}
            bodyClassName="relative"
          >
            <div className="img-phos overflow-hidden bg-bg">
              <img src={images[activeImage]} alt={product.name} className="h-[380px] w-full object-cover" />
            </div>
            <span className="crt-scanlines pointer-events-none absolute inset-0 opacity-30" />
          </Frame>

          {images.length > 1 && (
            <div className="flex gap-2">
              {images.map((src, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setActiveImage(i)}
                  className={`h-16 w-16 overflow-hidden border bg-bg transition ${
                    i === activeImage ? 'border-phos' : 'border-line hover:border-line-2'
                  }`}
                >
                  <img src={src} alt="" className="h-full w-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* details */}
        <div className="space-y-5">
          <div>
            <div className="flex items-center gap-3 text-[10px] tracking-[0.2em] uppercase">
              <span className="text-line-2">unit/{product._id.slice(-6)}</span>
              <Link to={`/products?brand=${product.brand?.slug || ''}`} className="text-phos hover:underline">
                {product.brand?.name?.toLowerCase()}
              </Link>
            </div>
            <h1 className="mt-2 font-display text-4xl leading-[0.95] text-ink uppercase sm:text-5xl">
              {product.name}
            </h1>
            <div className="mt-3">
              <Rating value={product.average_rating} count={product.total_reviews} />
            </div>
          </div>

          <div className="flex flex-wrap items-end gap-3">
            <span className="font-display text-4xl leading-none text-phos">
              {formatPrice(product.discount_price ?? product.price)}
            </span>
            {off > 0 && (
              <>
                <span className="text-sm text-line-2 line-through">
                  {formatPrice(product.price)}
                </span>
                <span className="chip border-phos/50 text-phos">-{off}%</span>
              </>
            )}
          </div>

          <p className="text-xs leading-relaxed text-dim">{product.description}</p>

          <div className="flex items-center gap-2 text-[11px] tracking-[0.14em] uppercase">
            <span className={inStock ? 'text-sig' : 'text-alert'}>●</span>
            <span className={inStock ? 'text-sig' : 'text-alert'}>
              {inStock ? `in stock — ${product.stock} units` : 'out of stock'}
            </span>
          </div>

          <div className="hairline" />

          <div className="flex flex-wrap items-center gap-2">
            <Stepper
              value={quantity}
              max={product.stock || 1}
              onChange={setQuantity}
            />
            <button
              type="button"
              onClick={() => requireAuth(() => addItem(product, quantity))}
              disabled={!inStock}
              className="btn btn-primary"
            >
              [ + add to buffer ]
            </button>
            <button
              type="button"
              onClick={() => requireAuth(() => toggle(product))}
              className={`btn ${wished ? '!border-phos !text-phos' : ''}`}
            >
              [ ♥ {wished ? 'saved' : 'save'} ]
            </button>
            <button type="button" onClick={() => addCompare(product)} className="btn">
              [ ⇄ compare ]
            </button>
          </div>
        </div>
      </div>

      {/* datasheet */}
      {product.specifications?.length > 0 && (
        <section>
          <SecHead index={1} title="datasheet" count={product.specifications.length} unit="SPEC" />
          <Frame bodyClassName="grid gap-x-10 gap-y-3 p-5 sm:grid-cols-2">
            {product.specifications.map((s) => (
              <Leader key={s.key} label={s.key} value={s.value} />
            ))}
          </Frame>
        </section>
      )}

      {/* price log */}
      {product.price_history?.length > 0 && (
        <section>
          <SecHead index={2} title="price log" count={product.price_history.length} unit="Δ" />
          <Frame bodyClassName="divide-y divide-line">
            {product.price_history.map((h, i) => {
              const delta = (h.new_price || 0) - (h.old_price || 0)
              return (
                <div key={i} className="flex items-center justify-between gap-4 px-5 py-3 text-xs">
                  <span className="text-dim">{formatDate(h.changed_at)}</span>
                  <span className="text-line-2 line-through">{formatPrice(h.old_price)}</span>
                  <span className="text-sig">→ {formatPrice(h.new_price)}</span>
                  <span className={delta <= 0 ? 'text-sig' : 'text-alert'}>
                    {delta <= 0 ? '' : '+'}
                    {formatPrice(delta)}
                  </span>
                </div>
              )
            })}
          </Frame>
        </section>
      )}

      {/* reviews */}
      <section>
        <SecHead index={3} title="feedback log" count={product.total_reviews} unit="LOG" />
        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <div className="space-y-2">
            {(product.reviews || []).length === 0 && (
              <p className="panel px-4 py-6 text-center text-xs text-dim">
                no entries yet — be the first to log feedback
              </p>
            )}
            {(product.reviews || []).map((r, i) => (
              <div key={i} className="panel px-4 py-3">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-xs text-phos">@{r.username}</span>
                  <Rating value={r.rating} showValue={false} />
                </div>
                <p className="mt-1.5 text-xs text-dim">{r.comment}</p>
                <p className="mt-1 text-[10px] tracking-[0.14em] text-line-2 uppercase">
                  {formatDate(r.created_at)}
                </p>
              </div>
            ))}
          </div>

          <Frame label="append entry" bodyClassName="p-4">
            {user ? (
              <form onSubmit={submitReview} className="space-y-3">
                <RatingInput
                  value={reviewForm.rating}
                  onChange={(rating) => setReviewForm((f) => ({ ...f, rating }))}
                />
                <textarea
                  required
                  rows={4}
                  value={reviewForm.comment}
                  onChange={(e) => setReviewForm((f) => ({ ...f, comment: e.target.value }))}
                  placeholder="log your experience…"
                  className="field resize-none"
                />
                {reviewError && <p className="text-xs text-alert">{reviewError}</p>}
                <button type="submit" disabled={submitting} className="btn btn-primary w-full">
                  {submitting ? 'writing…' : 'commit entry'}
                </button>
              </form>
            ) : (
              <p className="text-xs text-dim">
                <Link to="/login" className="text-phos hover:underline">
                  Authenticate
                </Link>{' '}
                to append a feedback entry.
              </p>
            )}
          </Frame>
        </div>
      </section>

      {/* related */}
      {related?.length > 0 && (
        <section>
          <SecHead index={4} title="related units" count={related.length} />
          <ProductGrid products={related} />
        </section>
      )}
    </div>
  )
}
