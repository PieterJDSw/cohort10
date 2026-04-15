import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { startCandidate } from '../api/sessionsApi'
import { StartForm } from '../components/landing/StartForm'
import { cardTitle, pageStack, panel, statusClasses } from '../lib/ui'

export function LandingPage() {
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit() {
    if (!fullName.trim()) {
      setError('Enter the candidate name before starting.')
      return
    }

    try {
      setIsSubmitting(true)
      setError('')
      const response = await startCandidate(fullName)
      navigate(`/test/${response.session_id}`)
    } catch {
      setError('Unable to start the assessment session.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className={pageStack}>
      <StartForm
        fullName={fullName}
        isSubmitting={isSubmitting}
        onChange={setFullName}
        onSubmit={handleSubmit}
      />
      {error ? <p className={statusClasses.error}>{error}</p> : null}
      <section className="grid gap-4 lg:grid-cols-2">
        <article className={`${panel} grid gap-4`}>
          <h2 className={cardTitle}>What the MVP covers</h2>
          <ul className="grid gap-3 text-sm leading-6 text-slate-700">
            <li className="flex gap-3">
              <span className="mt-2 h-1.5 w-1.5 rounded-full bg-amber-600" />
              <span>FastAPI backend with Postgres persistence</span>
            </li>
            <li className="flex gap-3">
              <span className="mt-2 h-1.5 w-1.5 rounded-full bg-amber-600" />
              <span>React assessment workspace with Monaco editor</span>
            </li>
            <li className="flex gap-3">
              <span className="mt-2 h-1.5 w-1.5 rounded-full bg-amber-600" />
              <span>Deterministic scoring and radar chart results</span>
            </li>
          </ul>
        </article>
        <article className={`${panel} grid gap-4`}>
          <h2 className={cardTitle}>What starts automatically</h2>
          <ul className="grid gap-3 text-sm leading-6 text-slate-700">
            <li className="flex gap-3">
              <span className="mt-2 h-1.5 w-1.5 rounded-full bg-slate-900" />
              <span>Database migrations on backend boot</span>
            </li>
            <li className="flex gap-3">
              <span className="mt-2 h-1.5 w-1.5 rounded-full bg-slate-900" />
              <span>Question seeding when the DB is empty</span>
            </li>
            <li className="flex gap-3">
              <span className="mt-2 h-1.5 w-1.5 rounded-full bg-slate-900" />
              <span>Docker services for frontend, backend, and Postgres</span>
            </li>
          </ul>
        </article>
      </section>
    </div>
  )
}
