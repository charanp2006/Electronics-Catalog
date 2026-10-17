import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { extractError } from '../services/api'
import { Frame } from '../components/ui/Frame'
import Field from '../components/ui/Field'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(form)
      navigate(location.state?.from || '/')
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-md py-10">
      <Frame label="auth://login" bodyClassName="space-y-5 p-6">
        <div className="space-y-1">
          <span className="label text-phos">~/access</span>
          <h1 className="font-display text-4xl leading-none text-ink uppercase">Access terminal</h1>
          <p className="text-xs text-dim">Input operator credentials to continue.</p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <Field
            label="email"
            type="email"
            value={form.email}
            onChange={(v) => setForm({ ...form, email: v })}
          />
          <Field
            label="password"
            type="password"
            value={form.password}
            onChange={(v) => setForm({ ...form, password: v })}
          />
          {error && <p className="text-xs text-alert">!! {error}</p>}
          <button type="submit" disabled={loading} className="btn btn-primary w-full">
            {loading ? 'authenticating…' : '[ sign in ]'}
          </button>
        </form>

        <div className="hairline" />
        <p className="text-xs text-dim">
          no account?{' '}
          <Link to="/register" className="text-phos hover:underline">
            register operator
          </Link>
        </p>
      </Frame>
    </div>
  )
}
