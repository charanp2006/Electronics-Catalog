import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

export default function StatusBar() {
  const [now, setNow] = useState(() => new Date())
  const { pathname } = useLocation()

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 border-t border-line bg-bg/95 backdrop-blur">
      <div className="mx-auto flex h-7 max-w-[1400px] items-center gap-4 overflow-hidden px-4 text-[10px] tracking-[0.18em] uppercase text-dim">
        <span className="flex items-center gap-2">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-sig" />
          online
        </span>
        <span className="hidden sm:inline">db: mongodb://local</span>
        <span className="flex-1" />
        <span className="hidden md:inline">fastapi · pymongo · react</span>
        <span className="truncate text-phos">{pathname}</span>
        <span className="hidden sm:inline tabular-nums">{now.toLocaleTimeString('en-GB')}</span>
      </div>
    </div>
  )
}
