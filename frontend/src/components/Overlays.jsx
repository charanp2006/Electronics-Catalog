export default function Overlays() {
  return (
    <div className="crt-overlay" aria-hidden="true">
      <div className="absolute inset-0 crt-grain" />
      <div className="absolute inset-0 crt-scanlines crt-flicker" />
      <div className="absolute inset-0 crt-vignette" />
    </div>
  )
}
