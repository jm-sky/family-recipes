/**
 * Google Keep integration API service (/integrations/keep/*).
 */

import { apiClient } from '@/shared/services/apiClient'
import type {
  KeepConnectRequest,
  KeepMirror,
  KeepMirrorCreateRequest,
  KeepStatus,
  KeepSyncAllResultItem,
} from '../types/keep.type'

export const keepIntegrationService = {
  async getStatus(): Promise<KeepStatus> {
    const response = await apiClient.get<KeepStatus>('/integrations/keep/status')
    return response.data
  },

  async connect(request: KeepConnectRequest): Promise<KeepStatus> {
    const response = await apiClient.post<KeepStatus>('/integrations/keep/connect', request)
    return response.data
  },

  async disconnect(): Promise<void> {
    await apiClient.delete('/integrations/keep/disconnect')
  },

  async getMirrors(): Promise<KeepMirror[]> {
    const response = await apiClient.get<{ mirrors: KeepMirror[] }>('/integrations/keep/mirrors')
    return response.data.mirrors
  },

  async createMirror(request: KeepMirrorCreateRequest): Promise<KeepMirror> {
    const response = await apiClient.post<KeepMirror>('/integrations/keep/mirrors', request)
    return response.data
  },

  async deleteMirror(mirrorId: string): Promise<void> {
    await apiClient.delete(`/integrations/keep/mirrors/${mirrorId}`)
  },

  async updateMirror(mirrorId: string, autoSync: boolean): Promise<KeepMirror> {
    const response = await apiClient.patch<KeepMirror>(`/integrations/keep/mirrors/${mirrorId}`, { autoSync })
    return response.data
  },

  async syncMirror(mirrorId: string): Promise<KeepMirror> {
    const response = await apiClient.post<KeepMirror>(`/integrations/keep/mirrors/${mirrorId}/sync`)
    return response.data
  },

  async syncAll(): Promise<KeepSyncAllResultItem[]> {
    const response = await apiClient.post<{ results: KeepSyncAllResultItem[] }>('/integrations/keep/sync-all')
    return response.data.results
  },
}
