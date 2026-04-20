import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { QuestionPanel } from '../components/test/QuestionPanel'
import { AnswerBox } from '../components/test/AnswerBox'
import { CodeEditorPanel } from '../components/test/CodeEditorPanel'
import { AIAssistantPanel } from '../components/test/AIAssistantPanel'
import { SubmitBar } from '../components/test/SubmitBar'
import {
  finishSession,
  getCurrentQuestion,
  getSession,
  nextQuestion,
  runCode,
  saveCodeAnswer,
  saveTextAnswer,
  sendAiChat,
} from '../api/sessionsApi'
import {
  badgeMuted,
  badgePrimary,
  buttonPrimary,
  cardTitle,
  eyebrow,
  lede,
  pageStack,
  panel,
  statusClasses,
} from '../lib/ui'
import type { CodeRunResponse, QuestionPayload, SessionSummary } from '../types/api'

type ChatMessage = {
  role: 'user' | 'assistant'
  text: string
}

function buildPythonStarter(question: QuestionPayload | null) {
  if (!question || question.type !== 'coding') {
    return ''
  }

  const entrypoint =
    typeof question.metadata?.entrypoint === 'string' ? question.metadata.entrypoint : 'solve'
  const tests = Array.isArray(question.metadata?.tests) ? question.metadata.tests : []
  const firstTest = tests[0]
  const inputCount = Array.isArray(firstTest?.input) ? firstTest.input.length : 0
  const params =
    inputCount > 0
      ? Array.from({ length: inputCount }, (_, index) => `arg${index + 1}`).join(', ')
      : ''

  return `def ${entrypoint}(${params}):\n    pass\n`
}

export function TestPage() {
  const { sessionId = '' } = useParams()
  const navigate = useNavigate()
  const [summary, setSummary] = useState<SessionSummary | null>(null)
  const [question, setQuestion] = useState<QuestionPayload | null>(null)
  const [textAnswer, setTextAnswer] = useState('')
  const [codeAnswer, setCodeAnswer] = useState('')
  const [runResult, setRunResult] = useState<CodeRunResponse | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [assistantPrompt, setAssistantPrompt] = useState('')
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [nextSummary, nextQuestionPayload] = await Promise.all([
          getSession(sessionId),
          getCurrentQuestion(sessionId),
        ])
        setSummary(nextSummary)
        setQuestion(nextQuestionPayload)
        setRunResult(null)
        setTextAnswer('')
        setCodeAnswer(buildPythonStarter(nextQuestionPayload))
      } catch {
        setError('Unable to load the session.')
      }
    }

    void load()
  }, [sessionId])

  const isCoding = question?.type === 'coding'

  async function handleSave() {
    if (!question) {
      return
    }
    try {
      setBusy(true)
      setError('')
      setStatus('')
      if (isCoding) {
        await saveCodeAnswer(sessionId, codeAnswer)
      } else {
        await saveTextAnswer(sessionId, textAnswer)
      }
      setStatus('Answer saved and queued for evaluation.')
      setSummary(await getSession(sessionId))
    } catch {
      setError('Unable to save the answer.')
    } finally {
      setBusy(false)
    }
  }

  async function handleRunCode() {
    if (!isCoding) {
      return
    }
    try {
      setBusy(true)
      setError('')
      setRunResult(await runCode(sessionId, codeAnswer))
      setStatus('Code executed against the local MVP tests.')
    } catch {
      setError('Code execution failed.')
    } finally {
      setBusy(false)
    }
  }

  async function handleNext() {
    try {
      setBusy(true)
      setError('')
      const next = await nextQuestion(sessionId)
      setQuestion(next)
      setTextAnswer('')
      setCodeAnswer(buildPythonStarter(next))
      setRunResult(null)
      setSummary(await getSession(sessionId))
      setStatus(next ? 'Moved to the next question.' : 'No more questions remain.')
    } catch {
      setError('Unable to move to the next question.')
    } finally {
      setBusy(false)
    }
  }

  async function handleFinish() {
    try {
      setBusy(true)
      setError('')
      await finishSession(sessionId)
      navigate(`/result/${sessionId}`)
    } catch {
      setError('Unable to finish the session.')
    } finally {
      setBusy(false)
    }
  }

  async function handleAiSend() {
    if (!assistantPrompt.trim()) {
      return
    }
    try {
      setBusy(true)
      setError('')
      const prompt = assistantPrompt
      setMessages((current) => [...current, { role: 'user', text: prompt }])
      setAssistantPrompt('')
      const response = await sendAiChat(sessionId, prompt)
      setMessages((current) => [...current, { role: 'assistant', text: response.response }])
    } catch {
      setError('Unable to send the AI helper message.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className={pageStack}>
      <section className={`${panel} grid gap-4`}>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-3">
            <p className={eyebrow}>Active session</p>
            <h2 className="font-display text-3xl tracking-tight text-slate-950 sm:text-4xl">
              {summary?.candidate_name ?? 'Loading session...'}
            </h2>
            <p className={lede}>
              Work through the prompt, save often, run code locally when available, and finish to
              kick off scoring.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <span className={badgePrimary}>status: {summary?.status ?? 'loading'}</span>
            <span className={badgeMuted}>
              progress: {summary?.current_sequence ?? 0}/{summary?.total_questions ?? 0}
            </span>
          </div>
        </div>
      </section>

      {error ? <p className={statusClasses.error}>{error}</p> : null}
      {status ? <p className={statusClasses.success}>{status}</p> : null}

      {question ? (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.92fr)]">
          <div className="grid gap-6">
            <QuestionPanel question={question} />
            {isCoding ? (
              <CodeEditorPanel value={codeAnswer} onChange={setCodeAnswer} />
            ) : (
              <AnswerBox value={textAnswer} onChange={setTextAnswer} />
            )}
            {runResult ? (
              <section className={`${panel} grid gap-4`}>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h3 className={cardTitle}>Run results</h3>
                  <span className={badgePrimary}>
                    {runResult.passed}/{runResult.total} passing
                  </span>
                </div>
                <ul className="grid gap-3">
                  {runResult.results.map((result) => (
                    <li
                      key={result.name}
                      className="rounded-[22px] border border-slate-200/80 bg-slate-50/85 px-4 py-3 text-sm leading-6 text-slate-700"
                    >
                      <strong className="font-semibold text-slate-950">{result.name}</strong>
                      <span className="mx-1">:</span>
                      <span className={result.passed ? 'text-emerald-700' : 'text-rose-700'}>
                        {result.passed ? 'pass' : 'fail'}
                      </span>
                      {result.error ? <span>{` | ${result.error}`}</span> : null}
                    </li>
                  ))}
                </ul>
              </section>
            ) : null}
            <SubmitBar
              isCoding={isCoding}
              busy={busy}
              onSave={handleSave}
              onRunCode={handleRunCode}
              onNext={handleNext}
              onFinish={handleFinish}
            />
          </div>
          <AIAssistantPanel
            messages={messages}
            prompt={assistantPrompt}
            busy={busy}
            onPromptChange={setAssistantPrompt}
            onSend={handleAiSend}
          />
        </div>
      ) : (
        <section className={`${panel} grid gap-4`}>
          <h2 className={cardTitle}>No active question</h2>
          <p className={lede}>The session has no current question. Finish the session to score it.</p>
          <button className={`${buttonPrimary} w-full sm:w-auto`} onClick={handleFinish} disabled={busy}>
            Finish session
          </button>
        </section>
      )}
    </div>
  )
}
