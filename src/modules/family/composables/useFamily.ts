/**
 * Composable for family state with TanStack Query
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { isAxiosError } from 'axios'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { CreateFamilyRequest } from '../types'
import { familyService } from '../services/familyService'

export const familyQueryKeys = {
  all: ['family'] as const,
  me: ['family', 'me'] as const,
  members: ['family', 'members'] as const,
  invitations: ['family', 'invitations'] as const,
}

export function useFamily() {
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const { handleError } = useHandleError()

  const {
    data: family,
    isLoading: isLoadingFamily,
    error: familyError,
  } = useQuery({
    queryKey: familyQueryKeys.me,
    queryFn: () => familyService.getMyFamily(),
    retry: (failureCount, error) => {
      // 404 means "no family yet" - don't retry, show onboarding
      if (isAxiosError(error) && error.response?.status === 404) return false
      return failureCount < 2
    },
    staleTime: 60 * 1000,
  })

  // 404 = user has no family yet (onboarding state, not an error)
  const hasNoFamily = computed(() => {
    const error = familyError.value
    return !!error && isAxiosError(error) && error.response?.status === 404
  })

  const isOwner = computed(() => family.value?.role === 'owner')

  const canInvite = computed(() => {
    if (!family.value) return false
    if (family.value.memberLimit === null) return true
    return family.value.memberCount < family.value.memberLimit
  })

  const { data: members, isLoading: isLoadingMembers } = useQuery({
    queryKey: familyQueryKeys.members,
    queryFn: () => familyService.getMembers(),
    enabled: computed(() => !!family.value),
  })

  const { data: invitations } = useQuery({
    queryKey: familyQueryKeys.invitations,
    queryFn: () => familyService.getInvitations(),
    enabled: computed(() => !!family.value),
  })

  const invalidateFamily = async () => {
    await queryClient.invalidateQueries({ queryKey: familyQueryKeys.all })
  }

  const createFamilyMutation = useMutation({
    mutationFn: (request: CreateFamilyRequest) => familyService.createFamily(request),
    onSuccess: async () => {
      toast.success(t('family.toasts.created'))
      await invalidateFamily()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('family.toasts.createError') }),
  })

  const createInvitationMutation = useMutation({
    mutationFn: () => familyService.createInvitation(),
    onSuccess: async () => {
      toast.success(t('family.toasts.invitationCreated'))
      await invalidateFamily()
    },
    onError: (error) => {
      if (isAxiosError(error) && error.response?.status === 403) {
        toast.error(t('family.toasts.memberLimitReached'))
        return
      }
      handleError(error, { fallbackMessage: t('family.toasts.invitationError') })
    },
  })

  const removeMemberMutation = useMutation({
    mutationFn: (userId: string) => familyService.removeMember(userId),
    onSuccess: async () => {
      toast.success(t('family.toasts.memberRemoved'))
      await invalidateFamily()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('family.toasts.removeMemberError') }),
  })

  return {
    family,
    members,
    invitations,
    isLoadingFamily,
    isLoadingMembers,
    hasNoFamily,
    isOwner,
    canInvite,
    createFamily: createFamilyMutation.mutateAsync,
    isCreatingFamily: computed(() => createFamilyMutation.isPending.value),
    createInvitation: createInvitationMutation.mutateAsync,
    isCreatingInvitation: computed(() => createInvitationMutation.isPending.value),
    removeMember: removeMemberMutation.mutateAsync,
    invalidateFamily,
  }
}
