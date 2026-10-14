import { useEffect, useRef } from 'react'

const GLYPHS = '!<>-_\\/[]{}—=+*^?#01ABCDEF'

/**
 * Character-scramble reveal, terminal style. Runs once on mount.
 */
export default function Scramble({ text, className = '', speed = 1, as: Tag = 'span' }) {
  const ref = useRef(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    let frame = 0
    let raf
    const queue = text.split('').map((char, i) => ({
      to: char,
      start: Math.floor(i * (6 / speed)),
      end: Math.floor(i * (6 / speed)) + 14 + Math.floor(Math.random() * 10),
      char: '',
    }))

    const tick = () => {
      let output = ''
      let done = 0
      for (const q of queue) {
        if (frame >= q.end) {
          done++
          output += q.to
        } else if (frame >= q.start) {
          if (!q.char || Math.random() < 0.3) {
            q.char = q.to === ' ' ? ' ' : GLYPHS[Math.floor(Math.random() * GLYPHS.length)]
          }
          output += q.char
        } else {
          output += ' '
        }
      }
      el.textContent = output
      if (done === queue.length) return
      frame++
      raf = requestAnimationFrame(tick)
    }
    tick()
    return () => cancelAnimationFrame(raf)
  }, [text, speed])

  return (
    <Tag ref={ref} className={className}>
      {text}
    </Tag>
  )
}
