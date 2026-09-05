import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jobpulse_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('jobpulse_token')
      localStorage.removeItem('jobpulse_user')
    }
    return Promise.reject(err)
  }
)

// Auth
export const register = (data) => api.post('/auth/register', data)
export const login = (data) => api.post('/auth/login', data)
export const me = () => api.get('/auth/me')

// Jobs
export const listJobs = (params) => api.get('/jobs', { params })
export const getJob = (id) => api.get(`/jobs/${id}`)
export const saveJob = (id) => api.post(`/jobs/${id}/save`)
export const unsaveJob = (id) => api.delete(`/jobs/${id}/unsave`)
export const savedJobs = () => api.get('/saved-jobs')

// Resume
export const uploadResume = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/resume/upload', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const myResumes = () => api.get('/resume/me')

// Analytics
export const trends = () => api.get('/analytics/trends')

export default api