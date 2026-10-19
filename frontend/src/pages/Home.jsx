import { Link, useNavigate } from 'react-router-dom'
import heroArt from '../assets/Neon_Tech_E-Commerce_Showcase.webp'
import { getBrands, getCategories, getFeatured } from '../services/api'
import { useApi } from '../hooks/useApi'
import ProductGrid from '../components/ProductGrid'
import { ErrorState, Loader } from '../components/States'
import { Frame } from '../components/ui/Frame'
import { Reveal } from '../components/ui/Reveal'
import Scramble from '../components/ui/Scramble'
import CountUp from '../components/ui/CountUp'
import GridBackdrop from '../components/ui/GridBackdrop'
import { SecHead } from '../components/ui/Blocks'

const BOOT = [
  'connection secured',
  'catalog synced',
  '12 products loaded',
  'price tracker online',
  'catalog ready',
]

export default function Home() {
  const navigate = useNavigate()
  const { data: categories } = useApi(getCategories, [])
  const { data: brands } = useApi(getBrands, [])
  const { data: featured, loading, error, refetch } = useApi(() => getFeatured(8), [])

  const totalUnits = (categories || []).reduce((sum, c) => sum + (c.product_count || 0), 0)

  return (
    <div className="space-y-14">
      {/* ---------------------------------------------------------- hero */}
      <section className="panel frame relative overflow-hidden">
        <GridBackdrop />

        {/* showcase art — sits above & behind the system-status panel */}
        <div className="pointer-events-none absolute inset-0 z-0" aria-hidden="true">
          <img
            src={heroArt}
            alt=""
            className="absolute right-1 top-0 h-full w-full object-cover object-top opacity-25 mix-blend-screen sm:w-3/4 sm:opacity-40 lg:w-[100%]"
            style={{
              WebkitMaskImage: 'linear-gradient(to left, black 40%, transparent 95%)',
              maskImage: 'linear-gradient(to left, black 40%, transparent 95%)',
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-bg/60 via-transparent to-transparent" />
        </div>

        <div className="relative grid gap-8 p-6 sm:p-10 lg:grid-cols-[1.5fr_1fr] lg:items-end">
          <div className="space-y-6">
            <Scramble
              text="> cold boot · electrohub catalog v2.0"
              className="label block text-phos"
            />
            <h1 className="font-display text-6xl leading-[0.85] tracking-tight text-ink uppercase sm:text-8xl">
              Hardware
              <br />
              <span className="text-phos glow">Decoded</span>
              <span className="blink text-phos">_</span>
            </h1>
            <p className="max-w-xl text-xs leading-relaxed text-dim sm:text-sm">
              A precision index of smartphones, laptops, audio and displays. Query the catalog,
              trace price history, and compare units — all in real time.
            </p>
            <div className="flex flex-wrap gap-2">
              <Link to="/products" className="btn btn-primary">
                [ browse catalog ]
              </Link>
              <button
                type="button"
                onClick={() => navigate('/products?category=smartphones')}
                className="btn"
              >
                [ query smartphones ]
              </button>
            </div>
          </div>

          <Frame
            label="system status"
            bodyClassName="p-4 space-y-3"
            style={{
              background: 'transparent',
              // backdropFilter: 'blur(6px)',
              // WebkitBackdropFilter: 'blur(6px)',
            }}
          >
            <div className="grid grid-cols-3 gap-3 text-2xl font-bold text-ink">
              <Metric label="units" value={totalUnits} />
              <Metric label="categories" value={(categories || []).length} />
              <Metric label="brands" value={(brands || []).length} />
            </div>
            <div className="hairline" />
            <div className="space-y-1 font-mono text-[11px] text-dim">
              {BOOT.map((line, i) => (
                <Reveal key={line} delay={0.15 + i * 0.12} y={6}>
                  <div className="flex gap-2">
                    <span className="text-sig">✓</span>
                    {line}
                  </div>
                </Reveal>
              ))}
            </div>
          </Frame>
        </div>
      </section>

      {/* --------------------------------------------------- categories */}
      <section>
        <SecHead index={2} title="index by category" count={(categories || []).length} unit="CAT" />
        <div className="panel grid sm:grid-cols-2">
          {(categories || []).map((c, i) => (
            <Link
              key={c.slug}
              to={`/products?category=${c.slug}`}
              className="group flex items-center gap-4 border-b border-line px-5 py-5 transition last:border-b-0 hover:bg-panel-2 sm:odd:border-r"
            >
              <span className="font-display text-2xl leading-none text-line-2 transition group-hover:text-phos">
                {String(i + 1).padStart(2, '0')}
              </span>
              <span className="font-display text-2xl leading-none text-ink uppercase transition group-hover:text-phos">
                {c.name}
              </span>
              <span className="leader hidden sm:block" />
              <span className="label whitespace-nowrap">
                {String(c.product_count || 0).padStart(2, '0')} units
              </span>
              <span className="text-phos transition group-hover:translate-x-1">→</span>
            </Link>
          ))}
        </div>
      </section>

      {/* ----------------------------------------------------- featured */}
      <section>
        <SecHead
          index={3}
          title="featured units"
          count={featured?.length}
          action={
            <Link
              to="/products"
              className="text-[10px] tracking-[0.2em] text-dim uppercase transition hover:text-phos"
            >
              [ view all → ]
            </Link>
          }
        />
        {loading && <Loader label="indexing units" />}
        {error && <ErrorState message={error} onRetry={refetch} />}
        {featured && featured.length > 0 && <ProductGrid products={featured} />}
      </section>
    </div>
  )
}

function Metric({ label, value }) {
  return (
    <div>
      <div className="font-display text-3xl leading-none text-phos">
        <CountUp value={value} pad={3} />
      </div>
      <div className="label mt-1">{label}</div>
    </div>
  )
}
