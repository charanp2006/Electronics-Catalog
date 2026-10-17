import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('electrohub_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use((response) => {
  const contentType = response.headers?.['content-type'] || ''
  if (contentType.includes('text/html')) {
    return Promise.reject(
      new Error(
        'API returned HTML instead of JSON. Set VITE_API_URL to your backend URL (including /api/v1) and redeploy.'
      )
    )
  }
  return response
})

export function extractError(error) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(', ')
  return error?.message || 'Something went wrong'
}

// Catalog
export const getProducts = (params) => api.get('/products/', { params }).then((r) => r.data)
export const getProduct = (slug) => api.get(`/products/${slug}`).then((r) => r.data)
export const getFeatured = (limit = 8) =>
  api.get('/products/featured', { params: { limit } }).then((r) => r.data)
export const getRelated = (slug, limit = 4) =>
  api.get(`/products/${slug}/related`, { params: { limit } }).then((r) => r.data)
export const getCategories = () => api.get('/categories/').then((r) => r.data)
export const getBrands = () => api.get('/brands/').then((r) => r.data)

// Auth
export const registerUser = (data) => api.post('/auth/register', data).then((r) => r.data)
export const loginUser = (data) => api.post('/auth/login', data).then((r) => r.data)
export const getMe = () => api.get('/auth/me').then((r) => r.data)

// Cart
export const getCart = () => api.get('/cart/').then((r) => r.data)
export const addToCartApi = (product_id, quantity = 1) =>
  api.post('/cart/add', { product_id, quantity }).then((r) => r.data)
export const updateCartApi = (product_id, quantity) =>
  api.put('/cart/update', { product_id, quantity }).then((r) => r.data)
export const removeCartApi = (product_id) =>
  api.delete(`/cart/remove/${product_id}`).then((r) => r.data)
export const clearCartApi = () => api.delete('/cart/clear').then((r) => r.data)

// Wishlist
export const getWishlist = () => api.get('/wishlist/').then((r) => r.data)
export const addWishlistApi = (product_id) =>
  api.post('/wishlist/add', { product_id }).then((r) => r.data)
export const removeWishlistApi = (product_id) =>
  api.delete(`/wishlist/remove/${product_id}`).then((r) => r.data)

// Reviews
export const addReviewApi = (slug, data) =>
  api.post(`/products/${slug}/reviews`, data).then((r) => r.data)

// Orders
export const createOrderApi = (data) => api.post('/orders/', data).then((r) => r.data)
export const getOrders = () => api.get('/orders/').then((r) => r.data)

export default api
