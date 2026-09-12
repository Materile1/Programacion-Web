function RealOverview({ active, completed, news, progress, onPractice }: { active: Level; completed: number; news: News[]; progress: Progress | null; onPractice: () => void }) {
  const today = new Intl.DateTimeFormat('es-ES', { dateStyle: 'full' }).format(new Date())
  const scores = Object.values(progress?.skill_breakdown ?? {})
  const mastery = scores.length ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 0
  return <div className="space-y-8"><section className="hero-panel reveal"><div className="relative z-10 max-w-3xl"><div className="eyebrow text-mint">{today.toUpperCase()}</div><h1 className="mt-4 font-display text-4xl font-bold leading-tight tracking-tight sm:text-6xl">Tu siguiente nivel<br /><span className="text-mint">se construye hoy.</span></h1><p className="mt-5 max-w-xl text-base leading-7 text-slate-300">Una sesión enfocada en <strong className="text-white">{active.skill.toLowerCase()}</strong>.</p><button onClick={onPractice} className="primary-button mt-8"><Play size={16} fill="currentColor" /> Continuar entrenamiento <ArrowRight size={16} /></button></div><div className="hero-orbit"><div className="orbit-ring" /><div className="orbit-center"><span>{mastery}</span><small>% dominio</small></div></div></section><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3"><Stat label="Racha activa" value={`${progress?.streak ?? 0} días`} detail="Días consecutivos con envíos exitosos" icon={<Flame />} tone="amber" /><Stat label="Ejercicios" value={String(progress?.total_submissions ?? 0)} detail={`${progress?.completed_challenges ?? 0} retos completados`} icon={<Check />} tone="mint" /><Stat label="Dominio general" value={`${mastery}%`} detail="Promedio de skills con actividad" icon={<Activity />} tone="coral" /></div><div className="grid gap-6 xl:grid-cols-2"><section className="panel"><div className="eyebrow text-aqua">RUTA PROFESIONAL</div><h2 className="section-title mt-2">{active.title}</h2><p className="mt-2 text-slate-400">Nivel {active.number} en progreso.</p></section><section className="panel"><div className="eyebrow text-aqua">ACTUALIZACIONES</div><div className="mt-5 space-y-4">{news.slice(0, 3).map(item => <article key={item.url}><p className="text-sm text-slate-200">{item.title}</p><p className="mt-1 text-xs text-slate-500">{item.source}</p></article>)}</div></section></div></div>
}
import { useEffect, useState } from 'react'
import { Activity, ArrowRight, BookOpen, Check, ChevronRight, Code2, Compass, Flame, Gauge, Menu, MessageCircle, Play, Settings2, Sparkles, Timer, Trophy, X } from 'lucide-react'
import { api, executeCode, submitCode, type Challenge, type Level, type News, type Progress, type TestCaseResult } from './api'
import { GoogleSignIn, useAuth } from './AuthContext'
import { PracticePanel } from './PracticePanel'
import { ReviewPanel } from './ReviewPanel'
import { InterviewPanel } from './InterviewPanel'
import { ProfilePanel } from './ProfilePanel'
import type { View } from './types'

