import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { getJob, saveJob, unsaveJob } from '../api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function JobDetail() {
  const { id } = useParams()
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    getJob(id)
      .then((res) => setJob(res.data))
      .catch((err) => {
        toast.error('Job not found')
        navigate('/')
      })
      .finally(() => setLoading(false))
  }, [id])

  const onSave = async () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: { pathname: `/jobs/${id}` } } })
      return
    }
    setSaving(true)
    try {
      const { data } = await saveJob(id)
      setSaved(true)
      toast.success(`Saved · ${data.match_score ?? 'no'} match score`)
      setJob((j) => ({ ...j, match_score: data.match_score }))
    } catch (err) {
      toast.error('Could not save')
    } finally {
      setSaving(false)
    }
  }

  const onUnsave = async () => {
    setSaving(true)
    try {
      await unsaveJob(id)
      setSaved(false)
      toast.success('Removed from saved')
    } catch (err) {
      toast.error('Could not remove')
    } finally {
      setSaving(false)
    }
  }

  if (loading || !job) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-12">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-3/4 bg-ink-800 rounded" />
          <div className="h-4 w-1/2 bg-ink-800 rounded" />
          <div className="h-40 bg-ink-800 rounded" />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-sm text-ink-400 hover:text-ink-100 mb-8 transition-colors"
      >
        <span>←</span> All jobs
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="flex items-start justify-between gap-4 mb-2">
          <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-ink-100 leading-tight">
            {job.title}
          </h1>
          <span className="text-[11px] font-mono uppercase tracking-wider px-2.5 py-1 rounded bg-ink-800 text-ink-300 shrink-0">
            {job.seniority_level}
          </span>
        </div>

        <p className="text-ink-300 mb-8">
          {job.company}
          <span className="text-ink-500 mx-2">·</span>
          <span className="text-ink-400">{job.location}</span>
          <span className="text-ink-500 mx-2">·</span>
          <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">
            {job.source}
          </span>
        </p>

        {job.match_score != null && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-8 p-4 rounded-lg border border-ink-800 bg-ink-900/50"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono uppercase tracking-wider text-ink-400">
                Resume match
              </span>
              <span className="text-2xl font-mono text-amber-glow">{job.match_score}</span>
            </div>
            <div className="h-1 bg-ink-800 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${job.match_score}%` }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="h-full bg-amber-glow"
              />
            </div>
          </motion.div>
        )}

        {job.description_summary && (
          <section className="mb-10 p-6 rounded-lg border border-ink-800 bg-ink-900/30">
            <p className="text-xs font-mono uppercase tracking-wider text-amber-glow mb-3">
              AI summary
            </p>
            <p className="text-ink-200 leading-relaxed">{job.description_summary}</p>
          </section>
        )}

        {job.extracted_skills?.length > 0 && (
          <section className="mb-10">
            <p className="text-xs font-mono uppercase tracking-wider text-ink-400 mb-4">
              Extracted skills
            </p>
            <div className="flex flex-wrap gap-2">
              {job.extracted_skills.map((skill) => (
                <span
                  key={skill}
                  className="text-sm font-mono text-ink-200 px-3 py-1.5 rounded border border-ink-800 bg-ink-900/40"
                >
                  {skill}
                </span>
              ))}
            </div>
          </section>
        )}

        <section className="mb-10">
          <p className="text-xs font-mono uppercase tracking-wider text-ink-400 mb-4">
            Full description
          </p>
          <Description text={job.description_raw} />
        </section>

        <div className="flex gap-3 sticky bottom-4 p-4 rounded-lg border border-ink-800 bg-ink-900/80 backdrop-blur-xl">
          <a
            href={job.url}
            target="_blank"
            rel="noreferrer"
            className="flex-1 h-11 flex items-center justify-center rounded-md bg-ink-100 text-ink-950 font-medium hover:bg-amber-glow transition-colors"
          >
            Apply on source
          </a>
          {saved ? (
            <button
              onClick={onUnsave}
              disabled={saving}
              className="px-5 h-11 rounded-md border border-ink-700 text-ink-200 hover:border-amber-glow hover:text-amber-glow transition-colors disabled:opacity-50"
            >
              Saved
            </button>
          ) : (
            <button
              onClick={onSave}
              disabled={saving}
              className="px-5 h-11 rounded-md border border-ink-700 text-ink-200 hover:border-amber-glow hover:text-amber-glow transition-colors disabled:opacity-50"
            >
              {saving ? 'Saving…' : 'Save job'}
            </button>
          )}
        </div>
      </motion.div>
    </div>
  )
}

/**
 * Render plain-text job description as proper paragraphs + list items.
 * The scraper uses html_to_text() so input is already plain text with
 * newlines and "- " bullets for list items.
 */
function Description({ text }) {
  if (!text) {
    return <p className="text-ink-500 text-sm">No description available.</p>
  }

  // Split into blocks by blank lines
  const blocks = text
    .split(/\n{2,}/)
    .map((b) => b.trim())
    .filter(Boolean)

  return (
    <div className="space-y-4 text-sm text-ink-300 leading-relaxed">
      {blocks.map((block, i) => {
        // Detect a list: every non-empty line starts with "- " or "• "
        const lines = block.split("\n").map((l) => l.trim()).filter(Boolean)
        const isList =
          lines.length > 1 &&
          lines.every((l) => /^[-•*]\s+/.test(l))

        if (isList) {
          return (
            <ul key={i} className="space-y-2 pl-1">
              {lines.map((line, j) => (
                <li
                  key={j}
                  className="flex gap-3"
                >
                  <span className="text-amber-glow mt-1.5 shrink-0">•</span>
                  <span>{line.replace(/^[-•*]\s+/, "")}</span>
                </li>
              ))}
            </ul>
          )
        }

        // Plain paragraph - preserve internal line breaks as soft breaks
        return (
          <p key={i} className="whitespace-pre-line">
            {block}
          </p>
        )
      })}
    </div>
  )
}