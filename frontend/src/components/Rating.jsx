export default function Rating({ value = 0, count, showValue = true, className = '' }) {
  const filled = Math.max(0, Math.min(5, Math.round(value || 0)))
  return (
    <span className={`inline-flex items-center gap-2 text-xs ${className}`}>
      <span className="tracking-[-1px] text-phos" aria-hidden="true">
        {'■'.repeat(filled)}
        <span className="text-line-2">{'□'.repeat(5 - filled)}</span>
      </span>
      {showValue && (
        <span className="text-dim tabular-nums">
          {value ? Number(value).toFixed(1) : '0.0'}
          {count !== undefined && ` (${count})`}
        </span>
      )}
    </span>
  )
}

export function RatingInput({ value = 5, onChange }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => onChange(n)}
            aria-label={`${n} star`}
            className={`text-lg leading-none transition ${
              n <= value ? 'text-phos' : 'text-line-2 hover:text-phos/50'
            }`}
          >
            {n <= value ? '■' : '□'}
          </button>
        ))}
      </div>
      <span className="label">{value}/5</span>
    </div>
  )
}
