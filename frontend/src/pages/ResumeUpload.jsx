import { useEffect, useRef, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { uploadResume, myResumes } from '../api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function ResumeUpload() {
  const { isAuthenticated } = useAuth()
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [resumes, setResumes] = useState([])
  const inputRef = useRef(null)
  const navigate = useNavigate()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: { pathname: '/resume' } }} replace />
  }

  useEffect(() => {
    myResumes().then((r) => setResumes(r.data.results)).catch(() => {})
  }, [])

  const onSubmit = async (e) => {
    e?.preventDefault()
    if (!file) return
    setUploading(true)
    try {
      const { data } = await uploadResume(file)
      toast.success('Resume parsed')
      setResumes((r) => [data, ...r])
      setFile(null)
    } catch (err) {
      const detail = err.response?.data?.detail || 'Upload failed'
      toast.error(detail)
    } finally {
      setUploading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files?.[0]
    if (dropped && dropped.name.toLowerCase().endsWith('.pdf')) {
      setFile(dropped)
    } else {
      toast.error('PDF only')
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-3xl font-semibold tracking-tight text-ink-100 mb-2">
          Resume
        </h1>
        <p className="text-ink-400 mb-10">
          Drop a PDF. We'll extract your skills and use them to score every job.
        </p>

        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
          className={`relative cursor-pointer p-12 rounded-xl border-2 border-dashed transition-colors text-center ${
            dragging
              ? 'border-amber-glow bg-amber-glow/5'
              : 'border-ink-800 bg-ink-900/30 hover:border-ink-700'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) setFile(f)
            }}
          />
          <div className="text-4xl mb-3 text-ink-500">↑</div>
          {file ? (
            <div>
              <p className="text-ink-100 font-medium">{file.name}</p>
              <p className="text-sm text-ink-400 mt-1">
                {(file.size / 1024).toFixed(0)} KB · click to change
              </p>
            </div>
          ) : (
            <div>
              <p className="text-ink-200">Drop a PDF here or click to choose</p>
              <p className="text-sm text-ink-500 mt-1">Max 10 MB</p>
            </div>
          )}
        </div>

        <button
          onClick={onSubmit}
          disabled={!file || uploading}
          className="mt-4 w-full h-11 rounded-md bg-ink-100 text-ink-950 font-medium hover:bg-amber-glow transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {uploading ? 'Parsing…' : 'Upload and parse'}
        </button>

        {resumes.length > 0 && (
          <section className="mt-12">
            <h2 className="text-xs font-mono uppercase tracking-wider text-ink-400 mb-4">
              Past resumes
            </h2>
            <div className="space-y-4">
              {resumes.map((r) => (
                <div
                  key={r.id}
                  className="p-5 rounded-lg border border-ink-800 bg-ink-900/40"
                >
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm text-ink-300 font-mono">
                      {new Date(r.uploaded_at).toLocaleString()}
                    </p>
                    <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-ink-800 text-ink-300">
                      {r.seniority_level} · {r.experience_years} yrs
                    </span>
                  </div>
                  {r.summary && (
                    <p className="text-sm text-ink-200 mb-3">{r.summary}</p>
                  )}
                  <div className="flex flex-wrap gap-1.5">
                    {r.parsed_skills?.slice(0, 20).map((s) => (
                      <span
                        key={s}
                        className="text-[11px] font-mono text-ink-300 px-2 py-0.5 rounded border border-ink-800"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </motion.div>
    </div>
  )
}