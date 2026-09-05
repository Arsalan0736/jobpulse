import { createContext, useContext, useEffect, useState } from 'react'
import { me as meApi } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('jobpulse_user')
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('jobpulse_token')
    if (!token) {
      setLoading(false)
      return
    }
    meApi()
      .then((res) => {
        setUser(res.data)
        localStorage.setItem('jobpulse_user', JSON.stringify(res.data))
      })
      .catch(() => {
        localStorage.removeItem('jobpulse_token')
        localStorage.removeItem('jobpulse_user')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const loginWithToken = (token, userData) => {
    localStorage.setItem('jobpulse_token', token)
    localStorage.setItem('jobpulse_user', JSON.stringify(userData))
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('jobpulse_token')
    localStorage.removeItem('jobpulse_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, loginWithToken, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)