function App() {
  const { user, token, loading, signOut } = useAuth()
  const [view, setView] = useState<View>('overview')
  const [levels, setLevels] = useState<Level[]>([])
  const [news, setNews] = useState<News[]>([])
  const [progress, setProgress] = useState<Progress | null>(null)
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [code, setCode] = useState('')
  const [result, setResult] = useState('')
  const [stdout, setStdout] = useState('')
  const [stderr, setStderr] = useState('')
  const [caseResults, setCaseResults] = useState<TestCaseResult[]>([])
  const [running, setRunning] = useState(false)
  const [notice, setNotice] = useState('Conectando con DevCoach...')
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    if (!token) return
    Promise.all([api<Level[]>('/dashboard/path'), api<News[]>('/dashboard/news'), api<Progress>('/users/me/progress')]).then(([path, updates, currentProgress]) => { setLevels(path); setChallenge(path.find(level => level.status === 'active')?.challenges[0] ?? path[0]?.challenges[0] ?? null); setNews(updates); setProgress(currentProgress); setNotice('Sincronizado con tu workspace') }).catch(() => setNotice('No se pudo sincronizar con la API'))
  }, [token])
  useEffect(() => { if (challenge) { setCode(challenge.starter_code); setStdout(''); setStderr(''); setCaseResults([]) } }, [challenge])
  const active = levels.find(level => level.status === 'active') ?? levels[0]
  const completed = levels.filter(level => level.status === 'completed').length

  const navigate = (next: View) => { setView(next); setMobileOpen(false); setResult('') }
  const run = async () => {
    if (!challenge) return
    setRunning(true); setResult(''); setStdout(''); setStderr(''); setCaseResults([])
    try { const response = await executeCode(challenge.id, code, challenge.language); setStdout(response.stdout); setStderr(response.stderr); setResult(response.feedback); setCaseResults(response.results); if (response.passed) { await submitCode(challenge.id, code, challenge.language); const [updatedPath, updatedProgress] = await Promise.all([api<Level[]>('/dashboard/path'), api<Progress>('/users/me/progress')]); setLevels(updatedPath); setProgress(updatedProgress); setChallenge(updatedPath.flatMap(level => level.challenges).find(item => item.id === challenge.id) ?? challenge); setNotice('Progreso guardado en tu workspace') } }
    catch (error) { setStderr(error instanceof Error ? error.message : 'No se pudo ejecutar el código') }
    finally { setRunning(false) }
  }
  if (loading) return <div className="grid min-h-screen place-items-center bg-ink text-slate-300">Cargando sesión...</div>
  if (!user || !token) return <AuthScreen />
  if (!challenge || !active) return <div className="grid min-h-screen place-items-center bg-ink text-slate-300">Cargando ruta de aprendizaje...</div>
  return <div className="min-h-screen bg-ink text-slate-100"><div className="ambient" />
    <aside className={`${mobileOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-30 w-72 border-r border-line bg-[#09151e]/95 p-6 transition-transform lg:translate-x-0`}>
      <div className="flex items-center justify-between"><div className="flex items-center gap-3"><div className="brand-mark"><Code2 size={20} /></div><div><div className="font-display text-lg font-bold tracking-tight">DevCoach</div><div className="eyebrow">TRAINING OS</div></div></div><button className="icon-button lg:hidden" onClick={() => setMobileOpen(false)} aria-label="Cerrar menú"><X size={18} /></button></div>
      <div className="mt-10 rounded-2xl border border-line bg-panel p-4"><div className="flex items-center gap-3"><div className="avatar">{user.name.slice(0, 2).toUpperCase()}</div><div><div className="font-semibold">{user.name}</div><div className="text-xs text-slate-400">Nivel {user.level + 1} · Builder</div></div><button className="ml-auto text-slate-500" onClick={signOut} aria-label="Cerrar sesión"><Settings2 size={16} /></button></div><div className="mt-5 flex items-center justify-between text-xs"><span className="text-slate-400">Racha actual</span><span className="font-semibold text-amber"><Flame size={14} className="mr-1 inline" />{user.streak} {user.streak === 1 ? 'día' : 'días'}</span></div></div>
      <nav className="mt-8 space-y-2">{([['overview','Resumen',Gauge],['path','Ruta de aprendizaje',Compass],['practice','Práctica guiada',Code2],['review','Code review',MessageCircle],['interview','Entrevista técnica',Trophy],['profile','Perfil',Activity]] as const).map(([id,label,Icon]) => <button key={id} onClick={() => navigate(id)} className={`nav-item ${view === id ? 'nav-active' : ''}`}><Icon size={18} /><span>{label}</span>{id === 'practice' && <span className="ml-auto h-2 w-2 rounded-full bg-mint" />}</button>)}</nav>
      <div className="absolute bottom-6 left-6 right-6 rounded-2xl border border-[#315144] bg-[#10241e] p-4"><div className="flex items-center gap-2 text-mint"><Sparkles size={16} /><span className="text-xs font-bold uppercase tracking-widest">Coach tip</span></div><p className="mt-2 text-sm leading-5 text-slate-300">La consistencia gana a la intensidad. Vuelve mañana.</p></div>
    </aside>
    <main className="lg:pl-72"><header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-line bg-ink/80 px-5 backdrop-blur-xl lg:px-10"><button className="icon-button lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Abrir menú"><Menu size={20} /></button><div className="hidden text-sm text-slate-400 md:block">Workspace / <span className="text-slate-200">{view === 'overview' ? 'Resumen' : view}</span></div><div className="ml-auto flex items-center gap-4"><div className="hidden items-center gap-2 text-xs text-slate-500 sm:flex"><span className="pulse-dot" /> {notice}</div><button className="icon-button" aria-label="Actividad"><Activity size={18} /></button><div className="avatar small">{user.name.slice(0, 2).toUpperCase()}</div></div></header>
      <div className="mx-auto max-w-[1500px] px-5 py-8 lg:px-10 lg:py-10">{view === 'overview' && <RealOverview active={active} completed={completed} news={news} progress={progress} onPractice={() => navigate('practice')} />}{view === 'path' && <Path levels={levels} onSelect={(item) => { setChallenge(item.challenges[0]); navigate('practice') }} />}{view === 'review' && <ReviewPanel />}{view === 'interview' && <InterviewPanel />}{view === 'profile' && <ProfilePanel />}{view === 'practice' && <PracticePanel view={view} challenge={challenge} levels={levels} code={code} setCode={setCode} run={run} running={running} stdout={stdout} stderr={stderr} result={result} caseResults={caseResults} onSelectChallenge={setChallenge} />}</div>
    </main>
  </div>
}

