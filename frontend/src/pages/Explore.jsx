import { useEffect, useState } from 'react'
import { Search } from 'lucide-react'
import api from '../services/api'
import { ItemCard, Spinner, ErrorBox, Empty, useLoad } from '../components/ui'
export default function Explore() {
  const [f, setF] = useState({ q: '', category: '', location: '', condition: '' }); const [page, setPage] = useState(1)
  const facets = useLoad(() => api.get('/items/facets').then(r => r.data))
  const { data, loading, error, retry } = useLoad(() => api.get('/items', { params: { ...f, page, size: 12 } }).then(r => r.data), [f, page])
  const [qIn, setQIn] = useState('')
  useEffect(() => { const t = setTimeout(() => { setF(x => x.q === qIn ? x : { ...x, q: qIn }); setPage(1) }, 300); return () => clearTimeout(t) }, [qIn])
  const set = (k, v) => { setF({ ...f, [k]: v }); setPage(1) }
  const sel = (k, label, opts = []) => <select className="input" value={f[k]} onChange={e => set(k, e.target.value)}><option value="">{label}</option>{opts.map(o => <option key={o}>{o}</option>)}</select>
  return <div className="space-y-6"><h1 className="text-3xl font-extrabold">Explore</h1>
    <div className="card grid gap-3 p-4 md:grid-cols-4"><div className="relative md:col-span-1"><Search size={16} className="absolute left-3 top-3 text-ink/40" /><input className="input pl-9" placeholder="Search items" value={qIn} onChange={e => setQIn(e.target.value)} /></div>
      {sel('category', 'All categories', facets.data?.categories)}{sel('location', 'All locations', facets.data?.locations)}{sel('condition', 'Any condition', facets.data?.conditions)}</div>
    <ErrorBox msg={error} onRetry={retry} />{loading ? <Spinner /> : !data?.items.length ? <Empty text="No items match those filters." /> :
      <><div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">{data.items.map(i => <ItemCard key={i.id} item={i} />)}</div>
        <div className="flex items-center justify-center gap-3"><button className="btn-ghost" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button><span className="text-sm">{data.total} items · page {page}</span><button className="btn-ghost" disabled={page * 12 >= data.total} onClick={() => setPage(page + 1)}>Next</button></div></>}</div>
}