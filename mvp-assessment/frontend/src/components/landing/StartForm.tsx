import { buttonPrimary, displayTitle, eyebrow, inputClass, insetPanel, lede, panel } from '../../lib/ui'

type StartFormProps = {
  fullName: string
  isSubmitting: boolean
  onChange: (value: string) => void
  onSubmit: () => void
}

export function StartForm({
  fullName,
  isSubmitting,
  onChange,
  onSubmit,
}: StartFormProps) {
  return (
    <section className={`${panel} grid gap-6 lg:grid-cols-[minmax(0,1.5fr)_minmax(320px,0.9fr)]`}>
      <div className="flex flex-col justify-between gap-6">
        <div className="space-y-4">
          <p className={eyebrow}>Candidate Launch</p>
          <h1 className={displayTitle}>Run a developer assessment without hand-wiring the workflow.</h1>
          <p className={lede}>
            Launch a polished session workspace, collect theory and coding responses, audit helper usage,
            and finish with a structured scorecard that hiring teams can actually inspect.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          {[
            ['10 questions', 'Balanced across coding, architecture, culture, and AI usage.'],
            ['Live code runs', 'Execute candidate Python against local deterministic test cases.'],
            ['Full audit trail', 'Inspect submissions, evaluator JSON, and final synthesis output.'],
          ].map(([title, copy]) => (
            <article
              key={title}
              className="rounded-3xl border border-white/70 bg-white/65 p-4 shadow-[0_16px_40px_-24px_rgba(15,23,42,0.3)]"
            >
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-amber-700">{title}</p>
              <p className="mt-2 text-sm leading-6 text-slate-600">{copy}</p>
            </article>
          ))}
        </div>
      </div>
      <div className={`${insetPanel} flex flex-col justify-between gap-5 border border-slate-200/80 bg-white/90`}>
        <div className="space-y-2">
          <p className={eyebrow}>Start New Session</p>
          <h2 className="font-display text-2xl tracking-tight text-slate-950">Candidate Details</h2>
          <p className="text-sm leading-6 text-slate-600">
            Use a real candidate or reviewer name. A fresh question plan is generated automatically.
          </p>
        </div>
        <div className="space-y-4">
          <label className="grid gap-2">
            <span className="text-sm font-semibold text-slate-700">Candidate full name</span>
            <input
              className={inputClass}
              value={fullName}
              onChange={(event) => onChange(event.target.value)}
              placeholder="Jane Doe"
            />
          </label>
          <button className={`${buttonPrimary} w-full`} onClick={onSubmit} disabled={isSubmitting}>
            {isSubmitting ? 'Starting session...' : 'Start test'}
          </button>
        </div>
      </div>
    </section>
  )
}
