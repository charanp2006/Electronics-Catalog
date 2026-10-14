const OPTIONS = [
  { value: 'newest', label: 'newest' },
  { value: 'price_asc', label: 'price ↑' },
  { value: 'price_desc', label: 'price ↓' },
  { value: 'rating_desc', label: 'top rated' },
]

export default function SortDropdown({ value, onChange }) {
  return (
    <label className="flex items-center gap-2">
      <span className="label hidden sm:inline">sort</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="border border-line-2 bg-bg px-3 py-1.5 text-xs tracking-[0.1em] text-ink uppercase outline-none transition focus:border-phos"
      >
        {OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  )
}
