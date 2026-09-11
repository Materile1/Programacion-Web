import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google'
import { api } from './api'

export type User = { id: number; email: string; name: string; avatar?: string | null; level: number; streak: number }
type AuthContextValue = { user: User | null; token: string | null; loading: boolean; signInWithGoogle: (response: CredentialResponse) => Promise<void>; signInWithPassword: (email: string, password: string) => Promise<void>; registerWithPassword: (name: string, email: string, password: string) => Promise<void>; signOut: () => void }
const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => localStorage.getItem('devcoach_token'))
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(Boolean(token))

  useEffect(() => {
    if (!token) return
    api<User>('/auth/me').then(setUser).catch(() => { localStorage.removeItem('devcoach_token'); setToken(null) }).finally(() => setLoading(false))
  }, [token])

  const signInWithGoogle = async (response: CredentialResponse) => {
    if (!response.credential) throw new Error('Google no devolvió una credencial')
    const session = await api<{ access_token: string }>('/auth/google/callback', { method: 'POST', body: JSON.stringify({ id_token: response.credential }) })
    localStorage.setItem('devcoach_token', session.access_token)
    setLoading(true)
    setToken(session.access_token)
  }
  const setSession = (accessToken: string) => { localStorage.setItem('devcoach_token', accessToken); setLoading(true); setToken(accessToken) }
  const signInWithPassword = async (email: string, password: string) => {
    const session = await api<{ access_token: string }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
    setSession(session.access_token)
  }
  const registerWithPassword = async (name: string, email: string, password: string) => {
    const session = await api<{ access_token: string }>('/auth/register', { method: 'POST', body: JSON.stringify({ name, email, password }) })
    setSession(session.access_token)
  }
  const signOut = () => { localStorage.removeItem('devcoach_token'); setToken(null); setUser(null) }
  return <AuthContext.Provider value={{ user, token, loading, signInWithGoogle, signInWithPassword, registerWithPassword, signOut }}>{children}</AuthContext.Provider>
}

export function GoogleSignIn() {
  const { signInWithGoogle } = useAuth()
  return <GoogleLogin onSuccess={signInWithGoogle} onError={() => undefined} theme="filled_black" shape="rectangular" text="signin_with" />
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return value
}
