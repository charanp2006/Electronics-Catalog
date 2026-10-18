import axios from 'axios'

export const ADMIN_TOKEN_KEY = 'electrohub_admin_token'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ADMIN_TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const url = error?.config?.url || ''
    if (status === 401 && !url.includes('/auth/login')) {
      localStorage.removeItem(ADMIN_TOKEN_KEY)
      window.dispatchEvent(new Event('admin-unauthorized'))
    }
    return Promise.reject(error)
  }
)

export function extractError(error) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(', ')
  return error?.message || 'Something went wrong'
}

// Auth
export const adminLogin = (data) => api.post('/admin/auth/login', data).then((r) => r.data)
export const adminMe = () => api.get('/admin/auth/me').then((r) => r.data)

// Stats
export const getOverview = () => api.get('/admin/stats').then((r) => r.data)

// Products
export const listProducts = (params) =>
  api.get('/admin/products', { params }).then((r) => r.data)
export const getProductById = (id) => api.get(`/admin/products/${id}`).then((r) => r.data)
export const createProduct = (data) => api.post('/admin/products', data).then((r) => r.data)
export const updateProduct = (id, data) => api.put(`/admin/products/${id}`, data).then((r) => r.data)
export const deleteProduct = (id, hard = false) =>
  api.delete(`/admin/products/${id}`, { params: { hard } }).then((r) => r.data)

// Categories
export const listCategories = (params) =>
  api.get('/admin/categories', { params }).then((r) => r.data)
export const createCategory = (data) => api.post('/admin/categories', data).then((r) => r.data)
export const updateCategory = (id, data) =>
  api.put(`/admin/categories/${id}`, data).then((r) => r.data)
export const deleteCategory = (id) => api.delete(`/admin/categories/${id}`).then((r) => r.data)

// Brands
export const listBrands = (params) => api.get('/admin/brands', { params }).then((r) => r.data)
export const createBrand = (data) => api.post('/admin/brands', data).then((r) => r.data)
export const updateBrand = (id, data) => api.put(`/admin/brands/${id}`, data).then((r) => r.data)
export const deleteBrand = (id) => api.delete(`/admin/brands/${id}`).then((r) => r.data)

// Orders
export const listOrders = (params) => api.get('/admin/orders', { params }).then((r) => r.data)
export const getOrderById = (id) => api.get(`/admin/orders/${id}`).then((r) => r.data)
export const setOrderStatus = (id, status) =>
  api.patch(`/admin/orders/${id}/status`, { status }).then((r) => r.data)

// Reviews
export const listReviews = (params) => api.get('/admin/reviews', { params }).then((r) => r.data)
export const moderateReview = (productId, reviewId, data) =>
  api.patch(`/admin/reviews/${productId}/${reviewId}`, data).then((r) => r.data)
export const deleteReview = (productId, reviewId) =>
  api.delete(`/admin/reviews/${productId}/${reviewId}`).then((r) => r.data)

export default api
