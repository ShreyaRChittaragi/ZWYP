import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { MapPin, Repeat2, ShieldCheck } from 'lucide-react'
import api, { errMsg } from '../services/api'
import { useAuth } from '../services/auth'
import { assetUrl } from '../services/assets'
import { ItemCard, Spinner, ErrorBox, imgFallback, useLoad } from '../components/ui'
export default function ItemDetail() {
  const { id } = useParams(); const { user } = useAuth(); const nav = useNavigate()
  const { data, loading, error, retry } = useLoad(() => api.get(`/items/${id}`).then(r => r.data), [id])
  const mine = useLoad(() => user ? api.get('/items/mine').then(r => r.data.filter(i => i.status === 'available')) : Promise.resolve([]), [user])
  const [offer, setOffer] = useState(''); const [note, setNote] = useState(''); const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  if (loading) return <Spinner />
  if (error) return <div className="space-y-4"><ErrorBox msg={error} onRetry={retry} /><Link to="/explore" className="btn-ghost">Back to Explore</Link></div>
  const { item, similar } = data; const own = user?.id === item.owner_id; const available = item.status === 'available'
  const send = async () => { setErr(''); setBusy(true)
    try { await api.post('/swaps', { target_item_id: item.id, offered_item_id: +offer, note }); nav('/swaps?tab=outgoing') } catch (e) { setErr(errMsg(e)) } finally { setBusy(false) } }
  return <div className="space-y-12"><div className="grid gap-8 md:grid-cols-2">
    <img src={assetUrl(item.image_url)} alt={item.title} onError={imgFallback} className="aspect-[4/3] w-full rounded-3xl object-cover shadow-lg" />
    <div className="space-y-5"><div><span className="rounded-full bg-brand/10 px-3 py-1 text-xs font-bold text-brand">{item.category}</span><h1 className="mt-3 text-3xl font-extrabold">{item.title}</h1>
      <div className="mt-2 flex flex-wrap gap-3 text-sm text-ink/60"><span className="flex items-center gap-1"><ShieldCheck size={14} />{item.condition}</span><span className="flex items-center gap-1"><MapPin size={14} />{item.location}</span>{item.value_inr > 0 && <span>Approx. ₹{item.value_inr.toLocaleString('en-IN')}</span>}</div></div>
      <p className="text-ink/80">{item.description}</p>
      <div className="card flex items-center gap-3 p-4"><div className="grid h-10 w-10 place-items-center rounded-full bg-brand font-bold text-white">{item.owner.name[0]}</div><div><div className="font-bold">{item.owner.name}</div><div className="text-xs text-ink/60">{item.owner.location}</div></div></div>
      <div className="rounded-2xl bg-accent/30 p-4"><div className="flex items-center gap-2 text-xs font-bold uppercase text-deep"><Repeat2 size={14} />Wants in exchange</div><div className="mt-1 font-semibold">{item.wants}</div></div>
      {!available ? <p className="rounded-xl bg-canvas p-3 text-sm font-semibold text-ink/70">This item is no longer available for swapping.</p>
        : own ? <p className="text-sm text-ink/60">This is your listing.</p> : !user ? <Link to="/login" state={{ from: `/items/${item.id}` }} className="btn-primary w-full">Log in to send swap request</Link> :
        <div className="card space-y-3 p-4"><div className="font-bold">Send swap request</div>
          {mine.loading ? <Spinner /> : mine.error ? <ErrorBox msg={mine.error} onRetry={mine.retry} /> : mine.data?.length ? <><select className="input" aria-label="Item to offer" value={offer} onChange={e => setOffer(e.target.value)}><option value="">Choose one of your items to offer</option>{mine.data.map(i => <option key={i.id} value={i.id}>{i.title}</option>)}</select>
            <textarea className="input" rows={2} maxLength={500} placeholder="Add a note (optional)" value={note} onChange={e => setNote(e.target.value)} /><ErrorBox msg={err} />
            <button className="btn-primary w-full" disabled={!offer || busy} onClick={send}>{busy ? 'Sending...' : 'Send Swap Request'}</button></>
            : <p className="text-sm">You need an available listing to offer. <Link to="/listings/new" className="font-semibold text-brand">List an item</Link></p>}</div>}</div></div>
    {similar.length > 0 && <section><h2 className="mb-4 text-xl font-extrabold">Similar listings</h2><div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">{similar.map(i => <ItemCard key={i.id} item={i} />)}</div></section>}</div>
}