export function cn(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(' ')
}

export const pageStack = 'flex flex-col gap-6'

export const panel =
  'rounded-[28px] border border-white/70 bg-white/88 p-6 shadow-[0_24px_70px_-28px_rgba(15,23,42,0.35)] backdrop-blur'

export const insetPanel =
  'rounded-[24px] border border-slate-200/80 bg-slate-50/85 p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.8)]'

export const eyebrow =
  'text-[0.72rem] font-semibold uppercase tracking-[0.28em] text-slate-500'

export const displayTitle =
  'font-display text-4xl leading-none tracking-tight text-slate-950 sm:text-5xl lg:text-6xl'

export const sectionTitle = 'font-display text-2xl tracking-tight text-slate-950 sm:text-3xl'

export const cardTitle = 'font-display text-xl tracking-tight text-slate-950'

export const lede = 'max-w-3xl text-sm leading-7 text-slate-600 sm:text-base'

export const mutedText = 'text-sm text-slate-500'

export const inputClass =
  'w-full rounded-2xl border border-slate-200/80 bg-white/95 px-4 py-3 text-sm text-slate-800 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-amber-500 focus:ring-4 focus:ring-amber-500/15'

export const textareaClass = `${inputClass} min-h-[220px] resize-y`

export const codeBlockClass =
  'overflow-x-auto rounded-2xl border border-slate-200/80 bg-slate-950 px-4 py-4 font-mono text-[0.82rem] leading-6 text-slate-100'

export const badgeBase =
  'inline-flex items-center rounded-full px-3 py-1 text-[0.7rem] font-semibold uppercase tracking-[0.18em]'

export const badgePrimary = `${badgeBase} border border-amber-300/70 bg-amber-100/90 text-amber-900`

export const badgeMuted = `${badgeBase} border border-slate-200/80 bg-slate-100/90 text-slate-600`

export const badgeSuccess = `${badgeBase} border border-emerald-300/70 bg-emerald-100/90 text-emerald-900`

export const buttonBase =
  'inline-flex items-center justify-center rounded-full px-4 py-2.5 text-sm font-semibold transition focus:outline-none focus:ring-4 focus:ring-amber-500/20 disabled:cursor-not-allowed disabled:opacity-55'

export const buttonPrimary =
  `${buttonBase} bg-slate-950 text-white shadow-lg shadow-slate-950/15 hover:bg-slate-800`

export const buttonSecondary =
  `${buttonBase} border border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50`

export const buttonGhost =
  `${buttonBase} bg-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900`

export const statusBase = 'rounded-2xl border px-4 py-3 text-sm font-medium shadow-sm'

export const statusClasses = {
  neutral: `${statusBase} border-slate-200/80 bg-white/90 text-slate-600`,
  success: `${statusBase} border-emerald-200 bg-emerald-50 text-emerald-800`,
  error: `${statusBase} border-rose-200 bg-rose-50 text-rose-800`,
} as const

export function recommendationTone(value: string) {
  switch (value) {
    case 'strong_hire':
      return 'border-emerald-300/80 bg-emerald-100/90 text-emerald-900'
    case 'hire':
      return 'border-sky-300/80 bg-sky-100/90 text-sky-900'
    case 'mixed':
      return 'border-amber-300/80 bg-amber-100/90 text-amber-900'
    default:
      return 'border-rose-300/80 bg-rose-100/90 text-rose-900'
  }
}
