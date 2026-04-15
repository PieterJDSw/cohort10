import {
  badgeMuted,
  buttonSecondary,
  cardTitle,
  cn,
  inputClass,
  mutedText,
  panel,
} from '../../lib/ui'

type Message = {
  role: 'user' | 'assistant'
  text: string
}

type AIAssistantPanelProps = {
  messages: Message[]
  prompt: string
  busy: boolean
  onPromptChange: (value: string) => void
  onSend: () => void
}

export function AIAssistantPanel({
  messages,
  prompt,
  busy,
  onPromptChange,
  onSend,
}: AIAssistantPanelProps) {
  return (
    <section className={`${panel} flex h-full flex-col gap-5`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className={cardTitle}>AI helper</h3>
        <span className={badgeMuted}>logged to backend</span>
      </div>
      <div className="grid min-h-[260px] gap-3 overflow-auto rounded-[24px] border border-slate-200/70 bg-slate-50/75 p-4">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center rounded-[20px] border border-dashed border-slate-200 bg-white/70 px-6 text-center">
            <p className={mutedText}>Ask for a nudge, test strategy, or structure advice.</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <article
              key={`${message.role}-${index}`}
              className={cn(
                'grid gap-2 rounded-[24px] border px-4 py-3 shadow-sm',
                message.role === 'user'
                  ? 'justify-self-end border-slate-200 bg-white text-slate-700'
                  : 'justify-self-start border-amber-200/70 bg-amber-50 text-slate-800',
              )}
            >
              <span className="text-[0.68rem] font-semibold uppercase tracking-[0.24em] text-slate-500">
                {message.role}
              </span>
              <p className="text-sm leading-6 whitespace-pre-wrap">{message.text}</p>
            </article>
          ))
        )}
      </div>
      <div className="grid gap-3">
        <textarea
          className={`${inputClass} min-h-[130px] resize-y`}
          value={prompt}
          onChange={(event) => onPromptChange(event.target.value)}
          placeholder="Ask the assistant for help..."
        />
        <button className={`${buttonSecondary} w-full sm:w-auto`} onClick={onSend} disabled={busy}>
          {busy ? 'Sending...' : 'Send'}
        </button>
      </div>
    </section>
  )
}
