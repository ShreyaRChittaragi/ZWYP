import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, Trash2, ImagePlus } from 'lucide-react'
import api, { errMsg } from '../services/api'
import { useAuth } from '../services/auth'
import { ItemCard, Spinner, ErrorBox, Empty, useLoad } from '../components/ui'
export function Listings() {
  const { data, loading, error, reload, retry } = useLoad(() => api.get('/items/mine').then(r => r.data)); const [delErr, setDelErr] = useState('')
  const del = async id => { if (!confirm('Remove this listing?')) return; setDelErr(''); try { await api.delete(`/items/${id}`) } catch (e) { setDelErr(errMsg(e)) } finally { reload() } }
  return <div className="space-y-6"><div className="flex items-center justify-between"><h1 className="text-3xl font-extrabold">My Listings</h1><Link to="/listings/new" className="btn-accent"><Plus size={16} />New listing</Link></div>
    <ErrorBox msg={delErr || error} onRetry={error ? retry : undefined} />{loading ? <Spinner /> : !data?.length ? <Empty text="You haven't listed anything yet." /> : <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">{data.map(i => <div key={i.id} className="space-y-2"><ItemCard item={i} />
      <div className="flex items-center justify-between text-xs"><span className="font-semibold capitalize text-brand">{i.status}</span>{i.status === 'available' && <button className="flex items-center gap-1 text-red-600" onClick={() => del(i.id)}><Trash2 size={12} />Remove</button>}</div></div>)}</div>}</div>
}
export function NewListing() {
  const nav = useNavigate(); const { user } = useAuth(); const facets = useLoad(() => api.get('/items/facets').then(r => r.data))
  const [f, setF] = useState({ title: '', description: '', category: 'Electronics', condition: 'Good', location: user?.location || '', wants: '', value_inr: '' }); const [img, setImg] = useState(null); const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  const set = k => e => setF({ ...f, [k]: e.target.value }); const L = (t, c) => <label className="block space-y-1"><span className="text-xs font-semibold">{t}</span>{c}</label>
  const pick = e => { const file = e.target.files[0]; if (!file) return setImg(null)
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) { setImg(null); e.target.value = ''; return setErr('Please choose a JPEG, PNG or WebP image.') }
    if (file.size > 5 * 1024 * 1024) { setImg(null); e.target.value = ''; return setErr('Image must be 5 MB or smaller.') }
    setErr(''); setImg(file) }
  const submit = async e => { e.preventDefault(); setErr('')
    if (f.title.length < 3 || f.description.length < 10) return setErr('Title needs 3+ characters and description 10+.')
    const fd = new FormData(); Object.entries(f).forEach(([k, v]) => fd.append(k, v || (k === 'value_inr' ? 0 : ''))); if (img) fd.append('image', img)
    setBusy(true); try { await api.post('/items', fd); nav('/listings') } catch (x) { setErr(errMsg(x)) } finally { setBusy(false) } }
  const cats = facets.data?.categories || ['Electronics'], conds = facets.data?.conditions || ['Good']
  return <form onSubmit={submit} className="card mx-auto max-w-2xl space-y-4 p-6"><h1 className="text-2xl font-extrabold">List an item</h1>
    {L('Title', <input className="input" value={f.title} onChange={set('title')} required />)}{L('Description', <textarea className="input" rows={3} value={f.description} onChange={set('description')} required />)}
    <div className="grid gap-3 sm:grid-cols-2">{L('Category', <select className="input" value={f.category} onChange={set('category')}>{cats.map(c => <option key={c}>{c}</option>)}</select>)}
      {L('Condition', <select className="input" value={f.condition} onChange={set('condition')}>{conds.map(c => <option key={c}>{c}</option>)}</select>)}
      {L('Location', <input className="input" placeholder="e.g. Pune" value={f.location} onChange={set('location')} required />)}{L('Approx. value (₹, optional)', <input className="input" type="number" min="0" value={f.value_inr} onChange={set('value_inr')} />)}</div>
    {L('What do you want in exchange?', <input className="input" placeholder="e.g. Acoustic guitar or keyboard" value={f.wants} onChange={set('wants')} required />)}
    <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-dashed border-brand/40 p-4 text-sm"><ImagePlus className="text-brand" />{img ? img.name : 'Upload a photo (JPEG, PNG or WebP, up to 5 MB). If skipped, a placeholder is used.'}<input type="file" accept="image/*" hidden onChange={pick} /></label>
    <ErrorBox msg={err} /><button className="btn-primary w-full" disabled={busy}>{busy ? 'Publishing...' : 'Publish listing'}</button></form>
}