import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getAudit } from '../api/sessionsApi'
import { formatDimensionLabel } from '../lib/dimensions'
import {
  badgeBase,
  badgeMuted,
  buttonGhost,
  buttonSecondary,
  cardTitle,
  cn,
  codeBlockClass,
  displayTitle,
  eyebrow,
  insetPanel,
  lede,
  mutedText,
  pageStack,
  panel,
  recommendationTone,
  statusClasses,
} from '../lib/ui'
import type { AuditEvaluatorRun, AuditPayload, AuditQuestion } from '../types/api'

function formatDate(value: string | null) {
  if (!value) {
    return 'Not completed'
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatList(values: unknown) {
  if (!Array.isArray(values) || values.length === 0) {
    return <p className={mutedText}>None recorded.</p>
  }

  return (
    <ul className="grid gap-2 text-sm leading-6 text-slate-700">
      {values.map((item, index) => (
        <li key={`${String(item)}-${index}`} className="flex gap-3">
          <span className="mt-2 h-1.5 w-1.5 rounded-full bg-slate-400" />
          <span>{String(item)}</span>
        </li>
      ))}
    </ul>
  )
}

function formatRecommendation(value: string) {
  return value.replaceAll('_', ' ')
}

function getLatestSubmission(question: AuditQuestion) {
  return question.submissions.at(-1) ?? null
}

function renderSubmissionBody(question: AuditQuestion) {
  const latestSubmission = getLatestSubmission(question)
  if (!latestSubmission) {
    return <p className={mutedText}>No submission saved for this question.</p>
  }

  const body = latestSubmission.code_answer ?? latestSubmission.text_answer ?? ''
  return (
    <div className="grid gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className={badgeMuted}>{latestSubmission.submission_type}</span>
        {latestSubmission.language ? (
          <span className={badgeMuted}>{latestSubmission.language}</span>
        ) : null}
        <span className={mutedText}>{formatDate(latestSubmission.created_at)}</span>
      </div>
      <pre className={codeBlockClass}>{body}</pre>
      {question.submissions.length > 1 ? (
        <details className="grid gap-3 rounded-[22px] border border-slate-200/80 bg-slate-50/70 p-4">
          <summary className="cursor-pointer text-sm font-semibold text-amber-700">
            Show all saved submissions
          </summary>
          <div className="grid gap-4">
            {question.submissions.map((submission) => (
              <div key={submission.id} className="grid gap-2">
                <p className={mutedText}>
                  {submission.submission_type}
                  {submission.language ? ` | ${submission.language}` : ''} |{' '}
                  {formatDate(submission.created_at)}
                </p>
                <pre className={codeBlockClass}>
                  {submission.code_answer ?? submission.text_answer ?? ''}
                </pre>
              </div>
            ))}
          </div>
        </details>
      ) : null}
    </div>
  )
}

function renderRubric(rubric: Record<string, string>) {
  const entries = Object.entries(rubric)
  if (!entries.length) {
    return <p className={mutedText}>No rubric metadata stored.</p>
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {entries.map(([key, value]) => (
        <article
          key={key}
          className="rounded-[22px] border border-slate-200/80 bg-slate-50/85 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.6)]"
        >
          <p className={eyebrow}>{key.replaceAll('_', ' ')}</p>
          <p className="mt-2 text-sm leading-6 text-slate-700">{value}</p>
        </article>
      ))}
    </div>
  )
}

function renderRubricScores(value: unknown) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return <p className={mutedText}>No rubric scores recorded.</p>
  }

  const entries = Object.entries(value as Record<string, unknown>)
  if (!entries.length) {
    return <p className={mutedText}>No rubric scores recorded.</p>
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {entries.map(([key, score]) => (
        <article
          key={key}
          className="rounded-[22px] border border-slate-200/80 bg-slate-50/85 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.6)]"
        >
          <p className="text-sm font-medium text-slate-600">{key.replaceAll('_', ' ')}</p>
          <strong className="mt-2 block font-display text-3xl tracking-tight text-slate-950">
            {Number(score).toFixed(1)}
          </strong>
        </article>
      ))}
    </div>
  )
}

function renderEvidenceItems(value: unknown) {
  const items =
    value && typeof value === 'object' && !Array.isArray(value) && Array.isArray((value as any).items)
      ? ((value as { items: Array<Record<string, unknown>> }).items ?? [])
      : []

  if (!items.length) {
    return <p className={mutedText}>No evidence entries recorded.</p>
  }

  return (
    <div className="grid gap-3">
      {items.map((item, index) => (
        <article
          key={`${String(item.question_type)}-${index}`}
          className="rounded-[22px] border border-slate-200/80 bg-white/85 p-4"
        >
          <div className="flex flex-wrap items-center gap-2">
            <span className={badgeMuted}>{String(item.question_type ?? 'unknown')}</span>
            <span className={badgeMuted}>
              {typeof item.score === 'number' ? item.score.toFixed(1) : String(item.score ?? '')}
            </span>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-700">
            {String(item.summary ?? 'No summary recorded.')}
          </p>
        </article>
      ))}
    </div>
  )
}

