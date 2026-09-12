import { useState } from 'react'
import { ArrowLeft, ArrowRight, MessageCircle, Sparkles } from 'lucide-react'
import type { View } from './types'
import { askTutor, type Challenge, type Level, type TestCaseResult } from './api'
import { CodeEditor } from './CodeEditor'

type Props = {
  view: View
  challenge: Challenge
  levels: Level[]
  code: string
  setCode: (value: string) => void
  run: () => void
  running: boolean
  stdout: string
  stderr: string
  result: string
  caseResults: TestCaseResult[]
  onSelectChallenge: (challenge: Challenge) => void
}

export function PracticePanel({ view, challenge, levels, code, setCode, run, running, stdout, stderr, result, caseResults, onSelectChallenge }: Props) {
  const [question, setQuestion] = useState('')
  const [tutor, setTutor] = useState<{ answer: string; mode: string } | null>(null)
  const [asking, setAsking] = useState(false)
  const [tutorError, setTutorError] = useState('')
  const title = view === 'practice' ? 'Práctica guiada' : view === 'review' ? 'Code review' : 'Entrevista técnica'
  const level = levels.find(item => item.challenges.some(itemChallenge => itemChallenge.id === challenge.id))
  const trackChallenges = level?.challenges.filter(item => item.language === challenge.language) ?? []
  const challengeIndex = trackChallenges.findIndex(item => item.id === challenge.id)
  const hasPrevious = challengeIndex > 0
  const nextChallenge = trackChallenges[challengeIndex + 1]
  const nextLevel = level && levels.find(item => item.number === level.number + 1 && item.status !== 'locked')
  const nextLevelChallenge = nextLevel?.challenges.find(item => item.language === challenge.language)
  const hasNext = Boolean(nextChallenge || nextLevelChallenge)
  const nextBlocked = !challenge.completed
  const alternate = level?.challenges.find(item => {
    const baseTitle = challenge.title.replace(' [JavaScript]', '')
    return item.id !== challenge.id && item.language !== challenge.language && item.title.replace(' [JavaScript]', '') === baseTitle
  })

  const context = `Reto: ${challenge.prompt}\n\nLenguaje: ${challenge.language}\n\nCódigo actual:\n${code || '(sin código todavía)'}`
  const requestTutor = async (studentQuestion: string, extraContext = '') => {
    setAsking(true); setTutorError('')
    try { setTutor(await askTutor(studentQuestion, `${context}\n\n${extraContext}`)) } catch (cause) { setTutorError(cause instanceof Error ? cause.message : 'No se pudo contactar al tutor') } finally { setAsking(false) }
  }
  const explainFailure = (item: TestCaseResult) => requestTutor('Explícame por qué falló este caso con preguntas guiadas, sin mostrarme la solución completa.', `Caso fallido:\nEntrada: ${JSON.stringify(item.input)}\nEsperado: ${JSON.stringify(item.expected)}\nObtenido: ${JSON.stringify(item.actual)}`)
  const moveNext = () => {
    if (nextBlocked) return
    if (nextChallenge) return onSelectChallenge(nextChallenge)
    if (nextLevelChallenge) onSelectChallenge(nextLevelChallenge)
  }

  return <div className="space-y-7">
    <div><div className="eyebrow text-mint">{view === 'practice' ? 'MODO ENTRENAMIENTO' : view === 'review' ? 'MODO REVISIÓN' : 'MODO ENTREVISTA'}</div><h1 className="page-title">{title}</h1><p className="mt-3 text-slate-400">Ejecuta tu solución contra los casos de prueba guardados para este reto.</p></div>
    <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
      <section className="panel">
        <div className="flex items-center justify-between"><span className="status-pill active">RETO ACTIVO</span><span className="text-xs text-slate-500">{challenge.difficulty} · {challenge.language}</span></div>
        {level && <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400"><span>Reto {challengeIndex + 1} de {trackChallenges.length} · Nivel {level.number + 1}</span><div className="flex gap-2"><button className={`text-button ${challenge.language === 'python' ? 'text-mint' : ''}`} onClick={() => alternate && challenge.language !== 'python' && onSelectChallenge(alternate)}>Python</button><button className={`text-button ${challenge.language === 'javascript' ? 'text-mint' : ''}`} onClick={() => alternate && challenge.language !== 'javascript' && onSelectChallenge(alternate)}>JavaScript</button></div></div>}
        <h2 className="mt-6 font-display text-2xl font-semibold">{challenge.title}</h2><p className="mt-4 whitespace-pre-line leading-7 text-slate-300">{challenge.prompt}</p>
        <div className="mt-8 rounded-xl border border-line bg-[#0a141c] p-4"><div className="flex items-center gap-2 text-xs text-slate-400"><Sparkles size={14} className="text-amber" /> Tutor socrático</div><textarea className="input mt-3 min-h-20 w-full resize-y" value={question} onChange={event => setQuestion(event.target.value)} placeholder="¿Por dónde empiezo con este reto?" /><button className="primary-button mt-3" onClick={() => requestTutor(question.trim() || 'No sé por dónde empezar con este reto')} disabled={asking}>{asking ? 'Pensando...' : 'Pedir ayuda'}</button>{tutorError && <p className="mt-3 text-sm text-coral">{tutorError}</p>}{tutor && <div className="mt-4 border-l-2 border-mint pl-4 text-sm leading-6 text-slate-300"><div className="eyebrow text-mint">{tutor.mode === 'ai-configured' ? 'TUTOR IA' : 'TUTOR LOCAL'}</div><p className="mt-2 whitespace-pre-line">{tutor.answer}</p></div>}</div>
        <div className="mt-8 rounded-xl border border-line bg-[#0a141c] p-4"><div className="flex items-center gap-2 text-xs text-slate-400"><MessageCircle size={14} className="text-mint" /> Casos persistidos</div><p className="mt-3 text-sm leading-6 text-slate-300">{challenge.test_cases?.length ?? 0} casos se evaluarán en el servidor.</p></div>
        {caseResults.length > 0 && <div className="mt-8 space-y-3"><div className="eyebrow text-aqua">RESULTADOS POR CASO</div>{caseResults.map((item, index) => <div key={`${index}-${String(item.input)}`} className="rounded-xl border border-line bg-[#0a141c] p-3 text-sm"><div className="flex items-center gap-2"><span className={item.passed ? 'text-mint' : 'text-coral'}>{item.passed ? '✓' : '✕'}</span><span className={item.passed ? 'text-mint' : 'text-coral'}>Caso {index + 1}</span></div>{!item.passed && <><div className="mt-2 space-y-1 text-xs text-slate-400"><div>Entrada: <span className="font-mono text-slate-300">{JSON.stringify(item.input)}</span></div><div>Esperado: <span className="font-mono text-slate-300">{JSON.stringify(item.expected)}</span></div><div>Obtenido: <span className="font-mono text-coral">{JSON.stringify(item.actual)}</span></div></div><button className="text-button mt-3" onClick={() => explainFailure(item)} disabled={asking}>Explícame por qué falló</button></>}</div>)}</div>}
        <div className="mt-8 flex items-center justify-between gap-3 border-t border-line pt-5"><button className="text-button disabled:cursor-not-allowed disabled:opacity-40" disabled={!hasPrevious} onClick={() => onSelectChallenge(trackChallenges[challengeIndex - 1])}><ArrowLeft size={15} /> Reto anterior</button><button className="primary-button disabled:cursor-not-allowed disabled:opacity-40" disabled={!hasNext || nextBlocked} title={nextBlocked ? 'Completa este reto para continuar' : undefined} onClick={moveNext}>Siguiente reto <ArrowRight size={15} /></button></div>{nextBlocked && <p className="mt-3 text-right text-xs text-slate-500">Resuelve el reto correctamente para desbloquear el siguiente.</p>}
      </section>
      <section><CodeEditor code={code} language={challenge.language} onChange={setCode} onRun={run} running={running} stdout={stdout || result} stderr={stderr} /></section>
    </div>
  </div>
}