import { useState } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { login } from '../api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { loginWithToken } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/'

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await login({ email, password })
      loginWithToken(data.token, data.user)
      toast.success('Welcome back')
      navigate(from, { replace: true })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto px-6 py-20">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-3xl font-semibold tracking-tight text-ink-100 mb-2">
          Sign in
        </h1>
        <p className="text-ink-400 mb-8">Continue your job search.</p>

        <form onSubmit={onSubmit} className="space-y-4">
          <Field
            label="Email"
            type="email"
            value={email}
            onChange={setEmail}
            required
          />
          <Field
            label="Password"
            type="password"
            value={password}
            onChange={setPassword}
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 rounded-md bg-ink-100 text-ink-950 font-medium hover:bg-amber-glow transition-colors disabled:opacity-50"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="text-sm text-ink-400 mt-6 text-center">
          New here?{' '}
          <Link to="/register" className="text-amber-glow hover:underline">
            Create an account
          </Link>
        </p>
      </motion.div>
    </div>
  )
}

function Field({ label, type, value, onChange, required }) {
  return (
    <div>
      <label className="block text-xs font-mono uppercase tracking-wider text-ink-400 mb-2">
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        className="w-full h-11 px-4 bg-ink-900 border border-ink-800 rounded-md text-ink-100 focus:border-amber-glow focus:outline-none transition-colors"
      />
    </div>
  )
}