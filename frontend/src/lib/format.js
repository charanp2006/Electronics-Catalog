export function formatPrice(value) {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value)
}

export function discountPercent(price, discountPrice) {
  if (!discountPrice || !price || discountPrice >= price) return 0
  return Math.round(((price - discountPrice) / price) * 100)
}

export function effectivePrice(product) {
  return product?.discount_price ?? product?.price ?? 0
}

export function formatDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
