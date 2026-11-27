// Backend origin (no trailing slash, no /api). Set VITE_API_URL on Render; falls back to local dev backend.
const raw = (import.meta.env.VITE_API_URL || 'http://localhost:8000').trim().replace(/\/+$/, '')
export const API_ORIGIN = raw.replace(/\/api$/, '')
export const PLACEHOLDER_PATH = '/static/seed/placeholder.svg'

// Turns backend-relative paths (/uploads/..., /static/seed/...) into absolute URLs on the backend domain.
// Absolute http(s), data: and blob: URLs are returned unchanged.
// Demo/placeholder illustrations (/static/seed/<slug>.svg) are shown as real photos from picsum.photos.
// `key` (e.g. the item id) keeps each item's photo stable between page loads. User uploads are untouched.
const photo = (seed) => `https://picsum.photos/seed/${encodeURIComponent(seed)}/800/600`
export const assetUrl = (path, key) => {
  const seedMatch = /^\/static\/seed\/([\w-]+)\.svg$/.exec(path || '')
  if (!path || seedMatch) {
    const slug = seedMatch ? seedMatch[1] : 'placeholder'
    return photo(slug === 'placeholder' ? `zwyp-${key ?? 'item'}` : `${slug}-${key ?? ''}`)
  }
  if (/^(https?:)?\/\/|^data:|^blob:/i.test(path)) return path
  return `${API_ORIGIN}${path.startsWith('/') ? '' : '/'}${path}`
}