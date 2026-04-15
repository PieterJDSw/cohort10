import { buttonGhost, buttonPrimary, buttonSecondary } from '../../lib/ui'

type SubmitBarProps = {
  isCoding: boolean
  busy: boolean
  onSave: () => void
  onRunCode: () => void
  onNext: () => void
  onFinish: () => void
}

export function SubmitBar({
  isCoding,
  busy,
  onSave,
  onRunCode,
  onNext,
  onFinish,
}: SubmitBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <button className={buttonPrimary} onClick={onSave} disabled={busy}>
        Save answer
      </button>
      {isCoding ? (
        <button className={buttonSecondary} onClick={onRunCode} disabled={busy}>
          Run code
        </button>
      ) : null}
      <button className={buttonSecondary} onClick={onNext} disabled={busy}>
        Next question
      </button>
      <button className={buttonGhost} onClick={onFinish} disabled={busy}>
        Finish session
      </button>
    </div>
  )
}
