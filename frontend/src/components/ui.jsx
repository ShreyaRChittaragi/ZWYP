import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { errMsg } from '../services/api'
import { assetUrl, PLACEHOLDER_PATH } from '../services/assets'
import { Loader2, MapPin, Repeat2, AlertCircle, Inbox } from 'lucide-react'
export const Logo = ({ light }) => <Link to="/" className="flex items-center gap-2 text-xl font-extrabold tracking-tight">
  <span className="grid h-8 w-8 place-items-center rounded-lg bg-accent text-deep"><Repeat2 size={18} /></span><span className={light ? 'text-white' : 'text-brand'}>ZWYP</span></Link>
export const Spinner = () => <div className="grid place-items-center py-20 text-brand"><Loader2 className="animate-spin" /></div>
export const ErrorBox = ({ msg, onRetry }) => msg ? <div role="alert" className="flex items-center gap-2 rounded-xl bg-red-50 p-3 text-sm text-red-700"><AlertCircle size={16} className="shrink-0" /><span className="flex-1">{msg}</span>{onRetry && <button type="button" onClick={onRetry} className="font-semibold underline">Retry</button>}</div> : null
export const imgFallback = e => { e.currentTarget.onerror = null; e.currentTarget.src = assetUrl(PLACEHOLDER_PATH) }
export const Empty = ({ text, children }) => <div className="card grid place-items-center gap-3 p-12 text-center text-ink/60"><Inbox />{text}{children}</div>
export const StatusPill = ({ s }) => { const c = { pending:'bg-accent/40 text-deep', accepted:'bg-green-100 text-green-800', rejected:'bg-red-100 text-red-700', cancelled:'bg-gray-100 text-gray-600', completed:'bg-brand text-white' }[s]
  return <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${c}`}>{s}</span> }
export const ItemCard = ({ item }) => <Link to={`/items/${item.id}`} className="card group overflow-hidden transition hover:-translate-y-1 hover:shadow-xl">
  <div className="aspect-[4/3] overflow-hidden bg-canvas"><img src={assetUrl(item.image_url)} alt={item.title} loading="lazy" onError={imgFallback} className="h-full w-full object-cover transition duration-500 group-hover:scale-105" /></div>
  <div className="space-y-1.5 p-4"><div className="text-xs font-semibold text-brand">{item.category}</div><h3 className="font-bold leading-snug">{item.title}</h3>
    <div className="flex items-center gap-1 text-xs text-ink/60"><MapPin size={12} />{item.location} · {item.condition}</div>
    <p className="line-clamp-1 border-t border-ink/5 pt-2 text-xs text-ink/70">Wants: <span className="font-semibold text-deep">{item.wants}</span></p></div></Link>
export const Mini = ({ item }) => <div className="flex items-center gap-3"><img src={assetUrl(item.image_url)} alt="" onError={imgFallback} className="h-12 w-12 rounded-lg object-cover" /><div className="min-w-0"><div className="truncate text-sm font-bold">{item.title}</div><div className="text-xs text-ink/60">{item.owner.name}</div></div></div>
export function useLoad(fn, deps = []) {
  const [s, set] = useState({ data: null, loading: true, error: '' }); const run = useRef(0)
  const load = (silent = false) => { const id = ++run.current; if (!silent) set(x => ({ ...x, loading: true, error: '' }))
    return fn().then(d => { if (id === run.current) set({ data: d, loading: false, error: '' }) })
      .catch(e => { if (id === run.current) set(x => ({ data: silent ? x.data : null, loading: false, error: errMsg(e) })) }) }
  useEffect(() => { load(); return () => { run.current++ } }, deps) // ignores stale responses
  return { ...s, reload: () => load(true), retry: () => load() }
}