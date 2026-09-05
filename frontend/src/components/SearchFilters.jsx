import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

export default function SearchFilters({ q, location, seniority, onQ, onLocation, onSeniority }) {
  const [localQ, setLocalQ] = useState(q)
  useEffect(() => setLocalQ(q), [q])

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="grid grid-cols-1 md:grid-cols-[1fr_220px_180px] gap-3 mb-8"
    >
      <div className="relative">
        <input
          type="text"
          placeholder="Search title or company"
          value={localQ}
          onChange={(e) => setLocalQ(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onQ(localQ)}
          className="w-full h-11 px-4 bg-ink-900 border border-ink-800 rounded-md text-ink-100 placeholder-ink-500 focus:border-amber-glow focus:outline-none transition-colors"
        />
      </div>
      <input
        type="text"
        placeholder="Location"
        value={location}
        onChange={(e) => onLocation(e.target.value)}
        className="h-11 px-4 bg-ink-900 border border-ink-800 rounded-md text-ink-100 placeholder-ink-500 focus:border-amber-glow focus:outline-none transition-colors"
      />
      <select
        value={seniority}
        onChange={(e) => onSeniority(e.target.value)}
        className="h-11 px-3 bg-ink-900 border border-ink-800 rounded-md text-ink-100 focus:border-amber-glow focus:outline-none transition-colors"
      >
        <option value="">All levels</option>
        <option value="entry">Entry</option>
        <option value="mid">Mid</option>
        <option value="senior">Senior</option>
      </select>
    </motion.div>
  )
}