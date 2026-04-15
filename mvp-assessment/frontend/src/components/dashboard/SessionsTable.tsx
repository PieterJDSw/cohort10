import { useNavigate } from 'react-router-dom'
import type { DashboardSessionRow } from '../../types/api'
import {
  badgeMuted,
  badgePrimary,
  buttonGhost,
  buttonSecondary,
  cn,
  recommendationTone,
} from '../../lib/ui'

type SessionsTableProps = {
  rows: DashboardSessionRow[]
}

export function SessionsTable({ rows }: SessionsTableProps) {
  const navigate = useNavigate()

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-separate border-spacing-0">
        <thead>
          <tr className="text-left text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
            <th className="px-4 py-3">Candidate</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Recommendation</th>
            <th className="px-4 py-3">Overall score</th>
            <th className="px-4 py-3">Confidence</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.session_id} className="group">
              <td className="border-t border-slate-200 px-4 py-4 text-sm font-semibold text-slate-950">
                {row.candidate_name}
              </td>
              <td className="border-t border-slate-200 px-4 py-4 text-sm">
                <span className={badgeMuted}>{row.status}</span>
              </td>
              <td className="border-t border-slate-200 px-4 py-4 text-sm">
                <span
                  className={cn(
                    badgePrimary,
                    'border',
                    recommendationTone(row.recommendation ?? 'pending'),
                  )}
                >
                  {row.recommendation ?? 'pending'}
                </span>
              </td>
              <td className="border-t border-slate-200 px-4 py-4 font-display text-2xl text-slate-950">
                {row.overall_score?.toFixed(1) ?? '--'}
              </td>
              <td className="border-t border-slate-200 px-4 py-4 text-sm text-slate-600">
                {row.confidence?.toFixed(2) ?? '--'}
              </td>
              <td className="border-t border-slate-200 px-4 py-4">
                <div className="flex flex-wrap items-center justify-end gap-2">
                  <button
                    className={buttonSecondary}
                    onClick={() => navigate(`/result/${row.session_id}`)}
                  >
                    Open result
                  </button>
                  <button
                    className={buttonGhost}
                    onClick={() => navigate(`/audit/${row.session_id}`)}
                  >
                    Open audit
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
