import { Link } from 'react-router-dom'
import { PackagePlus, Search, Handshake, Leaf, Wallet, Users, ArrowRight } from 'lucide-react'
import api from '../services/api'
import { assetUrl } from '../services/assets'
import { ItemCard, Spinner, ErrorBox, imgFallback, useLoad } from '../components/ui'
const steps = [[PackagePlus, 'List', 'Post what you no longer use and what you would love in return.'], [Search, 'Discover', 'Browse items and get smart match suggestions.'], [Handshake, 'Swap', 'Send a request, chat, agree and exchange.']]
const perks = [[Wallet, 'Zero cash needed', 'Your unused things are your currency.'], [Leaf, 'Less waste', 'Give good items a second life.'], [Users, 'Real community', 'Meet people in your own city.']]
export default function Landing() {
  const { data, loading, error, retry } = useLoad(() => api.get('/items', { params: { size: 4 } }).then(r => r.data.items))
  return <div className="space-y-20">
    <section className="grid items-center gap-10 md:grid-cols-2"><div className="space-y-6">
      <span className="rounded-full bg-accent px-3 py-1 text-xs font-bold text-deep">Peer-to-peer barter marketplace</span>
      <h1 className="text-4xl font-extrabold leading-tight text-deep md:text-5xl">Your stuff. <span className="text-brand">Someone else's treasure.</span></h1>
      <p className="max-w-md text-ink/70">ZWYP lets you trade things you own for things you want. No money, no waste. Just a fair swap with someone nearby.</p>
      <div className="flex flex-wrap gap-3"><Link to="/explore" className="btn-primary">Explore items <ArrowRight size={16} /></Link><Link to="/register" className="btn-accent">Start swapping</Link></div></div>
      <div className="grid grid-cols-2 gap-3">{(data || []).slice(0, 4).map((i, k) => <img key={i.id} src={assetUrl(i.image_url)} alt={i.title} onError={imgFallback} className={`aspect-square w-full rounded-3xl object-cover shadow-lg ${k % 2 ? 'mt-6' : ''}`} />)}</div></section>
    <section><h2 className="mb-6 text-2xl font-extrabold">How ZWYP works</h2><div className="grid gap-4 md:grid-cols-3">{steps.map(([I, t, d], k) => <div key={t} className="card p-6"><div className="mb-4 grid h-11 w-11 place-items-center rounded-xl bg-brand text-white"><I size={20} /></div><div className="text-xs font-bold text-brand">STEP {k + 1}</div><h3 className="text-lg font-bold">{t}</h3><p className="text-sm text-ink/70">{d}</p></div>)}</div></section>
    <section><div className="mb-6 flex items-end justify-between"><h2 className="text-2xl font-extrabold">Featured items</h2><Link to="/explore" className="text-sm font-semibold text-brand">See all</Link></div>
      <ErrorBox msg={error} onRetry={retry} />{loading ? <Spinner /> : <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">{(data || []).map(i => <ItemCard key={i.id} item={i} />)}</div>}</section>
    <section className="rounded-3xl bg-deep p-8 text-white md:p-12"><h2 className="mb-6 text-2xl font-extrabold">Why swap instead of buy?</h2><div className="grid gap-6 md:grid-cols-3">{perks.map(([I, t, d]) => <div key={t}><I className="mb-2 text-accent" /><div className="font-bold">{t}</div><p className="text-sm text-white/70">{d}</p></div>)}</div>
      <Link to="/register" className="btn-accent mt-8">Create free account</Link></section></div>
}