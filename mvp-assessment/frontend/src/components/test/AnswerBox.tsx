import { cardTitle, panel, textareaClass } from '../../lib/ui'

type AnswerBoxProps = {
  value: string
  onChange: (value: string) => void
}

export function AnswerBox({ value, onChange }: AnswerBoxProps) {
  return (
    <section className={`${panel} grid gap-4`}>
      <h3 className={cardTitle}>Answer</h3>
      <textarea
        className={`${textareaClass} min-h-[260px]`}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Write the candidate answer here..."
      />
    </section>
  )
}
