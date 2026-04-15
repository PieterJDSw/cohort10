import Editor from '@monaco-editor/react'
import { cardTitle, panel } from '../../lib/ui'

type CodeEditorPanelProps = {
  value: string
  onChange: (value: string) => void
}

export function CodeEditorPanel({ value, onChange }: CodeEditorPanelProps) {
  return (
    <section className={`${panel} grid gap-4`}>
      <div className="flex items-center justify-between gap-3">
        <h3 className={cardTitle}>Python editor</h3>
        <p className="text-sm text-slate-500">Monaco editor with local test execution.</p>
      </div>
      <div className="overflow-hidden rounded-[26px] border border-slate-200/80 bg-slate-950 shadow-[0_18px_48px_-28px_rgba(15,23,42,0.55)]">
        <Editor
          height="380px"
          defaultLanguage="python"
          theme="vs-dark"
          value={value}
          onChange={(nextValue) => onChange(nextValue ?? '')}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
          }}
        />
      </div>
    </section>
  )
}
