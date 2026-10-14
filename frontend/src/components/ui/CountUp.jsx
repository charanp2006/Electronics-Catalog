import { useEffect, useRef } from 'react'
import gsap from 'gsap'

export default function CountUp({ value = 0, duration = 1.3, className = '', pad = 0 }) {
  const ref = useRef(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const state = { v: 0 }
    const tween = gsap.to(state, {
      v: value,
      duration,
      ease: 'power2.out',
      onUpdate: () => {
        el.textContent = String(Math.round(state.v)).padStart(pad, '0')
      },
    })
    return () => tween.kill()
  }, [value, duration, pad])

  return (
    <span ref={ref} className={className}>
      {String(value).padStart(pad, '0')}
    </span>
  )
}