function renderEvaluatorOutput(run: AuditEvaluatorRun) {
  const summary = typeof run.output_json.summary === 'string' ? run.output_json.summary : ''
  const strengths = run.output_json.strengths
  const weaknesses = run.output_json.weaknesses
  const redFlags = run.output_json.red_flags

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className={badgeMuted}>{run.evaluator_type}</span>
        <span className={badgeMuted}>{run.source}</span>
        <span className={badgeMuted}>confidence {run.confidence.toFixed(2)}</span>
        <span className={mutedText}>{formatDate(run.created_at)}</span>
      </div>
      {summary ? (
        <div className="rounded-[22px] border border-slate-200/80 bg-slate-50/80 p-4">
          <p className={eyebrow}>Summary</p>
          <p className="mt-2 text-sm leading-6 text-slate-700">{summary}</p>
        </div>
      ) : null}
      <div>
        <p className={eyebrow}>Rubric Scores</p>
        {renderRubricScores(run.output_json.rubric_scores)}
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <p className={eyebrow}>Strengths</p>
          {formatList(strengths)}
        </div>
        <div>
          <p className={eyebrow}>Weaknesses</p>
          {formatList(weaknesses)}
        </div>
        <div>
          <p className={eyebrow}>Red Flags</p>
          {formatList(redFlags)}
        </div>
      </div>
      {run.error_message ? <p className={statusClasses.error}>{run.error_message}</p> : null}
      {run.raw_output ? (
        <details className="grid gap-3 rounded-[22px] border border-slate-200/80 bg-slate-50/75 p-4">
          <summary className="cursor-pointer text-sm font-semibold text-amber-700">
            Show raw model output
          </summary>
          <pre className={codeBlockClass}>{run.raw_output}</pre>
        </details>
      ) : null}
    </div>
  )
}

