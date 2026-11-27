import { Link } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../services/auth'
import { Spinner, ErrorBox, useLoad } from '../components/ui'
export default function Profile() {
  const { user } = useAuth(); const { data, loading, error } = useLoad(() => api.get('/users/me/dashboard').then(r => r.data))
  const stats = data && [['Active listings', data.active_listings, '/listings'], ['Incoming requests', data.incoming_pending, '/swaps'], ['Outgoing requests', data.outgoing_pending, '/swaps'], ['Completed swaps', data.completed, '/swaps']]
  return <div className="space-y-6"><div className="card flex items-center gap-4 p-6"><div className="grid h-16 w-16 place-items-center rounded-full bg-brand text-2xl font-bold text-white">{user.name[0]}</div><div><h1 className="text-2xl font-extrabold">{user.name}</h1><p className="text-sm text-ink/60">{user.email} · {user.location || 'No location set'}</p><p className="text-sm">{user.bio}</p></div></div>
    <ErrorBox msg={error} />{loading ? <Spinner /> : <div className="grid grid-cols-2 gap-4 md:grid-cols-4">{stats.map(([l, v, to]) => <Link key={l} to={to} className="card p-5 transition hover:-translate-y-1"><div className="text-3xl font-extrabold text-brand">{v}</div><div className="text-sm text-ink/60">{l}</div></Link>)}</div>}</div>
}
