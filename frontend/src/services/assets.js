// Backend origin (no trailing slash, no /api). Set VITE_API_URL on Render; falls back to local dev backend.
const raw = (import.meta.env.VITE_API_URL || 'http://localhost:8000').trim().replace(/\/+$/, '')
export const API_ORIGIN = raw.replace(/\/api$/, '')
export const PLACEHOLDER_PATH = '/static/seed/placeholder.svg'

// Turns backend-relative paths (/uploads/..., /static/seed/...) into absolute URLs on the backend domain.
// Absolute http(s), data: and blob: URLs are returned unchanged.
export const assetUrl = (path) => {
  if (!path) return `${API_ORIGIN}${PLACEHOLDER_PATH}`
  if (/^(https?:)?\/\/|^data:|^blob:/i.test(path)) return path
  return `${API_ORIGIN}${path.startsWith('/') ? '' : '/'}${path}`
}