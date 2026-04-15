import { api } from './http'
import type {
  AuditPayload,
  CandidateStartResponse,
  CodeRunResponse,
  QuestionPayload,
  ResultPayload,
  SessionSummary,
} from '../types/api'

export async function startCandidate(fullName: string) {
  const { data } = await api.post<CandidateStartResponse>('/api/candidates/start', {
    full_name: fullName,
  })
  return data
}

export async function getSession(sessionId: string) {
  const { data } = await api.get<SessionSummary>(`/api/sessions/${sessionId}`)
  return data
}

export async function getCurrentQuestion(sessionId: string) {
  const { data } = await api.get<QuestionPayload | null>(
    `/api/sessions/${sessionId}/current-question`,
  )
  return data
}

export async function saveTextAnswer(sessionId: string, answer: string) {
  const { data } = await api.post(`/api/sessions/${sessionId}/answers/text`, {
    answer,
  })
  return data
}

export async function saveCodeAnswer(sessionId: string, code: string, language = 'python') {
  const { data } = await api.post(`/api/sessions/${sessionId}/answers/code`, {
    code,
    language,
  })
  return data
}

export async function runCode(sessionId: string, code: string, language = 'python') {
  const { data } = await api.post<CodeRunResponse>(`/api/sessions/${sessionId}/code/run`, {
    code,
    language,
  })
  return data
}

export async function sendAiChat(sessionId: string, message: string) {
  const { data } = await api.post<{ response: string }>(
    `/api/sessions/${sessionId}/ai/chat`,
    { message },
  )
  return data
}

export async function nextQuestion(sessionId: string) {
  const { data } = await api.post<QuestionPayload | null>(`/api/sessions/${sessionId}/next`)
  return data
}

export async function finishSession(sessionId: string) {
  const { data } = await api.post<ResultPayload>(`/api/sessions/${sessionId}/finish`)
  return data
}

export async function getResults(sessionId: string) {
  const { data } = await api.get<ResultPayload>(`/api/sessions/${sessionId}/results`)
  return data
}

export async function getAudit(sessionId: string) {
  const { data } = await api.get<AuditPayload>(`/api/sessions/${sessionId}/audit`)
  return data
}