function renderFinalReport(audit: AuditPayload) {
  if (!audit.final_report) {
    return null
  }

  const strengths = Array.isArray(audit.final_report.chart_payload.strengths)
    ? audit.final_report.chart_payload.strengths
    : []
  const weaknesses = Array.isArray(audit.final_report.chart_payload.weaknesses)
    ? audit.final_report.chart_payload.weaknesses
    : []

  return (
    <section className={`${panel} grid gap-5`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className={cardTitle}>Final Synthesis</h3>
        <span className={badgeMuted}>
          {audit.final_report.source} | {formatDate(audit.final_report.created_at)}
        </span>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={cn(
            badgeBase,
            'border',
            recommendationTone(audit.final_report.recommendation),
          )}
        >
          {formatRecommendation(audit.final_report.recommendation)}
        </span>
        <span className={badgeMuted}>
          overall {Number(audit.final_report.chart_payload.overall_score ?? 0).toFixed(1)}
        </span>
        <span className={badgeMuted}>
          confidence {Number(audit.final_report.chart_payload.confidence ?? 0).toFixed(2)}
        </span>
      </div>
      <div className="rounded-[22px] border border-slate-200/80 bg-slate-50/80 p-4">
        <p className={eyebrow}>Summary</p>
        <p className="mt-2 text-sm leading-6 text-slate-700">{audit.final_report.summary}</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <p className={eyebrow}>Strengths</p>
          {formatList(strengths)}
        </div>
        <div>
          <p className={eyebrow}>Weaknesses</p>
          {formatList(weaknesses)}
        </div>
      </div>
      {audit.final_report.error_message ? (
        <p className={statusClasses.error}>{audit.final_report.error_message}</p>
      ) : null}
      {audit.final_report.raw_output ? (
        <details className="grid gap-3 rounded-[22px] border border-slate-200/80 bg-slate-50/75 p-4">
          <summary className="cursor-pointer text-sm font-semibold text-amber-700">
            Show raw model output
          </summary>
          <pre className={codeBlockClass}>{audit.final_report.raw_output}</pre>
        </details>
      ) : null}
    </section>
  )
}

export function AuditPage() {
  const { sessionId = '' } = useParams()
  const [audit, setAudit] = useState<AuditPayload | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        setAudit(await getAudit(sessionId))
      } catch {
        setError('Unable to load the audit payload.')
      }
    }

    void load()
  }, [sessionId])

  if (error) {
    return <p className={statusClasses.error}>{error}</p>
  }

  if (!audit) {
    return <p className={statusClasses.neutral}>Loading audit...</p>
  }

  return (
    <div className={pageStack}>
      <section className={`${panel} grid gap-6 lg:grid-cols-[minmax(0,1.45fr)_minmax(280px,0.8fr)]`}>
        <div className="grid gap-4">
          <p className={eyebrow}>Audit trail</p>
          <h1 className={displayTitle}>{audit.candidate_name}</h1>
          <p className={lede}>
            Inspect the stored helper chats, evaluator JSON, dimension evidence, and final
            synthesis for session <code>{audit.session_id}</code>.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Link className={buttonSecondary} to={`/result/${audit.session_id}`}>
              Open result
            </Link>
            <Link className={buttonGhost} to="/dashboard">
              Back to dashboard
            </Link>
          </div>
        </div>
        <div className={`${insetPanel} grid content-start gap-3 border border-slate-200/80 bg-white/90`}>
          <p className="text-sm leading-7 text-slate-700">
            <strong>Status:</strong> {audit.status}
          </p>
          <p className="text-sm leading-7 text-slate-700">
            <strong>Started:</strong> {formatDate(audit.started_at)}
          </p>
          <p className="text-sm leading-7 text-slate-700">
            <strong>Completed:</strong> {formatDate(audit.completed_at)}
          </p>
          <p className="text-sm leading-7 text-slate-700">
            <strong>Recommendation:</strong>{' '}
            {audit.final_report?.recommendation?.replace('_', ' ') ?? 'pending'}
          </p>
        </div>
      </section>

      <section className={`${panel} grid gap-5`}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className={cardTitle}>Dimension Evidence</h3>
          <span className={badgeMuted}>{audit.dimension_scores.length} dimensions</span>
        </div>
        <div className="grid gap-4 lg:grid-cols-2 2xl:grid-cols-3">
          {audit.dimension_scores.map((dimension) => (
            <article
              key={dimension.dimension_name}
              className="rounded-[24px] border border-slate-200/80 bg-slate-50/85 p-5"
            >
              <p className="text-sm font-medium text-slate-600">
                {formatDimensionLabel(dimension.dimension_name)}
              </p>
              <strong className="mt-2 block font-display text-4xl tracking-tight text-slate-950">
                {dimension.score.toFixed(1)}
              </strong>
              <span className="mt-1 block text-sm text-slate-500">
                confidence {dimension.confidence.toFixed(2)}
              </span>
              {renderEvidenceItems(dimension.evidence)}
            </article>
          ))}
        </div>
      </section>

      {renderFinalReport(audit)}

      <section className={`${panel} grid gap-5`}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className={cardTitle}>Question Trace</h3>
          <span className={badgeMuted}>{audit.questions.length} questions</span>
        </div>
        <div className="grid gap-5">
          {audit.questions.map((question) => (
            <article
              key={question.session_question_id}
              className={`${insetPanel} grid gap-5 border border-slate-200/80 bg-white/90`}
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className={eyebrow}>
                    {question.sequence_no} / {audit.questions.length} | {question.question_type}
                  </p>
                  <h3 className="mt-2 font-display text-2xl tracking-tight text-slate-950">
                    {question.title}
                  </h3>
                </div>
                <span className={badgeMuted}>
                  {question.status} | {question.difficulty}
                </span>
              </div>

              <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">{question.prompt}</p>

              <section className="grid gap-3">
                <h4 className="font-display text-lg tracking-tight text-slate-950">Rubric</h4>
                {renderRubric(question.rubric)}
              </section>

              <section className="grid gap-3">
                <h4 className="font-display text-lg tracking-tight text-slate-950">Candidate Answer</h4>
                {renderSubmissionBody(question)}
              </section>

              <section className="grid gap-3">
                <h4 className="font-display text-lg tracking-tight text-slate-950">AI Helper</h4>
                {question.ai_interactions.length ? (
                  <div className="grid gap-4">
                    {question.ai_interactions.map((interaction) => (
                      <div key={interaction.id} className="grid gap-3">
                        <p className={mutedText}>{formatDate(interaction.created_at)}</p>
                        <div className="rounded-[22px] border border-slate-200/80 bg-slate-50/80 p-4">
                          <p className={eyebrow}>Candidate Prompt</p>
                          <p className="mt-2 text-sm leading-6 text-slate-700">
                            {interaction.user_message}
                          </p>
                        </div>
                        <div className="rounded-[22px] border border-amber-200/70 bg-amber-50/75 p-4">
                          <p className={eyebrow}>Assistant Reply</p>
                          <p className="mt-2 text-sm leading-6 text-slate-700">
                            {interaction.ai_response}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className={mutedText}>No helper conversation for this question.</p>
                )}
              </section>

              <section className="grid gap-3">
                <h4 className="font-display text-lg tracking-tight text-slate-950">Evaluator Runs</h4>
                {question.evaluator_runs.length ? (
                  <div className="grid gap-4">
                    {question.evaluator_runs.map((run) => (
                      <div key={run.id} className="grid gap-2 rounded-[24px] border border-slate-200/80 bg-slate-50/70 p-4">
                        {renderEvaluatorOutput(run)}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className={mutedText}>No evaluator output recorded for this question yet.</p>
                )}
              </section>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
