import { formatDimensionLabel } from '../../lib/dimensions'
import { cardTitle, eyebrow, insetPanel, panel } from '../../lib/ui'

type ScoreBreakdownCardProps = {
  dimensions: {
    dimension_name: string
    score: number
    confidence: number
  }[]
  strengths: string[]
  weaknesses: string[]
}

export function ScoreBreakdownCard({
  dimensions,
  strengths,
  weaknesses,
}: ScoreBreakdownCardProps) {
  return (
    <section className={`${panel} grid gap-5`}>
      <div className="space-y-1">
        <p className={eyebrow}>Scoring view</p>
        <h3 className={cardTitle}>Breakdown</h3>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {dimensions.map((dimension) => (
          <article
            key={dimension.dimension_name}
            className="rounded-[24px] border border-slate-200/80 bg-slate-50/85 p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.65)]"
          >
            <p className="text-sm font-medium text-slate-600">{formatDimensionLabel(dimension.dimension_name)}</p>
            <strong className="mt-3 block font-display text-4xl tracking-tight text-slate-950">
              {dimension.score.toFixed(1)}
            </strong>
            <span className="mt-1 block text-sm text-slate-500">
              confidence {dimension.confidence.toFixed(2)}
            </span>
          </article>
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <article className={`${insetPanel} grid gap-4 border border-emerald-200/70 bg-emerald-50/65`}>
          <div className="space-y-1">
            <p className={eyebrow}>Positive signal</p>
            <h4 className="font-display text-xl tracking-tight text-slate-950">Strengths</h4>
          </div>
          <ul className="grid gap-2 text-sm leading-6 text-slate-700">
            {strengths.map((item, index) => (
              <li key={`${item}-${index}`} className="flex gap-3">
                <span className="mt-2 h-1.5 w-1.5 rounded-full bg-emerald-600" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </article>
        <article className={`${insetPanel} grid gap-4 border border-amber-200/70 bg-amber-50/70`}>
          <div className="space-y-1">
            <p className={eyebrow}>Open risk</p>
            <h4 className="font-display text-xl tracking-tight text-slate-950">Weaknesses</h4>
          </div>
          <ul className="grid gap-2 text-sm leading-6 text-slate-700">
            {weaknesses.map((item, index) => (
              <li key={`${item}-${index}`} className="flex gap-3">
                <span className="mt-2 h-1.5 w-1.5 rounded-full bg-amber-600" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  )
}
