import { useEffect, useState } from 'react'
import { listSessions } from '../api/dashboardApi'
import { SessionsTable } from '../components/dashboard/SessionsTable'
import { eyebrow, lede, pageStack, panel, sectionTitle, statusClasses } from '../lib/ui'
import type { DashboardSessionRow } from '../types/api'

export function DashboardPage() {
  const [rows, setRows] = useState<DashboardSessionRow[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        setRows(await listSessions())
      } catch {
        setError('Unable to load dashboard sessions.')
      }
    }

    void load()
  }, [])

  return (
    <div className={pageStack}>
      <section className={`${panel} grid gap-4`}>
        <div className="space-y-3">
          <p className={eyebrow}>Dashboard</p>
          <h1 className={sectionTitle}>All assessment sessions</h1>
          <p className={lede}>Open a result to inspect the final scoring breakdown.</p>
        </div>
      </section>
      {error ? <p className={statusClasses.error}>{error}</p> : null}
      <section className={`${panel} overflow-hidden`}>
        <SessionsTable rows={rows} />
      </section>
    </div>
  )
}
