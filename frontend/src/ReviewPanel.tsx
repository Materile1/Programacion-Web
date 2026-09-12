import { useEffect, useState } from 'react'
import Editor from '@monaco-editor/react'
import { Check, X } from 'lucide-react'
import { api, type ReviewFeedback, type ReviewSnippet } from './api'

export function ReviewPanel() {
  const [snippets, setSnippets] = useState<ReviewSnippet[]>([])
  const [selected, setSelected] = useState<ReviewSnippet | null>(null)
  const [review, setReview] = useState('')
  const [feedback, setFeedback] = useState<{ detected: string[]; missed: string[]; score: number; feedback: string } | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api<ReviewSnippet[]>('/review/snippets').then(items => { setSnippets(items); setSelected(items[0] ?? null) }).catch(cause => setError(cause instanceof Error ? cause.message : 'No se pudieron cargar los snippets'))
  }, [])

  const selectSnippet = (snippet: ReviewSnippet) => { setSelected(snippet); setReview(''); setFeedback(null) }
  const submit = async () => {
    if (!selected || !review.trim()) return
    try { setFeedback(await api<ReviewFeedback>(`/review/snippets/${selected.id}/submit`, { method: 'POST', body: JSON.stringify({ review }) })) } catch (cause) { setError(cause instanceof Error ? cause.message : 'No se pudo enviar la revisión') }
  }

  return <div className="space-y-7"><div><div className="eyebrow text-mint">MODO REVISIÓN</div><h1 className="page-title">Encuentra el problema.</h1><p className="mt-3 text-slate-400">Lee código existente, explica sus riesgos y propón mejoras concretas.</p></div><div className="grid gap-6 xl:grid-cols-[280px_1fr]"><aside className="panel space-y-2"><div className="eyebrow text-aqua">SNIPPETS</div>{snippets.map(snippet => <button key={snippet.id} onClick={() => selectSnippet(snippet)} className={`nav-item ${selected?.id === snippet.id ? 'nav-active' : ''}`}><span className="text-left"><span className="block text-sm text-slate-200">{snippet.title}</span><span className="text-xs text-slate-500">{snippet.difficulty} · {snippet.language}</span></span></button>)}</aside>{selected && <section className="space-y-6"><div className="editor-wrap"><div className="editor-bar"><span className="text-xs text-slate-500">review.{selected.language === 'python' ? 'py' : 'js'}</span><span className="text-xs text-slate-500">solo lectura</span></div><Editor height="360px" language={selected.language} theme="vs-dark" value={selected.code} options={{ readOnly: true, minimap: { enabled: false }, fontSize: 14, padding: { top: 16 }, automaticLayout: true }} /></div><section className="panel"><label className="block text-sm text-slate-300">Tu revisión<textarea className="input mt-3 min-h-40 w-full resize-y" value={review} onChange={event => setReview(event.target.value)} placeholder="Describe bugs, límites, seguridad y mejoras..." /></label><button className="primary-button mt-4" onClick={submit} disabled={!review.trim()}>Enviar revisión</button>{error && <p className="mt-4 text-sm text-coral">{error}</p>}{feedback && <div className="mt-6 grid gap-3 sm:grid-cols-2"><div className="rounded-xl border border-[#315144] bg-[#10241e] p-4"><div className="flex items-center gap-2 text-mint"><Check size={16} /> Detectados ({feedback.detected.length})</div>{feedback.detected.map(issue => <p key={issue} className="mt-2 text-sm text-slate-300">{issue}</p>)}</div><div className="rounded-xl border border-[#5a3430] bg-[#241719] p-4"><div className="flex items-center gap-2 text-coral"><X size={16} /> Omitidos ({feedback.missed.length})</div>{feedback.missed.map(issue => <p key={issue} className="mt-2 text-sm text-slate-300">{issue}</p>)}</div><p className="sm:col-span-2 text-sm text-slate-400">{feedback.feedback} Puntuación: <strong className="text-white">{feedback.score}%</strong></p></div>}</section></section>}</div></div>
}