function OldOverview({ active, completed, news, onPractice }: { active: Level; completed: number; news: News[]; onPractice: () => void }) { return <div className="space-y-8"><section className="hero-panel reveal"><div className="relative z-10 max-w-3xl"><div className="eyebrow text-mint">SÁBADO, 12 OCTUBRE · SESIÓN 08</div><h1 className="mt-4 font-display text-4xl font-bold leading-tight tracking-tight sm:text-6xl">Tu siguiente nivel<br /><span className="text-mint">se construye hoy.</span></h1><p className="mt-5 max-w-xl text-base leading-7 text-slate-300">Una sesión enfocada en <strong className="text-white">estructuras de datos</strong>. Entrena el razonamiento, no solo la sintaxis.</p><button onClick={onPractice} className="primary-button mt-8"><Play size={16} fill="currentColor" /> Continuar entrenamiento <ArrowRight size={16} /></button></div><div className="hero-orbit"><div className="orbit-ring" /><div className="orbit-center"><span>68</span><small>% dominio</small></div></div></section><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Stat label="Racha activa" value="12 días" detail="+2 desde la semana pasada" icon={<Flame />} tone="amber" /><Stat label="Tiempo enfocado" value="18.5 h" detail="Esta semana" icon={<Timer />} tone="aqua" /><Stat label="Ejercicios" value="127" detail="94% aceptados" icon={<Check />} tone="mint" /><Stat label="Dominio general" value="73%" detail="Top 15%" icon={<Activity />} tone="coral" /></div><div className="grid gap-6 xl:grid-cols-[1.45fr_1fr]"><section className="panel"><div className="flex items-start justify-between"><div><div className="eyebrow text-aqua">RUTA PROFESIONAL</div><h2 className="section-title">Software Engineer</h2></div><button onClick={() => location.hash = 'path'} className="text-button">Ver ruta <ChevronRight size={15} /></button></div><div className="mt-8 flex gap-3 overflow-x-auto pb-2">{[...Array(8)].map((_, i) => <div key={i} className={`path-node ${i < completed ? 'done' : i === completed ? 'current' : ''}`}><div className="node-dot">{i < completed ? <Check size={15} /> : i === completed ? <Sparkles size={15} /> : i + 1}</div><span>{i === completed ? active.title : ['Fundamentos','Python','Algoritmos','Estructuras','POO','Git','SQL','APIs'][i]}</span></div>)}</div><div className="mt-7 flex items-center gap-4"><div className="progress-track"><div className="progress-fill" style={{ width: `${completed / 15 * 100}%` }} /></div><span className="text-xs text-slate-400">{completed} / 15 niveles</span></div></section><section className="panel"><div className="flex items-center justify-between"><div><div className="eyebrow text-amber">SEÑAL DEL ECOSISTEMA</div><h2 className="section-title">Reto del día</h2></div><Sparkles className="text-amber" size={20} /></div>{news.map(item => <a key={item.title} href={item.url} target="_blank" className="news-item"><div className="news-icon"><BookOpen size={17} /></div><div><div className="font-semibold leading-5">{item.title}</div><div className="mt-1 text-xs leading-5 text-slate-400">{item.summary}</div><div className="mt-2 text-[10px] uppercase tracking-widest text-amber">{item.source}</div></div><ArrowRight size={16} className="ml-auto shrink-0 text-slate-500" /></a>)}</section></div></div> }

