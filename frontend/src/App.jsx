import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import JobDetail from './pages/JobDetail'
import ResumeUpload from './pages/ResumeUpload'
import SavedJobs from './pages/SavedJobs'
import Analytics from './pages/Analytics'

export default function App() {
  return (
    <div className="min-h-[100dvh] bg-ink-950 text-ink-100">
      <div className="grain" />
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/jobs/:id" element={<JobDetail />} />
          <Route path="/resume" element={<ResumeUpload />} />
          <Route path="/saved" element={<SavedJobs />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </main>
    </div>
  )
}