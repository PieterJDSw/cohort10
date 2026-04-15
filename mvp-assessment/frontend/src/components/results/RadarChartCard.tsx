import {
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  PointElement,
  RadialLinearScale,
  Tooltip,
} from 'chart.js'
import { Radar } from 'react-chartjs-2'
import { formatDimensionLabel } from '../../lib/dimensions'
import { cardTitle, panel } from '../../lib/ui'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

type RadarChartCardProps = {
  labels: string[]
  scores: number[]
}

export function RadarChartCard({ labels, scores }: RadarChartCardProps) {
  const formattedLabels = labels.map(formatDimensionLabel)

  return (
    <section className={`${panel} grid gap-4`}>
      <div className="flex items-center justify-between gap-3">
        <h3 className={cardTitle}>Dimension radar</h3>
        <p className="text-sm text-slate-500">A quick view of strengths across the scoring model.</p>
      </div>
      <div className="h-[360px] rounded-[26px] border border-slate-200/80 bg-slate-50/80 p-4">
        <Radar
          data={{
            labels: formattedLabels,
            datasets: [
              {
                label: 'Score',
                data: scores,
                fill: true,
                backgroundColor: 'rgba(217, 119, 6, 0.16)',
                borderColor: '#b45309',
                pointBackgroundColor: '#0f172a',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#0f172a',
              },
            ],
          }}
          options={{
            maintainAspectRatio: false,
            plugins: {
              legend: {
                labels: {
                  color: '#334155',
                },
              },
            },
            scales: {
              r: {
                suggestedMin: 0,
                suggestedMax: 100,
                angleLines: { color: 'rgba(148, 163, 184, 0.25)' },
                grid: { color: 'rgba(148, 163, 184, 0.25)' },
                pointLabels: { color: '#334155', font: { size: 12 } },
                ticks: { backdropColor: 'transparent', color: '#64748b' },
              },
            },
          }}
        />
      </div>
    </section>
  )
}
