import { createContext, useCallback, useContext, useEffect, useState } from 'react'

const KEY = 'electrohub_compare'
const MAX = 4

const CompareContext = createContext(null)

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || '[]')
  } catch {
    return []
  }
}

export function CompareProvider({ children }) {
  const [items, setItems] = useState(load)
  const [notice, setNotice] = useState(null)

  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify(items))
  }, [items])

  const has = (product) => items.some((i) => i._id === (product._id || product.id))

  const add = useCallback(
    (product) => {
      const id = product._id || product.id
      if (items.some((i) => i._id === id)) return
      if (items.length >= MAX) {
        setNotice(`You can compare up to ${MAX} products. Remove one first.`)
        setTimeout(() => setNotice(null), 3000)
        return
      }
      setItems((prev) => [
        ...prev,
        {
          _id: id,
          slug: product.slug,
          name: product.name,
          image: product.image,
          price: product.price,
          discount_price: product.discount_price,
          brand: product.brand,
          average_rating: product.average_rating,
        },
      ])
    },
    [items]
  )

  const remove = useCallback((id) => {
    setItems((prev) => prev.filter((i) => i._id !== id))
  }, [])

  const clear = useCallback(() => setItems([]), [])

  return (
    <CompareContext.Provider value={{ items, count: items.length, max: MAX, has, add, remove, clear, notice }}>
      {children}
    </CompareContext.Provider>
  )
}

export const useCompare = () => useContext(CompareContext)
