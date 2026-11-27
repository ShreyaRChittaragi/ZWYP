import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { ArrowLeftRight, Sparkles, MessageCircle, RefreshCw } from 'lucide-react'
import api, { errMsg } from '../services/api'
import { useAuth } from '../services/auth'
import { Spinner, ErrorBox, Empty, StatusPill, Mini, useLoad } from '../components/ui'
export function Swaps() {
  const { user } = useAuth(); const [sp, setSp] = useSearchParams(); const tab = sp.get('tab') === 'outgoing' ? 'outgoing' : 'incoming'; const setTab = t => setSp({ tab: t }); const [err, setErr] = useState(''); const [busy, setBusy] = useState(null)
  const { data, loading, error, reload, retry } = useLoad(() => api.get('/swaps').then(r => r.data))
  const act = async (id, a) => { setErr(''); setBusy(id); try { await api.post(`/swaps/${id}/${a}`) } catch (e) { setErr(errMsg(e)) } finally { setBusy(null); reload() } }
  const rows = (data || []).filter(s => tab === 'incoming' ? s.owner.id === user.id : s.requester.id === user.id)
  const btn = (s, a, label, cls = 'btn-ghost') => <button disabled={busy === s.id} className={`${cls} !py-1.5`} onClick={() => act(s.id, a)}>{label}</button>
  return <div className="space-y-6"><h1 className="text-3xl font-extrabold">My Swaps</h1>
    <div className="inline-flex rounded-xl bg-white p-1 ring-1 ring-ink/10">{['incoming', 'outgoing'].map(t => <button key={t} onClick={() => setTab(t)} className={`rounded-lg px-4 py-1.5 text-sm font-semibold capitalize ${tab === t ? 'bg-brand text-white' : ''}`}>{t}</button>)}</div>
    <ErrorBox msg={err || error} onRetry={error ? retry : undefined} />{loading ? <Spinner /> : !rows.length ? <Empty text={`No ${tab} requests yet.`}><Link to="/explore" className="btn-primary">Explore items</Link></Empty> :
      <div className="space-y-3">{rows.map(s => <div key={s.id} className="card flex flex-wrap items-center justify-between gap-4 p-4">
        <div className="flex flex-wrap items-center gap-4"><Mini item={s.offered_item} /><ArrowLeftRight className="text-brand" size={18} /><Mini item={s.target_item} /></div>
        <div className="flex flex-wrap items-center gap-2"><StatusPill s={s.status} />
          {s.status === 'pending' && tab === 'incoming' && <>{btn(s, 'accept', 'Accept', 'btn-primary')}{btn(s, 'reject', 'Reject')}</>}
          {s.status === 'pending' && tab === 'outgoing' && btn(s, 'cancel', 'Cancel')}{s.status === 'accepted' && btn(s, 'complete', 'Mark completed', 'btn-accent')}
          <Link to={`/messages/${s.id}`} className="btn-ghost !py-1.5"><MessageCircle size={14} />Chat</Link></div></div>)}</div>}</div>
}
export function Matches() {
  const { data, loading, error, retry } = useLoad(() => api.get('/matches').then(r => r.data))
  if (loading) return <Spinner />
  return <div className="space-y-8"><div><h1 className="text-3xl font-extrabold">Smart matches</h1><p className="text-sm text-ink/60">Rule-based suggestions from what you offer and want. Matching uses keywords, category and city.</p></div><ErrorBox msg={error} onRetry={retry} />
    {data?.cycles.length > 0 && <section className="space-y-3"><h2 className="flex items-center gap-2 text-lg font-extrabold"><RefreshCw size={18} className="text-brand" />Three-way swap opportunities</h2>
      {data.cycles.map((c, k) => <div key={k} className="card flex flex-wrap items-center gap-3 p-4">{c.map((i, n) => <div key={i.id} className="flex items-center gap-3"><Link to={`/items/${i.id}`}><Mini item={i} /></Link>
        <span className="text-xs text-ink/50">→ {c[(n + 1) % 3].owner.name}</span></div>)}<p className="w-full text-xs text-ink/60">Each person gives their item to the next and receives the item they want from the previous. Suggestion only: coordinate via messages.</p></div>)}</section>}
    <section className="space-y-3"><h2 className="flex items-center gap-2 text-lg font-extrabold"><Sparkles size={18} className="text-brand" />Two-way matches</h2>
      {!data?.matches.length ? <Empty text="No matches yet. List an item and say what you want to see suggestions." /> : data.matches.map((m, k) => <div key={k} className="card space-y-3 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3"><div className="flex flex-wrap items-center gap-4"><Mini item={m.my_item} /><ArrowLeftRight size={18} className="text-brand" /><Mini item={m.their_item} /></div>
          <div className="flex items-center gap-2"><span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${m.kind === 'mutual' ? 'bg-accent text-deep' : 'bg-brand/10 text-brand'}`}>{m.kind === 'mutual' ? 'Mutual match' : 'Partial match'}</span><Link to={`/items/${m.their_item.id}`} className="btn-primary !py-1.5">View & request</Link></div></div>
        <ul className="list-inside list-disc text-sm text-ink/70">{m.reasons.map(r => <li key={r}>{r}</li>)}</ul></div>)}</section></div>
}