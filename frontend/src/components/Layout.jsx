import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Menu, X, Plus } from 'lucide-react'
import { useAuth } from '../services/auth'
import { Logo } from './ui'
export default function Layout() {
  const { user, logout } = useAuth(); const nav = useNavigate(); const [open, setOpen] = useState(false)
  const links = [['/', 'Home'], ['/explore', 'Explore'], ...(user ? [['/matches', 'Matches'], ['/swaps', 'My Swaps'], ['/listings', 'My Listings'], ['/messages', 'Messages'], ['/profile', 'Profile']] : [])]
  const cls = ({ isActive }) => `rounded-lg px-3 py-2 text-sm font-semibold transition ${isActive ? 'bg-brand/10 text-brand' : 'text-ink/70 hover:text-brand'}`
  const out = () => { logout(); nav('/') }
  const actions = user ? <><Link to="/listings/new" className="btn-accent"><Plus size={16} />List item</Link><button className="btn-ghost" onClick={out}>Log out</button></>
    : <><Link to="/login" className="btn-ghost">Log in</Link><Link to="/register" className="btn-primary">Join ZWYP</Link></>
  return <div className="min-h-screen">
    <header className="sticky top-0 z-30 border-b border-ink/5 bg-white/85 backdrop-blur"><div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
      <Logo /><nav className="hidden items-center gap-1 lg:flex">{links.map(([to, l]) => <NavLink key={to} to={to} end={to === '/'} className={cls}>{l}</NavLink>)}</nav>
      <div className="hidden items-center gap-2 lg:flex">{actions}</div>
      <button className="lg:hidden" onClick={() => setOpen(!open)} aria-label="Menu">{open ? <X /> : <Menu />}</button></div>
      {open && <div className="space-y-1 border-t border-ink/5 bg-white p-3 lg:hidden" onClick={() => setOpen(false)}>{links.map(([to, l]) => <NavLink key={to} to={to} end={to === '/'} className={cls}>{l}</NavLink>)}<div className="flex gap-2 pt-2">{actions}</div></div>}</header>
    <main className="mx-auto max-w-6xl px-4 py-8"><Outlet /></main>
    <footer className="mt-16 bg-deep py-10 text-sm text-white/70"><div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4"><Logo light />
      <div className="flex gap-5"><Link to="/explore">Explore</Link><Link to="/register">Join</Link></div><span>© 2026 ZWYP</span></div></footer></div>
}