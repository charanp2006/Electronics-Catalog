import Marquee from './ui/Marquee'

const ITEMS = [
  'SYSTEM ONLINE',
  'MONGODB 7.x DOCUMENT STORE',
  '12 UNITS INDEXED',
  'PRICE-TRACKING ACTIVE',
  'DEMO CHECKOUT — NO REAL PAYMENT',
  'FULL-TEXT SEARCH ENABLED',
  'FASTAPI · PYMONGO · REACT',
  'FREE SHIPPING OVER ₹50,000',
]

export default function Ticker() {
  return (
    <div className="border-b border-line bg-panel/60">
      <Marquee
        items={ITEMS}
        speed={34}
        className="py-1.5 text-[10px] tracking-[0.28em] text-dim uppercase"
      />
    </div>
  )
}
