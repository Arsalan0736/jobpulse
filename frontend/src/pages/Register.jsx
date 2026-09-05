import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { register } from '../api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Register() {
  const [form, setForm] = useState({
    email: '',
    name: '',
    password: '',
    password_confirm: '',
  })
  const [loading, setLoading] = useState(false)
  const { loginWithToken } = useAuth()
  const navigate = useNavigate()

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await register(form)
      loginWithToken(data.token, data.user)
      toast.success('Account created')
      navigate('/')
    } catch (err) {
      const data = err.response?.data
      if (data && typeof data === 'object') {
        const first = Object.values(data)[0]
        const msg = Array.isArray(first) ? first[0] : first
        toast.error(msg || 'Registration failed')
      } else {
        toast.error('Registration failed')
      }
    } finally {
      setLoading(false)
    }
  }

  const set = (key) => (v) => setForm({ ...form, [key]: v })

  return (
    <div className="max-w-md mx-auto px-6 py-20">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-3xl font-semibold tracking-tight text-ink-100 mb-2">
          Create account
        </h1>
        <p className="text-ink-400 mb-8">Save jobs, upload your resume, get matched.</p>

        <form onSubmit={onSubmit} className="space-y-4">
          <Field label="Name" value={form.name} onChange={set('name')} />
          <Field label="Email" type="email" value={form.email} onChange={set('email')} required />
          <Field label="Password" type="password" value={form.password} onChange={set('password')} required />
          <Field
            label="Confirm password"
            type="password"
            value={form.password_confirm}
            onChange={set('password_confirm')}
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 rounded-md bg-ink-100 text-ink-950 font-medium hover:bg-amber-glow transition-colors disabled:opacity-50"
          >
            {loading ? 'Creating…' : 'Create account'}
          </button>
        </form>

        <p className="text-sm text-ink-400 mt-6 text-center">
          Already have one?{' '}
          <Link to="/login" className="text-amber-glow hover:underline">
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  )
}

function Field({ label, type = 'text', value, onChange, required }) {
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