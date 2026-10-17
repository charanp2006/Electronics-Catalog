import { useEffect, useState } from 'react'

export default function SearchBar({
  initial = '',
  onSubmit,
  placeholder = 'grep units…',
  className = '',
}) {
  const [value, setValue] = useState(initial)

  useEffect(() => {
    setValue(initial)
  }, [initial])

  const submit = (e) => {
    e.preventDefault()
    onSubmit?.(value.trim())
  }

  return (
    <form
      onSubmit={submit}
      className={`flex items-center border border-line-2 bg-bg transition focus-within:border-phos ${className}`}
    >
      <span className="select-none pl-2.5 pr-1.5 text-phos">{'>'}</span>
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-transparent py-1.5 pr-2 text-xs text-ink outline-none placeholder:text-[#5c6c75]"
      />
      <button
        type="submit"
        className="border-l border-line-2 px-3 py-1.5 text-[10px] tracking-[0.2em] text-dim uppercase transition hover:bg-phos hover:text-bg"
      >
        go
      </button>
    </form>
  )
}
