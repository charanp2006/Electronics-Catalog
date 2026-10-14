import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { useAuth } from './AuthContext'
import { addWishlistApi, getWishlist, removeWishlistApi } from '../services/api'

const WishlistContext = createContext(null)

export function WishlistProvider({ children }) {
  const { user } = useAuth()
  const [items, setItems] = useState([])

  const refresh = useCallback(async () => {
    if (!user) {
      setItems([])
      return
    }
    try {
      setItems(await getWishlist())
    } catch {
      setItems([])
    }
  }, [user])

  useEffect(() => {
    refresh()
  }, [refresh])

  const isWished = (product) => items.some((i) => i._id === (product._id || product.id))

  const toggle = useCallback(async (product) => {
    const id = product._id || product.id
    const present = items.some((i) => i._id === id)
    if (present) {
      await removeWishlistApi(id)
    } else {
      await addWishlistApi(id)
    }
    await refresh()
  }, [items, refresh])

  return (
    <WishlistContext.Provider value={{ items, count: items.length, isWished, toggle, refresh }}>
      {children}
    </WishlistContext.Provider>
  )
}

export const useWishlist = () => useContext(WishlistContext)
