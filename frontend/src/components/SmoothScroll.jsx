import { ReactLenis } from 'lenis/react'

export default function SmoothScroll({ children }) {
  return (
    <ReactLenis
      root
      options={{ lerp: 0.09, duration: 1.15, smoothWheel: true, wheelMultiplier: 1 }}
    >
      {children}
    </ReactLenis>
  )
}
