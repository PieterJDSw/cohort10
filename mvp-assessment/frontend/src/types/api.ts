export type CandidateStartResponse = {
  candidate_id: string
  session_id: string
  status: string
}

export type SessionSummary = {
  session_id: string
  candidate_id: string
  candidate_name: string
  status: string
  started_at: string
  completed_at: string | null
  total_questions: number
  current_sequence: number
}

export type QuestionPayload = {
  session_question_id: string
  question_id: string
  type: 'coding' | 'theory' | 'architecture' | 'culture' | 'ai_fluency'
  title: string
  prompt: string
  difficulty: string
  sequence_no: number
  total_questions: number
  rubric: Record<string, string>
  metadata: Record<string, unknown>
}

export type CodeRunResult = {
  name: string
  passed: boolean
  expected?: unknown
  actual?: unknown
  error?: string
}

export type CodeRunResponse = {
  status: string
  passed: number
  total: number
  results: CodeRunResult[]
}

export type ResultPayload = {
  session_id: string
  recommendation: string
  summary: string
  overall_score: number
  confidence: number
  strengths: string[]
  weaknesses: string[]
  chart_payload: {
    labels: string[]
    scores: number[]
    confidences: number[]
    strengths: string[]
    weaknesses: string[]
    overall_score: number
    confidence: number
  }
  dimension_scores: {
    dimension_name: string
    score: number
    confidence: number
    evidence: Record<string, unknown>
  }[]
}

export type AuditSubmission = {
  id: string
  submission_type: string
  text_answer: string | null
  code_answer: string | null
  language: string | null
  created_at: string
}

export type AuditAIInteraction = {
  id: string
  user_message: string
  ai_response: string
  created_at: string
}

export type AuditEvaluatorRun = {
  id: string
  evaluator_type: string
  source: string
  confidence: number
  output_json: Record<string, unknown>
  raw_output: string | null
  error_message: string | null
  created_at: string
}

export type AuditQuestion = {
  session_question_id: string
  sequence_no: number
  status: string
  question_id: string
  question_type: 'coding' | 'theory' | 'architecture' | 'culture' | 'ai_fluency'
  title: string
  difficulty: string
  prompt: string
  rubric: Record<string, string>
  metadata: Record<string, unknown>
  submissions: AuditSubmission[]
  ai_interactions: AuditAIInteraction[]
  evaluator_runs: AuditEvaluatorRun[]
}

export type AuditPayload = {
  session_id: string
  candidate_name: string
  status: string
  started_at: string
  completed_at: string | null
  final_report: {
    recommendation: string
    summary: string
    chart_payload: Record<string, unknown>
    source: string
    raw_output: string | null
    error_message: string | null
    created_at: string
  } | null
  dimension_scores: {
    dimension_name: string
    score: number
    confidence: number
    evidence: Record<string, unknown>
  }[]
  questions: AuditQuestion[]
}

export type DashboardSessionRow = {
  session_id: string
  candidate_name: string
  status: string
  recommendation: string | null
  overall_score: number | null
  confidence: number | null
  started_at: string
  completed_at: string | null
}
