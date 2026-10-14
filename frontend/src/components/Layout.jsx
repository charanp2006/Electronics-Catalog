import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { motion } from 'motion/react'
import { useLenis } from 'lenis/react'
import Navbar from './Navbar'
import Footer from './Footer'
import Ticker from './Ticker'
import StatusBar from './StatusBar'
import Overlays from './Overlays'
import { EASE } from './ui/Reveal'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import { useWishlist } from '../context/WishlistContext'
import { useCompare } from '../context/CompareContext'

export default function Layout() {
  const { user } = useAuth()
  const { cart } = useCart()
  const { count: wishCount } = useWishlist()
  const { count: compareCount, notice } = useCompare()
  const location = useLocation()
  const lenis = useLenis()

  useEffect(() => {
    lenis?.scrollTo(0, { immediate: true })
  }, [location.pathname, lenis])

  return (
    <>
      <Overlays />
      <div className="relative z-10 flex min-h-screen flex-col pb-7">
        <Navbar
          user={user}
          cartCount={cart?.count || 0}
          wishCount={wishCount}
          compareCount={compareCount}
        />
        <Ticker />
        <motion.main
          key={location.pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: EASE }}
          className="mx-auto w-full max-w-[1400px] flex-1 px-4 py-8"
        >
          <Outlet />
        </motion.main>
        <Footer />
      </div>
      <StatusBar />
      {notice && (
        <div className="panel frame fixed bottom-10 left-1/2 z-[70] -translate-x-1/2 px-4 py-2 text-xs tracking-[0.14em] text-phos uppercase">
          {notice}
        </div>
      )}
    </>
  )
}
