import axios from 'axios'
import { API_ORIGIN } from './assets'
const api = axios.create({ baseURL: `${API_ORIGIN}/api`, timeout: 15000 })
api.interceptors.request.use(c => { const t = localStorage.getItem('zwyp_token'); if (t) c.headers.Authorization = `Bearer ${t}`; return c })
// An expired/invalid token on a protected call logs the user out instead of leaving a broken page.
api.interceptors.response.use(r => r, e => {
  if (e.response?.status === 401 && localStorage.getItem('zwyp_token') && !String(e.config?.url).startsWith('/auth/')) {
    localStorage.removeItem('zwyp_token'); window.dispatchEvent(new Event('zwyp:logout')) }
  return Promise.reject(e) })
export const errMsg = e => {
  if (!e.response) return e.code === 'ECONNABORTED' ? 'The request timed out. Please try again.' : 'Cannot reach the ZWYP server. Make sure the backend is running on port 8000.'
  const d = e.response.data?.detail
  if (Array.isArray(d)) return d.map(x => `${(x.loc || []).slice(-1)[0]}: ${x.msg}`).join('; ')
  return typeof d === 'string' ? d : `Request failed (${e.response.status})`
}
export default api