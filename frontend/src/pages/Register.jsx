import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { extractError } from '../services/api'
import { Frame } from '../components/ui/Frame'
import Field from '../components/ui/Field'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', username: '', email: '', password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await register(form)
      navigate('/')
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  const set = (key) => (v) => setForm({ ...form, [key]: v })

  return (
    <div className="mx-auto max-w-md py-10">
      <Frame label="auth://register" bodyClassName="space-y-5 p-6">
        <div className="space-y-1">
          <span className="label text-phos">~/access</span>
          <h1 className="font-display text-4xl leading-none text-ink uppercase">New operator</h1>
          <p className="text-xs text-dim">Provision a new operator profile.</p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <Field label="full name" value={form.name} onChange={set('name')} />
          <Field label="username" value={form.username} onChange={set('username')} />
          <Field label="email" type="email" value={form.email} onChange={set('email')} />
          <Field label="password" type="password" value={form.password} onChange={set('password')} />
          {error && <p className="text-xs text-alert">!! {error}</p>}
          <button type="submit" disabled={loading} className="btn btn-primary w-full">
            {loading ? 'provisioning…' : '[ create account ]'}
          </button>
        </form>

        <div className="hairline" />
        <p className="text-xs text-dim">
          already provisioned?{' '}
          <Link to="/login" className="text-phos hover:underline">
            sign in
          </Link>
        </p>
      </Frame>
    </div>
  )
}
