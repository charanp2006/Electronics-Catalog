import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useWishlist } from '../context/WishlistContext'
import ProductGrid from '../components/ProductGrid'
import { EmptyState } from '../components/States'
import { SecHead } from '../components/ui/Blocks'

export default function Wishlist() {
  const { user } = useAuth()
  const { items } = useWishlist()

  if (!user) {
    return (
      <EmptyState
        title="access denied"
        message="Authenticate to inspect your saved units."
        action={
          <Link to="/login" className="btn btn-primary">
            [ authenticate ]
          </Link>
        }
      />
    )
  }

  return (
    <div className="space-y-6">
      <SecHead
        index={1}
        title="saved units"
        count={items.length}
        action={
          <Link to="/products" className="text-[10px] tracking-[0.2em] text-dim uppercase hover:text-phos">
            [ browse catalog → ]
          </Link>
        }
      />
      {items.length === 0 ? (
        <EmptyState
          title="nothing saved"
          message="Mark units with ♥ to keep them on this shelf."
          action={
            <Link to="/products" className="btn btn-primary">
              [ browse catalog ]
            </Link>
          }
        />
      ) : (
        <ProductGrid products={items} />
      )}
    </div>
  )
}
