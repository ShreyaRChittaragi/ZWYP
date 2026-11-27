import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Send } from 'lucide-react'
import api, { errMsg } from '../services/api'
import { useAuth } from '../services/auth'
import { Spinner, ErrorBox, Empty, StatusPill, useLoad } from '../components/ui'
export default function Messages() {
  const { sid } = useParams(); const { user } = useAuth(); const [text, setText] = useState(''); const [err, setErr] = useState(''); const [sending, setSending] = useState(false); const end = useRef(null)
  const list = useLoad(() => api.get('/messages').then(r => r.data))
  const thread = useLoad(() => sid ? api.get(`/messages/${sid}`).then(r => r.data) : Promise.resolve([]), [sid])
  useEffect(() => { if (!sid) return; const t = setInterval(thread.reload, 5000); return () => clearInterval(t) }, [sid])
  useEffect(() => { end.current?.scrollIntoView({ block: 'end' }) }, [thread.data])
  const send = async e => { e.preventDefault(); const body = text.trim(); if (!body || sending) return; setErr(''); setSending(true)
    try { await api.post(`/messages/${sid}`, { body }); setText(''); thread.reload(); list.reload() } catch (x) { setErr(errMsg(x)) } finally { setSending(false) } }
  return <div className="space-y-4"><h1 className="text-3xl font-extrabold">Messages</h1><ErrorBox msg={list.error} onRetry={list.retry} /><div className="grid gap-4 md:grid-cols-3">
    <div className={`space-y-2 ${sid ? 'hidden md:block' : ''}`}>{list.loading ? <Spinner /> : !list.data?.length ? <Empty text="No conversations yet. Send a swap request to start one." /> : list.data.map(c => <Link key={c.swap_id} to={`/messages/${c.swap_id}`} className={`card block p-3 ${+sid === c.swap_id ? 'ring-2 ring-brand' : ''}`}>
      <div className="flex justify-between"><b className="text-sm">{c.with}</b><StatusPill s={c.status} /></div><div className="truncate text-xs text-ink/60">{c.title}</div><div className="truncate text-xs">{c.last}</div></Link>)}</div>
    <div className={`card flex h-[28rem] flex-col md:col-span-2 ${sid ? '' : 'hidden md:flex'}`}>{!sid ? <div className="grid flex-1 place-items-center text-sm text-ink/50">Select a conversation</div> : <>
      <Link to="/messages" className="flex items-center gap-1 border-b border-ink/5 p-3 text-sm font-semibold text-brand md:hidden"><ArrowLeft size={14} />All conversations</Link>
      <div className="flex-1 space-y-2 overflow-y-auto p-4">{thread.loading ? <Spinner /> : thread.error ? <ErrorBox msg={thread.error} onRetry={thread.retry} /> : !thread.data?.length ? <p className="text-center text-sm text-ink/50">No messages yet. Say hello!</p> : thread.data.map(m => <div key={m.id} className={`flex ${m.sender_id === user.id ? 'justify-end' : ''}`}><div className={`max-w-[75%] break-words rounded-2xl px-3.5 py-2 text-sm ${m.sender_id === user.id ? 'bg-brand text-white' : 'bg-canvas'}`}>{m.body}</div></div>)}<div ref={end} /></div>
      <ErrorBox msg={err} /><form onSubmit={send} className="flex gap-2 border-t border-ink/5 p-3"><input className="input" maxLength={1000} placeholder="Write a message" value={text} onChange={e => setText(e.target.value)} disabled={!!thread.error} /><button className="btn-primary" aria-label="Send" disabled={sending || !text.trim() || !!thread.error}><Send size={16} /></button></form></>}</div></div></div>
}