import type { QuestionPayload } from '../../types/api'
import { badgeMuted, badgePrimary, cardTitle, eyebrow, panel } from '../../lib/ui'

type QuestionPanelProps = {
  question: QuestionPayload
}

export function QuestionPanel({ question }: QuestionPanelProps) {
  return (
    <section className={`${panel} grid gap-5`}>
      <div className="flex flex-wrap items-center gap-2">
        <span className={badgePrimary}>{question.type}</span>
        <span className={badgeMuted}>difficulty: {question.difficulty}</span>
        <span className={badgeMuted}>
          {question.sequence_no} / {question.total_questions}
        </span>
      </div>
      <div className="space-y-3">
        <h2 className={cardTitle}>{question.title}</h2>
        <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700 sm:text-base">{question.prompt}</p>
      </div>
      <div className="grid gap-4 border-t border-slate-200 pt-5">
        <div className="space-y-1">
          <p className={eyebrow}>Rubric focus</p>
          <h3 className="font-display text-xl tracking-tight text-slate-950">What the evaluator will look for</h3>
        </div>
        <ul className="grid gap-3">
          {Object.entries(question.rubric).map(([key, value]) => (
            <li
              key={key}
              className="rounded-[22px] border border-slate-200/80 bg-slate-50/85 px-4 py-3 text-sm leading-6 text-slate-700"
            >
              <strong className="mr-1 font-semibold text-slate-950">{key}</strong>
              <span>{value}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
