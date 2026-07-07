/**
 * Utility functions for translating plan-related content
 */

import type { PlanTier } from '../types'

type TranslateFunction = (key: string, ...args: unknown[]) => string

const featureKeyMap: Record<PlanTier, Record<string, string>> = {
  free: {
    'Up to 2 family members': 'billing.plans.free.features.memberLimit',
    'Shared shopping lists': 'billing.plans.free.features.shoppingLists',
    'Shared family recipes': 'billing.plans.free.features.recipes',
  },
  basic: {
    'Up to 5 family members': 'billing.plans.basic.features.memberLimit',
    'Everything in Free': 'billing.plans.basic.features.everythingInFree',
    'Shared shopping lists and recipes': 'billing.plans.basic.features.shoppingAndRecipes',
  },
  pro: {
    'Unlimited family members': 'billing.plans.pro.features.memberLimit',
    'Everything in Basic': 'billing.plans.pro.features.everythingInBasic',
    'AI-powered recipe import': 'billing.plans.pro.features.aiImport',
  },
}

export function getTranslatedFeatures(
  planTier: PlanTier,
  features: string[],
  t: TranslateFunction,
): string[] {
  const keyMap = featureKeyMap[planTier]

  return features.map((feature) => {
    const translationKey = keyMap[feature]
    return translationKey ? t(translationKey) : feature
  })
}

export function getTranslatedPlanName(planTier: PlanTier, t: TranslateFunction): string {
  const planKey = `billing.plans.${planTier}.fullName` as const
  return t(planKey)
}
