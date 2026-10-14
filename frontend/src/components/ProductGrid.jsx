import { useNavigate } from 'react-router-dom'
import { motion } from 'motion/react'
import ProductCard from './ProductCard'
import { staggerChild, staggerParent } from './ui/Reveal'
import { useCart } from '../context/CartContext'
import { useWishlist } from '../context/WishlistContext'
import { useCompare } from '../context/CompareContext'
import { useAuth } from '../context/AuthContext'

export default function ProductGrid({ products = [] }) {
  const navigate = useNavigate()
  const { addItem } = useCart()
  const { isWished, toggle } = useWishlist()
  const { add: addCompare } = useCompare()
  const { user } = useAuth()

  const requireAuth = (action) => {
    if (!user) {
      navigate('/login', { state: { from: window.location.pathname } })
      return
    }
    action()
  }

  return (
    <motion.div
      variants={staggerParent}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-60px' }}
      className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
    >
      {products.map((p, i) => (
        <motion.div key={p._id} variants={staggerChild} className="h-full">
          <ProductCard
            product={p}
            index={i}
            wished={user ? isWished(p) : false}
            onAddToCart={(prod) => requireAuth(() => addItem(prod, 1))}
            onToggleWishlist={(prod) => requireAuth(() => toggle(prod))}
            onAddToCompare={addCompare}
          />
        </motion.div>
      ))}
    </motion.div>
  )
}
