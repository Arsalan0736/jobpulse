import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { savedJobs } from '../api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import JobCard from '../components/JobCard'

export default function SavedJobs() {
  const { isAuthenticated } = useAuth()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: { pathname: '/saved' } }} replace />
  }

  useEffect(() => {
    savedJobs()
      .then((r) => setJobs(r.data.results))
      .catch(() => toast.error('Failed to load saved jobs'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-12">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-3xl font-semibold tracking-tight text-ink-100 mb-2">
          Saved jobs
        </h1>
        <p className="text-ink-400 mb-10">
          {jobs.length > 0
            ? `${jobs.length} roles, ranked by resume match.`
            : 'No saved jobs yet.'}
        </p>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="h-48 rounded-xl border border-ink-800 bg-ink-900/50 animate-pulse"
              />
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="py-20 text-center border border-dashed border-ink-800 rounded-xl">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink-500 mb-3">
              Empty
            </p>
            <p className="text-ink-300 mb-6">
              Browse jobs and save the ones worth applying to.
            </p>
            <Link
              to="/"
              className="inline-block px-5 h-10 leading-10 rounded-md bg-ink-100 text-ink-950 font-medium hover:bg-amber-glow transition-colors"
            >
              Browse jobs
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((job, i) => (
              <JobCard key={job.id} job={job} index={i} />
            ))}
          </div>
        )}
      </motion.div>
    </div>
  )
}