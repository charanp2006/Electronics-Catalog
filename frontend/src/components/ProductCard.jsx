import { Link } from 'react-router-dom'
import Rating from './Rating'
import { discountPercent, formatPrice } from '../lib/format'

export default function ProductCard({
  product,
  index,
  onAddToCart,
  onToggleWishlist,
  onAddToCompare,
  wished,
}) {
  const off = discountPercent(product.price, product.discount_price)
  const inStock = product.stock > 0
  const specs = (product.specifications || []).slice(0, 2)

  return (
    <div className="panel frame group flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-line px-3 py-1.5 text-[10px] tracking-[0.2em] uppercase">
        <span className="text-line-2">
          unit {index !== undefined ? String(index + 1).padStart(3, '0') : '---'}
        </span>
        <span className="truncate text-phos">{product.brand?.name?.toLowerCase()}</span>
      </div>

      <Link
        to={`/products/${product.slug}`}
        className="img-phos relative block overflow-hidden border-b border-line bg-bg"
      >
        <img
          src={product.image}
          alt={product.name}
          loading="lazy"
          className="h-44 w-full object-cover"
        />
        <span className="crt-scanlines pointer-events-none absolute inset-0 opacity-25" />
        <div className="absolute left-2 top-2 flex flex-col items-start gap-1">
          {off > 0 && <span className="chip border-phos/50 bg-bg/70 text-phos">-{off}%</span>}
          {!inStock && <span className="chip border-alert/50 bg-bg/70 text-alert">out</span>}
        </div>
      </Link>

      <div className="flex flex-1 flex-col gap-2 p-3">
        <div className="flex items-center justify-between gap-2">
          <Rating value={product.average_rating} showValue={false} />
          <span className="text-[10px] text-line-2 tabular-nums">
            {product.stock} in stock
          </span>
        </div>

        <Link
          to={`/products/${product.slug}`}
          className="line-clamp-2 min-h-8 text-xs font-medium text-ink transition hover:text-phos"
        >
          {product.name}
        </Link>

        {specs.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {specs.map((s) => (
              <span key={s.key} className="chip">
                {s.value}
              </span>
            ))}
          </div>
        )}

        <div className="mt-auto space-y-2 pt-1">
          <div className="flex items-baseline gap-2">
            <span className="text-sm font-bold text-phos">
              {formatPrice(product.discount_price ?? product.price)}
            </span>
            {off > 0 && (
              <span className="text-[10px] text-line-2 line-through">
                {formatPrice(product.price)}
              </span>
            )}
          </div>

          <div className="flex gap-1">
            {onAddToCart && (
              <button
                type="button"
                onClick={() => onAddToCart(product)}
                disabled={!inStock}
                className="btn btn-primary flex-1"
              >
                + buf
              </button>
            )}
            {onToggleWishlist && (
              <button
                type="button"
                onClick={() => onToggleWishlist(product)}
                title="save"
                className={`btn !px-2.5 ${wished ? '!border-phos !text-phos' : ''}`}
              >
                ♥
              </button>
            )}
            {onAddToCompare && (
              <button
                type="button"
                onClick={() => onAddToCompare(product)}
                title="compare"
                className="btn !px-2.5"
              >
                ⇄
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
