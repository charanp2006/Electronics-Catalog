import { useEffect, useRef } from 'react'
import gsap from 'gsap'

export default function Marquee({ items = [], speed = 26, className = '', itemClassName = '' }) {
  const trackRef = useRef(null)

  useEffect(() => {
    const el = trackRef.current
    if (!el) return
    const tween = gsap.to(el, {
      xPercent: -50,
      ease: 'none',
      duration: speed,
      repeat: -1,
    })
    return () => tween.kill()
  }, [speed])

  const doubled = [...items, ...items]

  return (
    <div className={`ticker overflow-hidden ${className}`}>
      <div ref={trackRef} className="flex w-max items-center">
        {doubled.map((item, i) => (
          <span key={i} className={`flex items-center whitespace-nowrap ${itemClassName}`}>
            <span className="mx-4 text-phos">◆</span>
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}
