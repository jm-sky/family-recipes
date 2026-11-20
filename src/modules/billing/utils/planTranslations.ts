/**
 * Plan feature translation helpers
 */

type TranslateFn = (key: string, fallback?: string) => string

const FEATURE_KEY_MAP: Record<string, Record<string, string>> = {
  free: {
    'Up to 2 family members': 'billing.plans.free.features.memberLimit',
    'Shared shopping lists': 'billing.plans.free.features.shoppingLists',
    'Shared family recipes': 'billing.plans.free.features.recipes',
    'Google Keep export': 'billing.plans.free.features.keepExport',
    'AI import with your own OpenRouter key': 'billing.plans.free.features.aiByok',
  },
  basic: {
    'Up to 5 family members': 'billing.plans.basic.features.memberLimit',
    'Everything in Free': 'billing.plans.basic.features.everythingInFree',
    'AI recipe import (system key, limited)': 'billing.plans.basic.features.aiImport',
  },
  pro: {
    'Unlimited family members': 'billing.plans.pro.features.memberLimit',
    'Everything in Basic': 'billing.plans.pro.features.everythingInBasic',
    'Higher AI budget (system key)': 'billing.plans.pro.features.aiImport',
  },
}

export function getTranslatedFeatures(
  planTier: string,
  features: string[],
  t: TranslateFn,
): string[] {
  const map = FEATURE_KEY_MAP[planTier] ?? {}
  return features.map((feature) => {
    const key = map[feature]
    return key ? t(key, feature) : feature
  })
}

export function getPlanFullName(planTier: string, t: TranslateFn): string {
  const planKey = `billing.plans.${planTier}.fullName` as const
  return t(planKey, planTier)
}

export function getTranslatedPlanName(planTier: string, t: TranslateFn): string {
  return getPlanFullName(planTier, t)
}
