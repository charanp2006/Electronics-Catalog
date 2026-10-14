export default function Pagination({ page, limit, total, onPageChange }) {
  const pages = Math.max(1, Math.ceil(total / limit))
  if (pages <= 1) return null

  const go = (p) => {
    if (p >= 1 && p <= pages && p !== page) onPageChange(p)
  }

  const pad = (n) => String(n).padStart(2, '0')

  return (
    <div className="mt-6 flex items-center justify-between border-t border-line pt-5">
      <button type="button" className="btn" disabled={page <= 1} onClick={() => go(page - 1)}>
        ← prev
      </button>
      <span className="label">
        page <span className="text-phos">{pad(page)}</span> / {pad(pages)}
      </span>
      <button
        type="button"
        className="btn"
        disabled={page >= pages}
        onClick={() => go(page + 1)}
      >
        next →
      </button>
    </div>
  )
}
