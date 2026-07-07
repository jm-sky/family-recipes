/**
 * Composable for managing subscription state with TanStack Query.
 * Current plan display uses the family plan (source of truth for family-recipes).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { isAxiosError } from 'axios'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { familyQueryKeys } from '@/modules/family/composables/useFamily'
import { familyService } from '@/modules/family/services/familyService'
import { useHandleError } from '@/shared/composables/useHandleError'
import { config } from '@/shared/config/config'
import type {
  BillingInterval,
  CreateCheckoutSessionRequest,
  PlanTier,
  UpdateOpenRouterTokenRequest,
} from '../types'
import { BillingRoutePaths } from '../routes'
import { billingService } from '../services/billingService'
import { PLAN_FEATURES } from '../types'

export function useSubscription() {
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const { handleError } = useHandleError()

  const stripeEnabled = config.stripe.enabled

  const {
    data: family,
    isLoading: isLoadingFamily,
    error: familyError,
  } = useQuery({
    queryKey: familyQueryKeys.me,
    queryFn: () => familyService.getMyFamily(),
    retry: (failureCount, error) => {
      if (isAxiosError(error) && error.response?.status === 404) return false
      return failureCount < 2
    },
    staleTime: 60 * 1000,
  })

  const {
    data: subscription,
    isLoading: isLoadingSubscription,
    error: subscriptionError,
    refetch: refetchSubscription,
  } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => billingService.getSubscription(),
    staleTime: 5 * 60 * 1000,
  })

  const {
    data: limits,
    isLoading: isLoadingLimits,
    error: limitsError,
  } = useQuery({
    queryKey: ['subscription', 'limits'],
    queryFn: () => billingService.getSubscriptionLimits(),
    staleTime: 5 * 60 * 1000,
    enabled: stripeEnabled,
  })

  const createCheckoutMutation = useMutation({
    mutationFn: (request: CreateCheckoutSessionRequest) =>
      billingService.createCheckoutSession(request),
    onSuccess: (data) => {
      window.location.href = data.sessionUrl
    },
    onError: (error) => {
      handleError(error, {
        fallbackMessage: t('billing.errors.checkoutFailed', 'Failed to create checkout session. Please try again.'),
      })
    },
  })

  const createPortalMutation = useMutation({
    mutationFn: () =>
      billingService.createPortalSession({
        returnUrl: window.location.href,
      }),
    onSuccess: (data) => {
      window.location.href = data.sessionUrl
    },
    onError: (error) => {
      handleError(error, {
        fallbackMessage: t('billing.errors.portalFailed', 'Failed to open billing portal. Please try again.'),
      })
    },
  })

  const cancelSubscriptionMutation = useMutation({
    mutationFn: () => billingService.cancelSubscription(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] })
    },
  })

  const updateOpenRouterTokenMutation = useMutation({
    mutationFn: (request: UpdateOpenRouterTokenRequest) =>
      billingService.updateOpenRouterToken(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] })
    },
  })

  // Family plan is the source of truth for what the user sees
  const currentPlan = computed<PlanTier>(() => family.value?.plan ?? 'free')
  const currentPlanFeatures = computed(() => PLAN_FEATURES[currentPlan.value])
  const isFreeTier = computed(() => currentPlan.value === 'free')
  const isBasicTier = computed(() => currentPlan.value === 'basic')
  const isProTier = computed(() => currentPlan.value === 'pro')
  const isPaidTier = computed(() => !isFreeTier.value)
  const isGrandfathered = computed(() => subscription.value?.isGrandfathered || false)
  const isCanceled = computed(() => subscription.value?.status === 'canceled')
  const isPastDue = computed(() => subscription.value?.status === 'past_due')
  const cancelAtPeriodEnd = computed(() => subscription.value?.cancelAtPeriodEnd || false)

  const hasActiveSubscription = computed(
    () => stripeEnabled && subscription.value?.status === 'active' && !cancelAtPeriodEnd.value,
  )

  const canUpgradeTo = (targetPlan: PlanTier) => {
    if (!stripeEnabled || isGrandfathered.value) return false
    if (currentPlan.value === 'free') return targetPlan !== 'free'
    if (currentPlan.value === 'basic') return targetPlan === 'pro'
    return false
  }

  const canDowngradeTo = (targetPlan: PlanTier) => {
    if (!stripeEnabled || isGrandfathered.value) return false
    if (currentPlan.value === 'pro') return targetPlan !== 'pro'
    if (currentPlan.value === 'basic') return targetPlan === 'free'
    return false
  }

  const upgradeToPlan = async (planTier: Exclude<PlanTier, 'free'>, billingInterval: BillingInterval) => {
    const successUrl = `${window.location.origin}${BillingRoutePaths.success}`
    const cancelUrl = `${window.location.origin}${BillingRoutePaths.cancel}`

    await createCheckoutMutation.mutateAsync({
      planTier,
      billingInterval,
      successUrl,
      cancelUrl,
    })
  }

  const openBillingPortal = async () => {
    await createPortalMutation.mutateAsync()
  }

  const cancelSubscription = async () => {
    await cancelSubscriptionMutation.mutateAsync()
  }

  const updateOpenRouterToken = async (token: string | null) => {
    await updateOpenRouterTokenMutation.mutateAsync({
      openrouterApiToken: token,
    })
  }

  const hasNoFamily = computed(() => {
    const error = familyError.value
    return !!error && isAxiosError(error) && error.response?.status === 404
  })

  return {
    family,
    hasNoFamily,
    subscription,
    limits,
    currentPlan,
    currentPlanFeatures,
    stripeEnabled,

    isLoadingFamily,
    isLoadingSubscription,
    isLoadingLimits,
    isLoading: computed(() => isLoadingFamily.value || isLoadingSubscription.value || isLoadingLimits.value),

    subscriptionError,
    limitsError,
    error: computed(() => subscriptionError.value || limitsError.value),

    isFreeTier,
    isBasicTier,
    isProTier,
    isPaidTier,
    isGrandfathered,
    isCanceled,
    isPastDue,
    cancelAtPeriodEnd,
    hasActiveSubscription,

    canUpgradeTo,
    canDowngradeTo,

    upgradeToPlan,
    openBillingPortal,
    cancelSubscription,
    updateOpenRouterToken,
    refetchSubscription,

    isUpgrading: computed(() => createCheckoutMutation.isPending.value),
    isOpeningPortal: computed(() => createPortalMutation.isPending.value),
    isCanceling: computed(() => cancelSubscriptionMutation.isPending.value),
    isUpdatingToken: computed(() => updateOpenRouterTokenMutation.isPending.value),
  }
}
