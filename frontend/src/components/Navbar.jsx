import { Link, NavLink, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="sticky top-0 z-40 backdrop-blur-xl bg-ink-950/70 border-b border-ink-800">
      <nav className="max-w-[1400px] mx-auto h-16 px-6 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <motion.div
            whileHover={{ rotate: 90 }}
            transition={{ type: 'spring', stiffness: 200, damping: 12 }}
            className="w-7 h-7 rounded-md bg-amber-glow flex items-center justify-center"
          >
            <span className="font-mono font-bold text-ink-950 text-sm">P</span>
          </motion.div>
          <span className="font-semibold text-ink-100 tracking-tight">JobPulse</span>
          <span className="font-mono text-[10px] text-ink-400 ml-1 hidden sm:inline">
            v0.1
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-1">
          {isAuthenticated && (
            <>
              <NavTab to="/saved">Saved</NavTab>
              <NavTab to="/resume">Resume</NavTab>
              <NavTab to="/analytics">Trends</NavTab>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <button
              onClick={() => {
                logout()
                navigate('/')
              }}
              className="text-sm px-3 py-1.5 text-ink-300 hover:text-ink-100 transition-colors"
            >
              Sign out
            </button>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm px-3 py-1.5 text-ink-300 hover:text-ink-100 transition-colors"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="text-sm px-4 py-1.5 rounded-md bg-ink-100 text-ink-950 font-medium hover:bg-amber-glow transition-colors"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}

function NavTab({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `relative px-3 py-1.5 text-sm transition-colors ${
          isActive ? 'text-ink-100' : 'text-ink-400 hover:text-ink-200'
        }`
      }
    >
      {({ isActive }) => (
        <>
          {children}
          {isActive && (
            <motion.span
              layoutId="nav-underline"
              className="absolute left-3 right-3 -bottom-px h-px bg-amber-glow"
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            />
          )}
        </>
      )}
    </NavLink>
  )
}