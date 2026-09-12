import { useEffect, useState } from 'react'
import { Clock, Trophy } from 'lucide-react'
import { api, type InterviewQuestion, type InterviewSession, type InterviewSummary } from './api'
import { CodeEditor } from './CodeEditor'

export function InterviewPanel() {
  const [session, setSession] = useState<InterviewSession | null>(null)
  const [index, setIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [seconds, setSeconds] = useState(0)
  const [summary, setSummary] = useState<InterviewSummary | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const question: InterviewQuestion | undefined = session?.questions[index]

  useEffect(() => { api<InterviewSession>('/interview/session').then(setSession).catch(cause => setError(cause instanceof Error ? cause.message : 'No se pudo iniciar la entrevista')) }, [])
  useEffect(() => { if (question) { setSeconds(question.time_limit_seconds); setAnswer('') } }, [question])
  useEffect(() => { if (!question || summary || submitting) return; const timer = window.setInterval(() => setSeconds(value => Math.max(value - 1, 0)), 1000); return () => window.clearInterval(timer) }, [question, summary, submitting])
  useEffect(() => { if (seconds === 0 && question && answer && !submitting && !summary) void submitAnswer() }, [seconds])

  const submitAnswer = async () => {
    if (!session || !question || !answer.trim() || submitting) return
    setSubmitting(true); setError('')
    try { await api(`/interview/session/${session.id}/answer`, { method: 'POST', body: JSON.stringify({ question_id: question.id, answer }) }); if (index + 1 >= session.questions.length) setSummary(await api<InterviewSummary>(`/interview/session/${session.id}/summary`)); else setIndex(value => value + 1) } catch (cause) { setError(cause instanceof Error ? cause.message : 'No se pudo enviar la respuesta') } finally { setSubmitting(false) }
  }

  if (summary) return <div className="panel mx-auto max-w-3xl text-center"><Trophy className="mx-auto text-amber" size={32} /><div className="eyebrow mt-4 text-amber">ENTREVISTA COMPLETADA</div><h1 className="page-title mt-2">Tu resumen</h1><p className="mt-4 text-4xl font-bold text-mint">{summary.score}%</p><p className="mt-2 text-slate-400">Respondiste {summary.answered_questions} de {summary.total_questions} preguntas.</p><div className="mt-8 space-y-3 text-left">{summary.answers.map((item, itemIndex) => <div key={item.question_id} className="rounded-xl border border-line bg-[#0a141c] p-4"><div className="flex justify-between text-sm"><span>Pregunta {itemIndex + 1}</span><span className="text-mint">{item.score}%</span></div><p className="mt-2 text-xs text-slate-400">{item.feedback}</p></div>)}</div></div>
  if (!question) return <div className="panel text-slate-400">{error || 'Preparando entrevista...'}</div>
  return <div className="space-y-7"><div><div className="eyebrow text-amber">MODO ENTREVISTA</div><h1 className="page-title">Piensa en voz alta.</h1><p className="mt-3 text-slate-400">Pregunta {index + 1} de {session?.questions.length ?? 0}. La respuesta se evalúa al enviarla.</p></div><section className="panel"><div className="flex items-center justify-between"><span className="status-pill active">{question.kind === 'coding' ? 'EJERCICIO DE CÓDIGO' : 'PREGUNTA CONCEPTUAL'}</span><span className={`flex items-center gap-2 text-sm ${seconds < 20 ? 'text-coral' : 'text-amber'}`}><Clock size={16} /> {Math.floor(seconds / 60)}:{String(seconds % 60).padStart(2, '0')}</span></div><h2 className="mt-7 font-display text-2xl font-semibold">{question.prompt}</h2>{question.kind === 'coding' ? <div className="mt-6"><CodeEditor code={answer} language="python" onChange={setAnswer} onRun={submitAnswer} running={submitting} stdout="" stderr="" /></div> : <textarea className="input mt-6 min-h-48 w-full resize-y" value={answer} onChange={event => setAnswer(event.target.value)} placeholder="Escribe una respuesta breve y precisa..." />}<button className="primary-button mt-5" onClick={submitAnswer} disabled={!answer.trim() || submitting}>{submitting ? 'Evaluando...' : index + 1 === session?.questions.length ? 'Finalizar entrevista' : 'Siguiente pregunta'}</button>{error && <p className="mt-4 text-sm text-coral">{error}</p>}</section></div>
}