function Stat({ label, value, detail, icon, tone }: { label: string; value: string; detail: string; icon: React.ReactNode; tone: string }) { return <div className="stat-card"><div className={`stat-icon ${tone}`}>{icon}</div><div className="eyebrow mt-5">{label}</div><div className="mt-1 font-display text-3xl font-bold">{value}</div><div className="mt-2 text-xs text-slate-500">{detail}</div></div> }
function Path({ levels, onSelect }: { levels: Level[]; onSelect: (level: Level) => void }) { return <div className="space-y-7"><div><div className="eyebrow text-aqua">SKILL TREE ENGINE</div><h1 className="page-title">Tu ruta de aprendizaje</h1><p className="mt-3 text-slate-400">Quince niveles. Una progresión que convierte práctica deliberada en criterio.</p></div><div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{levels.map(level => <button key={level.id} onClick={() => level.status !== 'locked' && onSelect(level)} className={`level-card text-left ${level.status}`}><div className="flex items-center justify-between"><span className="level-number">{String(level.number).padStart(2, '0')}</span><span className={`status-pill ${level.status}`}>{level.status === 'completed' ? 'Completado' : level.status === 'active' ? 'En progreso' : 'Bloqueado'}</span></div><h3 className="mt-6 font-display text-xl font-semibold">{level.title}</h3><p className="mt-2 text-sm text-slate-400">{level.skill}</p><div className="mt-6 flex items-center justify-between border-t border-line pt-4 text-xs text-slate-500"><span>{level.challenges.length} reto{level.challenges.length === 1 ? '' : 's'}</span><ChevronRight size={15} /></div></button>)}</div></div> }
function AuthScreen() {
  const { signInWithPassword, registerWithPassword } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError('')
    if (mode === 'register' && (name.trim().length < 2 || name.trim().length > 120)) { setError('El nombre debe tener entre 2 y 120 caracteres.'); return }
    if (password.length < 8 || password.length > 128) { setError('La contraseña debe tener entre 8 y 128 caracteres.'); return }
    setSubmitting(true)
    try { mode === 'login' ? await signInWithPassword(email, password) : await registerWithPassword(name.trim(), email, password) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'No se pudo iniciar sesión') }
    finally { setSubmitting(false) }
  }

  return <div className="grid min-h-screen place-items-center bg-ink px-5 text-slate-100"><div className="panel w-full max-w-md"><div className="eyebrow text-mint">DEVCOACH</div><h1 className="page-title mt-3">Entrena con criterio.</h1><p className="mt-3 text-slate-400">Guarda tu progreso y ejecuta tus retos.</p><div className="mt-7 grid grid-cols-2 border-b border-line"><button className={`pb-3 text-sm ${mode === 'login' ? 'border-b-2 border-mint text-mint' : 'text-slate-500'}`} onClick={() => { setMode('login'); setError('') }}>Iniciar sesión</button><button className={`pb-3 text-sm ${mode === 'register' ? 'border-b-2 border-mint text-mint' : 'text-slate-500'}`} onClick={() => { setMode('register'); setError('') }}>Crear cuenta</button></div><form className="mt-6 space-y-4" onSubmit={submit}>{mode === 'register' && <label className="block text-sm text-slate-300">Nombre<input className="input mt-2 w-full" value={name} onChange={event => setName(event.target.value)} minLength={2} maxLength={120} required /></label>}<label className="block text-sm text-slate-300">Email<input className="input mt-2 w-full" type="email" value={email} onChange={event => setEmail(event.target.value)} required /></label><label className="block text-sm text-slate-300">Contraseña<input className="input mt-2 w-full" type="password" value={password} onChange={event => setPassword(event.target.value)} minLength={8} maxLength={128} required /></label>{error && <p className="text-sm text-coral" role="alert">{error}</p>}<button className="primary-button w-full justify-center" disabled={submitting}>{submitting ? 'Conectando...' : mode === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}</button></form><div className="my-6 flex items-center gap-3 text-xs text-slate-600"><span className="h-px flex-1 bg-line" />o continúa con<span className="h-px flex-1 bg-line" /></div><div className="flex justify-center"><GoogleSignIn /></div></div></div>
}
export default App
