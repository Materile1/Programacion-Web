import Editor from '@monaco-editor/react'

type Props = { code: string; language: string; onChange: (value: string) => void; onRun: () => void; running: boolean; stdout: string; stderr: string }

export function CodeEditor({ code, language, onChange, onRun, running, stdout, stderr }: Props) {
  return <div className="editor-wrap">
    <div className="editor-bar"><span className="text-xs text-slate-500">solution.{language === 'python' ? 'py' : language === 'sql' ? 'sql' : 'js'}</span><span className="text-xs text-slate-500">{language}</span></div>
    <Editor height="390px" language={language} theme="vs-dark" value={code} onChange={(value) => onChange(value ?? '')} options={{ minimap: { enabled: false }, fontSize: 14, padding: { top: 16 }, automaticLayout: true, tabSize: 4 }} />
    <div className="flex items-center justify-between border-t border-line bg-[#0a141c] px-4 py-3"><span className="text-xs text-slate-500">stdout / stderr</span><button className="primary-button" onClick={onRun} disabled={running}><span>{running ? 'Ejecutando...' : 'Ejecutar'}</span></button></div>
    {(stdout || stderr) && <pre className={`m-0 max-h-40 overflow-auto whitespace-pre-wrap border-t border-line bg-[#071018] p-4 text-xs ${stderr ? 'text-coral' : 'text-mint'}`}>{stderr || stdout}</pre>}
  </div>
}
