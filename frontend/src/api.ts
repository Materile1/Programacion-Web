export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'
export type Level = { id: number; number: number; title: string; skill: string; status: string; challenges: Challenge[] }
export type Challenge = { id: number; title: string; prompt: string; language: string; difficulty: string; starter_code: string; completed?: boolean; test_cases?: { input: unknown; output: unknown }[] }
export type News = { title: string; summary: string; url: string; source: string; kind: string }
export type TestCaseResult = { input: unknown; expected: unknown; actual: unknown; passed: boolean }
export type ReviewSnippet = { id: number; title: string; language: string; code: string; difficulty: string }
export type ReviewFeedback = { detected: string[]; missed: string[]; score: number; feedback: string }
export type InterviewQuestion = { id: number; kind: 'conceptual' | 'coding'; prompt: string; time_limit_seconds: number }
export type InterviewSession = { id: number; questions: InterviewQuestion[] }
export type InterviewAnswer = { question_id: number; score: number; feedback: string }
export type InterviewSummary = { session_id: number; total_questions: number; answered_questions: number; score: number; answers: InterviewAnswer[] }
export type Progress = { level: number; streak: number; completed_challenges: number; total_submissions: number; skill_breakdown: Record<string, number>; recent_submissions: { title: string; created_at: string; passed: boolean; score: number }[] }
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('devcoach_token')
  const response = await fetch(`${API_URL}${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers ?? {}) } })
  if (response.status === 401) {
    localStorage.removeItem('devcoach_token')
    window.dispatchEvent(new Event('devcoach:unauthorized'))
  }
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? 'No se pudo conectar con DevCoach')
  return response.json()
}
export const submitCode = (challengeId: number, code: string, language = 'python') => api<{ passed: boolean; score: number; quality: number; feedback: string; next_review_at: string }>('/progress', { method: 'POST', body: JSON.stringify({ challenge_id: challengeId, code, language }) })
export const executeCode = (challengeId: number, code: string, language: string) => api<{ passed: boolean; stdout: string; stderr: string; feedback: string; results: TestCaseResult[] }>('/execute', { method: 'POST', body: JSON.stringify({ challenge_id: challengeId, code, language }) })
