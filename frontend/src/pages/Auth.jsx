import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../services/auth'
import { errMsg } from '../services/api'
import { ErrorBox, Logo } from '../components/ui'
function Form({ mode }) {
  const reg = mode === 'register'; const { login, register } = useAuth(); const nav = useNavigate(); const loc = useLocation()
  const [f, setF] = useState({ name: '', email: reg ? '' : 'aarav@zwyp.demo', password: reg ? '' : 'zwyp1234', location: '' }); const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  const set = k => e => setF({ ...f, [k]: e.target.value })
  const submit = async e => { e.preventDefault(); setErr(''); setBusy(true)
    try { reg ? await register(f) : await login(f.email, f.password); nav(loc.state?.from || '/explore') } catch (x) { setErr(errMsg(x)) } finally { setBusy(false) } }
  return <div className="mx-auto max-w-md"><div className="card space-y-5 p-8"><Logo /><div><h1 className="text-2xl font-extrabold">{reg ? 'Join ZWYP' : 'Welcome back'}</h1><p className="text-sm text-ink/60">{reg ? 'Start swapping in under a minute.' : 'Demo account is prefilled (password: zwyp1234).'}</p></div>
    <form onSubmit={submit} className="space-y-3">{reg && <><input className="input" placeholder="Full name" value={f.name} onChange={set('name')} required minLength={2} /><input className="input" placeholder="City (e.g. Bengaluru)" value={f.location} onChange={set('location')} /></>}
      <input className="input" type="email" placeholder="Email" value={f.email} onChange={set('email')} required /><input className="input" type="password" placeholder="Password (min 6)" value={f.password} onChange={set('password')} required minLength={6} />
      <ErrorBox msg={err} /><button className="btn-primary w-full" disabled={busy}>{busy ? 'Please wait...' : reg ? 'Create account' : 'Log in'}</button></form>
    <p className="text-center text-sm">{reg ? <>Already a member? <Link className="font-semibold text-brand" to="/login">Log in</Link></> : <>New here? <Link className="font-semibold text-brand" to="/register">Create an account</Link></>}</p></div></div>
}
export const Login = () => <Form mode="login" />
export const Register = () => <Form mode="register" />
