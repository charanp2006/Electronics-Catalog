import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { AdminAuthProvider, useAdminAuth } from './AdminAuthContext'
import AdminLayout from './AdminLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import ProductForm from './pages/ProductForm'
import Categories from './pages/Categories'
import Brands from './pages/Brands'
import Orders from './pages/Orders'
import OrderDetail from './pages/OrderDetail'
import Reviews from './pages/Reviews'
import { Loader } from './ui'

function RequireAdmin() {
  const { admin, loading } = useAdminAuth()
  if (loading) return <Loader label="verifying session" />
  if (!admin) return <Navigate to="/admin-cms/login" replace />
  return <Outlet />
}

export default function AdminApp() {
  return (
    <AdminAuthProvider>
      <Routes>
        <Route path="login" element={<Login />} />
        <Route element={<RequireAdmin />}>
          <Route element={<AdminLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="products" element={<Products />} />
            <Route path="products/new" element={<ProductForm />} />
            <Route path="products/:id" element={<ProductForm />} />
            <Route path="categories" element={<Categories />} />
            <Route path="brands" element={<Brands />} />
            <Route path="orders" element={<Orders />} />
            <Route path="orders/:id" element={<OrderDetail />} />
            <Route path="reviews" element={<Reviews />} />
          </Route>
        </Route>
      </Routes>
    </AdminAuthProvider>
  )
}
