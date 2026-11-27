import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './services/auth'
import Layout from './components/Layout'
import { Spinner } from './components/ui'
import Landing from './pages/Landing'
import Explore from './pages/Explore'
import ItemDetail from './pages/ItemDetail'
import { Login, Register } from './pages/Auth'
import { Matches, Swaps } from './pages/Swaps'
import { Listings, NewListing } from './pages/Listings'
import Messages from './pages/Messages'
import Profile from './pages/Profile'
const Guard = ({ children }) => { const { user, ready } = useAuth(); const loc = useLocation()
  if (!ready) return <Spinner />; return user ? children : <Navigate to="/login" state={{ from: loc.pathname }} replace /> }
export default function App() {
  return <Routes><Route element={<Layout />}>
    <Route index element={<Landing />} /><Route path="explore" element={<Explore />} /><Route path="items/:id" element={<ItemDetail />} />
    <Route path="login" element={<Login />} /><Route path="register" element={<Register />} />
    <Route path="matches" element={<Guard><Matches /></Guard>} /><Route path="swaps" element={<Guard><Swaps /></Guard>} />
    <Route path="listings" element={<Guard><Listings /></Guard>} /><Route path="listings/new" element={<Guard><NewListing /></Guard>} />
    <Route path="messages/:sid?" element={<Guard><Messages /></Guard>} /><Route path="profile" element={<Guard><Profile /></Guard>} />
    <Route path="*" element={<Navigate to="/" />} /></Route></Routes>
}
