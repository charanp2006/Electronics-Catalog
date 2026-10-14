import CountUp from './CountUp'

export function SecHead({ index, title, count, unit = 'REC', action, className = '' }) {
  return (
    <div className={`mb-6 flex flex-wrap items-end gap-x-4 gap-y-2 border-b border-line pb-3 ${className}`}>
      {index && (
        <span className="font-display text-2xl leading-none text-phos">
          [{String(index).padStart(2, '0')}]
        </span>
      )}
      <h2 className="text-sm font-medium tracking-[0.28em] text-ink uppercase">{title}</h2>
      <span className="hidden h-3 flex-1 sm:block" />
      {count !== undefined && count !== null && (
        <span className="label">
          {String(count).padStart(3, '0')} {unit}
        </span>
      )}
      {action}
    </div>
  )
}

export function Stat({ label, value, pad = 0, suffix, tone = 'phos' }) {
  const tones = { phos: 'text-phos', sig: 'text-sig', ink: 'text-ink' }
  return (
    <div className="flex flex-col gap-1">
      <span className="label">{label}</span>
      <span className={`font-display text-3xl leading-none ${tones[tone]}`}>
        {typeof value === 'number' ? (
          <CountUp value={value} pad={pad} />
        ) : (
          value
        )}
        {suffix && <span className="ml-1 text-base text-dim">{suffix}</span>}
      </span>
    </div>
  )
}

export function Leader({ label, value }) {
  return (
    <div className="flex items-end gap-2 text-sm">
      <span className="text-dim">{label}</span>
      <span className="leader" />
      <span className="text-ink">{value}</span>
    </div>
  )
}

export function Prompt({ children, className = '' }) {
  return (
    <span className={className}>
      <span className="text-phos">{'>'}</span> {children}
    </span>
  )
}
