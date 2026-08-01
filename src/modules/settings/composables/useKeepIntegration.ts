import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { KeepConnectRequest, KeepMirrorCreateRequest, KeepStatus } from '../types/keep.type'
import { keepIntegrationService } from '../services/keepIntegrationService'

const STATUS_KEY = ['keep-status']
const MIRRORS_KEY = ['keep-mirrors']

export function useKeepIntegration() {
  const { t } = useI18n()
  const { handleError } = useHandleError()
  const queryClient = useQueryClient()

  const invalidateStatus = () => queryClient.invalidateQueries({ queryKey: STATUS_KEY })
  const invalidateMirrors = () => queryClient.invalidateQueries({ queryKey: MIRRORS_KEY })

  const statusQuery = useQuery<KeepStatus>({
    queryKey: STATUS_KEY,
    queryFn: () => keepIntegrationService.getStatus(),
    staleTime: 60 * 1000,
  })

  const connectMutation = useMutation({
    mutationFn: (request: KeepConnectRequest) => keepIntegrationService.connect(request),
    onSuccess: () => {
      invalidateStatus()
      toast.success(t('settings.integrations.keep.connectSuccess'))
    },
    onError: (error: unknown) => handleError(error, { fallbackMessage: t('settings.integrations.keep.connectError') }),
  })

  const disconnectMutation = useMutation({
    mutationFn: () => keepIntegrationService.disconnect(),
    onSuccess: () => {
      invalidateStatus()
      invalidateMirrors()
      toast.success(t('settings.integrations.keep.disconnectSuccess'))
    },
    onError: (error: unknown) => handleError(error, { fallbackMessage: t('settings.integrations.keep.disconnectError') }),
  })

  const mirrorsQuery = useQuery({
    queryKey: MIRRORS_KEY,
    queryFn: () => keepIntegrationService.getMirrors(),
    enabled: statusQuery.data.value?.connected ?? false,
    staleTime: 60 * 1000,
  })

  const createMirrorMutation = useMutation({
    mutationFn: (request: KeepMirrorCreateRequest) => keepIntegrationService.createMirror(request),
    onSuccess: () => {
      invalidateMirrors()
      toast.success(t('settings.integrations.keep.mirrorCreated'))
    },
    onError: (error: unknown) => handleError(error, { fallbackMessage: t('settings.integrations.keep.mirrorError') }),
  })

  const deleteMirrorMutation = useMutation({
    mutationFn: (mirrorId: string) => keepIntegrationService.deleteMirror(mirrorId),
    onSuccess: () => invalidateMirrors(),
    onError: (error: unknown) => handleError(error, { fallbackMessage: t('settings.integrations.keep.mirrorError') }),
  })

  const toggleAutoSyncMutation = useMutation({
    mutationFn: ({ mirrorId, autoSync }: { mirrorId: string, autoSync: boolean }) => keepIntegrationService.updateMirror(mirrorId, autoSync),
    onSuccess: () => invalidateMirrors(),
    onError: (error: unknown) => handleError(error, { fallbackMessage: t('settings.integrations.keep.mirrorError') }),
  })

  const syncNowMutation = useMutation({
    mutationFn: (mirrorId: string) => keepIntegrationService.syncMirror(mirrorId),
    onSuccess: () => {
      invalidateMirrors()
      toast.success(t('settings.integrations.keep.syncSuccess'))
    },
    onError: (error: unknown) => handleError(error, { fallbackMessage: t('settings.integrations.keep.syncError') }),
  })

  return {
    status: statusQuery.data,
    isStatusLoading: statusQuery.isLoading,
    mirrors: mirrorsQuery.data,
    connect: connectMutation.mutateAsync,
    isConnecting: connectMutation.isPending,
    disconnect: disconnectMutation.mutateAsync,
    isDisconnecting: disconnectMutation.isPending,
    createMirror: createMirrorMutation.mutateAsync,
    isCreatingMirror: createMirrorMutation.isPending,
    deleteMirror: deleteMirrorMutation.mutateAsync,
    toggleAutoSync: toggleAutoSyncMutation.mutateAsync,
    syncNow: syncNowMutation.mutateAsync,
    isSyncing: syncNowMutation.isPending,
  }
}
