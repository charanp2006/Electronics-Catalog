export function Loader({ label = 'loading' }) {
  return (
    <div className="flex flex-col items-center gap-3 py-20">
      <div className="h-1 w-48 overflow-hidden border border-line bg-bg">
        <div className="scanbar" />
      </div>
      <p className="label">
        {label}
        <span className="blink text-phos">_</span>
      </p>
    </div>
  )
}

export function EmptyState({ title = 'no data', message, action }) {
  return (
    <div className="panel frame flex flex-col items-center gap-3 px-6 py-16 text-center">
      <p className="font-display text-2xl tracking-wider text-dim uppercase">[ {title} ]</p>
      {message && <p className="max-w-md text-xs leading-relaxed text-dim">{message}</p>}
      {action}
    </div>
  )
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="panel frame flex flex-col items-center gap-3 border-alert/40 px-6 py-14 text-center">
      <p className="font-display text-2xl tracking-wider text-alert uppercase">!! error</p>
      <p className="max-w-md text-xs text-dim">{message}</p>
      {onRetry && (
        <button type="button" onClick={onRetry} className="btn btn-danger">
          retry
        </button>
      )}
    </div>
  )
}
