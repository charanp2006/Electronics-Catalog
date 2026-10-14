import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { useAuth } from './AuthContext'
import { addToCartApi, clearCartApi, getCart, removeCartApi, updateCartApi } from '../services/api'

const emptyCart = { items: [], subtotal: 0, discount: 0, total: 0, count: 0 }

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const { user } = useAuth()
  const [cart, setCart] = useState(emptyCart)
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    if (!user) {
      setCart(emptyCart)
      return
    }
    setLoading(true)
    try {
      setCart(await getCart())
    } catch {
      setCart(emptyCart)
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    refresh()
  }, [refresh])

  const addItem = useCallback(
    async (product, quantity = 1) => {
      const id = product._id || product.id
      setCart(await addToCartApi(id, quantity))
    },
    []
  )

  const updateItem = useCallback(async (productId, quantity) => {
    setCart(await updateCartApi(productId, quantity))
  }, [])

  const removeItem = useCallback(async (productId) => {
    setCart(await removeCartApi(productId))
  }, [])

  const clear = useCallback(async () => {
    setCart(await clearCartApi())
  }, [])

  const hasItem = (product) =>
    cart.items.some((i) => i.product_id === (product._id || product.id))

  return (
    <CartContext.Provider
      value={{ cart, loading, refresh, addItem, updateItem, removeItem, clear, hasItem }}
    >
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => useContext(CartContext)
