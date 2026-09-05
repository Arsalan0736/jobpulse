import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { listJobs } from '../api'
import JobCard from '../components/JobCard'
import SearchFilters from '../components/SearchFilters'
import toast from 'react-hot-toast'

export default function Landing() {
  const [params, setParams] = useSearchParams()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [count, setCount] = useState(0)

  const q = params.get('q') || ''
  const location = params.get('location') || ''
  const seniority = params.get('seniority_level') || ''

  useEffect(() => {
    setLoading(true)
    listJobs({ q, location, seniority_level: seniority, page, page_size: 20 })
      .then((res) => {
        setJobs(res.data.results)
        setCount(res.data.count)
      })
      .catch((err) => toast.error('Failed to load jobs'))
      .finally(() => setLoading(false))
  }, [q, location, seniority, page])

  const setFilters = (key, value) => {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value)
    else next.delete(key)
    setParams(next)
    setPage(1)
  }

  return (
    <div>
      <section className="relative overflow-hidden border-b border-ink-800">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-amber-glow/8 blur-[120px]" />
        </div>
        <div className="relative max-w-[1400px] mx-auto px-6 pt-24 pb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-3xl"
          >
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-amber-glow mb-6">
              AI job aggregation
            </p>
            <h1 className="text-5xl md:text-6xl font-semibold tracking-tightest text-ink-100 leading-[1.05]">
              Every role, summarized.
              <br />
              <span className="text-ink-400">Matched to you.</span>
            </h1>
            <p className="text-lg text-ink-300 leading-relaxed mt-6 max-w-xl">
              JobPulse pulls roles from public job boards, runs each one through
              Gemini, and ranks them against your resume. Less reading, more
              interviewing.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="max-w-[1400px] mx-auto px-6 py-10">
        <SearchFilters
          q={q}
          location={location}
          seniority={seniority}
          onQ={(v) => setFilters('q', v)}
          onLocation={(v) => setFilters('location', v)}
          onSeniority={(v) => setFilters('seniority_level', v)}
        />

        <div className="flex items-center justify-between mb-6">
          <p className="text-sm font-mono text-ink-400">
            {loading ? 'Loading…' : `${count} jobs`}
          </p>
        </div>

        <AnimatePresence mode="wait">
          {loading ? (
            <SkeletonGrid key="skel" />
          ) : jobs.length === 0 ? (
            <EmptyState key="empty" />
          ) : (
            <motion.div
              key="grid"
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              {jobs.map((job, i) => (
                <JobCard key={job.id} job={job} index={i} />
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {count > 20 && (
          <div className="flex justify-center gap-2 mt-10">
            <button
              disabled={page === 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="px-4 py-2 text-sm border border-ink-800 rounded-md text-ink-300 hover:text-ink-100 hover:border-ink-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm font-mono text-ink-400">
              {page} / {Math.ceil(count / 20)}
            </span>
            <button
              disabled={page * 20 >= count}
              onClick={() => setPage((p) => p + 1)}
              className="px-4 py-2 text-sm border border-ink-800 rounded-md text-ink-300 hover:text-ink-100 hover:border-ink-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        )}
      </section>
    </div>
  )
}

function SkeletonGrid() {
  return (
    <motion.div
      key="skel"
      className="grid grid-cols-1 md:grid-cols-2 gap-4"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="p-6 rounded-xl border border-ink-800 bg-ink-900/50 animate-pulse"
        >
          <div className="h-5 w-3/4 bg-ink-800 rounded mb-3" />
          <div className="h-3 w-1/2 bg-ink-800 rounded mb-6" />
          <div className="h-3 w-full bg-ink-800 rounded mb-2" />
          <div className="h-3 w-5/6 bg-ink-800 rounded mb-6" />
          <div className="flex gap-2">
            <div className="h-5 w-12 bg-ink-800 rounded" />
            <div className="h-5 w-12 bg-ink-800 rounded" />
            <div className="h-5 w-12 bg-ink-800 rounded" />
          </div>
        </div>
      ))}
    </motion.div>
  )
}

function EmptyState() {
  return (
    <motion.div
      key="empty"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="py-20 text-center"
    >
      <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink-500 mb-3">
        No matches
      </p>
      <p className="text-ink-300">Try clearing the filters or scraping more sources.</p>
    </motion.div>
  )
}