import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useParams } from 'react-router-dom'
import { getResults } from '../api/sessionsApi'
import { RadarChartCard } from '../components/results/RadarChartCard'
import { ScoreBreakdownCard } from '../components/results/ScoreBreakdownCard'
import {
  badgeBase,
  buttonSecondary,
  displayTitle,
  eyebrow,
  insetPanel,
  lede,
  pageStack,
  panel,
  recommendationTone,
  statusClasses,
} from '../lib/ui'
import type { ResultPayload } from '../types/api'

export function ResultPage() {
  const { sessionId = '' } = useParams()
  const [result, setResult] = useState<ResultPayload | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        setResult(await getResults(sessionId))
      } catch {
        setError('Unable to load the result payload.')
      }
    }

    void load()
  }, [sessionId])

  if (error) {
    return <p className={statusClasses.error}>{error}</p>
  }

  if (!result) {
    return <p className={statusClasses.neutral}>Loading result...</p>
  }

  return (
    <div className={pageStack}>
      <section className={`${panel} grid gap-6 lg:grid-cols-[minmax(0,1.45fr)_minmax(280px,0.8fr)]`}>
        <div className="space-y-5">
          <p className={eyebrow}>Final recommendation</p>
          <div className="space-y-4">
            <span
              className={`${badgeBase} border ${recommendationTone(result.recommendation)}`}
            >
              {result.recommendation.replace('_', ' ')}
            </span>
            <h1 className={displayTitle}>{result.recommendation.replace('_', ' ')}</h1>
            <p className={lede}>{result.summary}</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Link className={buttonSecondary} to={`/audit/${sessionId}`}>
              Open audit
            </Link>
          </div>
        </div>
        <div className={`${insetPanel} grid content-start gap-5 border border-slate-200/80 bg-white/90`}>
          <div>
            <p className={eyebrow}>Score snapshot</p>
            <p className="mt-2 font-display text-5xl tracking-tight text-slate-950">
              {result.overall_score.toFixed(1)}
            </p>
            <p className="mt-1 text-sm text-slate-500">Overall score</p>
          </div>
          <div className="rounded-[22px] border border-slate-200/80 bg-slate-50/80 p-4">
            <p className="text-sm font-medium text-slate-600">Confidence</p>
            <p className="mt-2 font-display text-4xl tracking-tight text-slate-950">
              {result.confidence.toFixed(2)}
            </p>
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <RadarChartCard
          labels={result.chart_payload.labels}
          scores={result.chart_payload.scores}
        />
        <ScoreBreakdownCard
          dimensions={result.dimension_scores}
          strengths={result.strengths}
          weaknesses={result.weaknesses}
        />
      </div>
    </div>
  )
}
