const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'
export type Level = { id: number; number: number; title: string; skill: string; status: string; challenges: Challenge[] }
export type Challenge = { id: number; title: string; prompt: string; language: string; difficulty: string; starter_code: string; test_cases?: { input: unknown; output: unknown }[] }
export type News = { title: string; summary: string; url: string; source: string; kind: string }
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('devcoach_token')
  const response = await fetch(`${API_URL}${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers ?? {}) } })
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? 'No se pudo conectar con DevCoach')
  return response.json()
}
export const submitCode = (challengeId: number, code: string, language = 'python') => api<{ passed: boolean; score: number; quality: number; feedback: string; next_review_at: string }>('/progress', { method: 'POST', body: JSON.stringify({ challenge_id: challengeId, code, language }) })
export const executeCode = (challengeId: number, code: string, language: string) => api<{ passed: boolean; stdout: string; stderr: string; feedback: string }>('/execute', { method: 'POST', body: JSON.stringify({ challenge_id: challengeId, code, language }) })
