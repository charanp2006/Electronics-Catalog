import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { ADMIN_TOKEN_KEY, adminLogin, adminMe } from './api'

const AdminAuthContext = createContext(null)

export function AdminAuthProvider({ children }) {
  const [admin, setAdmin] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!localStorage.getItem(ADMIN_TOKEN_KEY)) {
      setLoading(false)
      return
    }
    adminMe()
      .then(setAdmin)
      .catch(() => localStorage.removeItem(ADMIN_TOKEN_KEY))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    const onUnauthorized = () => setAdmin(null)
    window.addEventListener('admin-unauthorized', onUnauthorized)
    return () => window.removeEventListener('admin-unauthorized', onUnauthorized)
  }, [])

  const login = useCallback(async (credentials) => {
    const data = await adminLogin(credentials)
    localStorage.setItem(ADMIN_TOKEN_KEY, data.access_token)
    setAdmin(data.admin)
    return data.admin
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(ADMIN_TOKEN_KEY)
    setAdmin(null)
  }, [])

  return (
    <AdminAuthContext.Provider value={{ admin, loading, login, logout }}>
      {children}
    </AdminAuthContext.Provider>
  )
}

export const useAdminAuth = () => useContext(AdminAuthContext)
