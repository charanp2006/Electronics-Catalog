import { Loader, EmptyState, ErrorState } from '../components/States'

export { Loader, EmptyState, ErrorState }

export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="panel frame flex flex-wrap items-end justify-between gap-4 p-5">
      <div>
        {subtitle && <p className="label mb-1">{subtitle}</p>}
        <h1 className="font-display text-3xl tracking-wider text-ink uppercase">{title}</h1>
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  )
}

const STATUS_STYLES = {
  pending: 'border-dim text-dim',
  processing: 'border-sig text-sig',
  shipped: 'border-phos text-phos',
  delivered: 'border-phos text-phos',
  cancelled: 'border-alert text-alert',
  published: 'border-phos text-phos',
  hidden: 'border-alert/60 text-alert',
}

export function StatusChip({ status }) {
  const tone = STATUS_STYLES[status] || 'border-line-2 text-dim'
  return <span className={`chip ${tone}`}>{status || 'unknown'}</span>
}

export function Money({ value }) {
  return <span>₹{Number(value || 0).toLocaleString('en-IN')}</span>
}

export function Input({ label, value, onChange, type = 'text', step, placeholder, required }) {
  return (
    <label className="block">
      <span className="label mb-1.5 block">{label}</span>
      <input
        type={type}
        step={step}
        required={required}
        value={value ?? ''}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="field"
      />
    </label>
  )
}

export function TextArea({ label, value, onChange, rows = 3, placeholder }) {
  return (
    <label className="block">
      <span className="label mb-1.5 block">{label}</span>
      <textarea
        rows={rows}
        value={value ?? ''}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="field resize-y"
      />
    </label>
  )
}

export function Select({ label, value, onChange, options, placeholder }) {
  return (
    <label className="block">
      <span className="label mb-1.5 block">{label}</span>
      <select value={value ?? ''} onChange={(e) => onChange(e.target.value)} className="field">
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </label>
  )
}

export function Checkbox({ label, checked, onChange }) {
  return (
    <label className="flex cursor-pointer items-center gap-2">
      <input
        type="checkbox"
        checked={!!checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 accent-[#00ed64]"
      />
      <span className="label">{label}</span>
    </label>
  )
}
