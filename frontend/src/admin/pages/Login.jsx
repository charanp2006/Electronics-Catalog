import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock } from 'lucide-react'
import { useAdminAuth } from '../AdminAuthContext'
import { extractError } from '../api'
import { Input } from '../ui'

export default function Login() {
  const { login } = useAdminAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await login({ email, password })
      navigate('/admin-cms', { replace: true })
    } catch (err) {
      setError(extractError(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form onSubmit={submit} className="panel frame w-full max-w-sm space-y-4 p-6">
        <div className="text-center">
          <p className="font-display text-3xl tracking-wider text-phos uppercase glow">electrohub</p>
          <p className="label mt-1 flex items-center justify-center gap-1">
            <Lock size={11} /> admin access
          </p>
        </div>

        {error && (
          <p className="border border-alert/40 bg-alert/5 px-3 py-2 text-xs text-alert">{error}</p>
        )}

        <Input label="email" type="email" required value={email} onChange={setEmail} />
        <Input label="password" type="password" required value={password} onChange={setPassword} />

        <button type="submit" disabled={busy} className="btn btn-primary w-full">
          {busy ? 'authenticating…' : 'authenticate'}
        </button>
      </form>
    </div>
  )
}
