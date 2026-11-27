import { createContext, useContext, useEffect, useState } from 'react'
import api from './api'
const Ctx = createContext(null)
export const useAuth = () => useContext(Ctx)
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); const [ready, setReady] = useState(false)
  useEffect(() => {
    const out = () => setUser(null); window.addEventListener('zwyp:logout', out)
    if (localStorage.getItem('zwyp_token')) api.get('/users/me').then(r => setUser(r.data)).catch(() => {}).finally(() => setReady(true)); else setReady(true)
    return () => window.removeEventListener('zwyp:logout', out) }, [])
  const finish = r => { localStorage.setItem('zwyp_token', r.data.token); setUser(r.data.user) }
  const login = (email, password) => api.post('/auth/login', { email, password }).then(finish)
  const register = d => api.post('/auth/register', d).then(finish)
  const logout = () => { localStorage.removeItem('zwyp_token'); setUser(null) }
  return <Ctx.Provider value={{ user, ready, login, register, logout }}>{children}</Ctx.Provider>
}