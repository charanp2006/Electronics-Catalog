export function Frame({ children, label, className = '', bodyClassName = '', as: Tag = 'div', ...rest }) {
  return (
    <Tag className={`panel frame relative ${className}`} {...rest}>
      {label && (
        <span className="absolute -top-2.5 left-4 z-10 bg-bg px-2 label text-phos">
          {label}
        </span>
      )}
      <div className={bodyClassName}>{children}</div>
    </Tag>
  )
}

export function Panel({ children, className = '', ...rest }) {
  return (
    <div className={`panel ${className}`} {...rest}>
      {children}
    </div>
  )
}

export function Tag({ children, className = '', tone = 'dim' }) {
  const tones = {
    dim: 'text-dim border-line-2',
    phos: 'text-phos border-phos/40',
    sig: 'text-sig border-sig/40',
    alert: 'text-alert border-alert/40',
  }
  return <span className={`chip ${tones[tone]} ${className}`}>{children}</span>
}
