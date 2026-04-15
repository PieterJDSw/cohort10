import { api } from './http'
import type { DashboardSessionRow } from '../types/api'

export async function listSessions() {
  const { data } = await api.get<DashboardSessionRow[]>('/api/dashboard/sessions')
  return data
}
