import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

const seniorityStyles = {
  entry: 'bg-ink-800 text-ink-300',
  mid: 'bg-amber-glow/15 text-amber-glow',
  senior: 'bg-amber-glow text-ink-950',
  unknown: 'bg-ink-800 text-ink-400',
}

export default function JobCard({ job, index = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: Math.min(index * 0.04, 0.4), ease: [0.16, 1, 0.3, 1] }}
    >
      <Link
        to={`/jobs/${job.id}`}
        className="group block p-6 rounded-xl border border-ink-800 bg-ink-900/50 hover:bg-ink-900 hover:border-ink-700 transition-all"
      >
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-medium text-ink-100 group-hover:text-amber-glow transition-colors leading-snug">
              {job.title}
            </h3>
            <p className="text-sm text-ink-300 mt-1">
              {job.company}
              {job.location && (
                <>
                  <span className="text-ink-500 mx-2">·</span>
                  <span className="text-ink-400">{job.location}</span>
                </>
              )}
            </p>
          </div>
          <span
            className={`text-[11px] font-mono uppercase tracking-wider px-2 py-1 rounded shrink-0 ${
              seniorityStyles[job.seniority_level] || seniorityStyles.unknown
            }`}
          >
            {job.seniority_level}
          </span>
        </div>

        {job.description_summary && (
          <p className="text-sm text-ink-400 leading-relaxed line-clamp-2 mb-4">
            {job.description_summary}
          </p>
        )}

        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-1.5">
            {(job.extracted_skills || []).slice(0, 4).map((skill) => (
              <span
                key={skill}
                className="text-[11px] font-mono text-ink-300 px-2 py-0.5 rounded border border-ink-800"
              >
                {skill}
              </span>
            ))}
            {(job.extracted_skills || []).length > 4 && (
              <span className="text-[11px] font-mono text-ink-500 px-2 py-0.5">
                +{job.extracted_skills.length - 4}
              </span>
            )}
          </div>
          <span className="text-[10px] font-mono uppercase tracking-wider text-ink-500">
            {job.source}
          </span>
        </div>

        {job.match_score != null && (
          <div className="mt-4 pt-4 border-t border-ink-800 flex items-center gap-2">
            <span className="text-[10px] font-mono uppercase tracking-wider text-ink-500">
              Match
            </span>
            <div className="flex-1 h-1 bg-ink-800 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${job.match_score}%` }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="h-full bg-amber-glow"
              />
            </div>
            <span className="text-sm font-mono text-amber-glow">{job.match_score}</span>
          </div>
        )}
      </Link>
    </motion.div>
  )
}