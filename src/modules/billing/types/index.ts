/**
 * TypeScript types for billing / family plan display
 */

export type PlanTier = 'free' | 'basic' | 'pro'

export type BillingInterval = 'monthly' | 'annual'

/** Values stored/returned by the API (Stripe-style). */
export type SubscriptionBillingInterval = 'month' | 'year'

export type SubscriptionStatus = 'active' | 'canceled' | 'past_due' | 'unpaid' | 'incomplete'

/** Stripe subscription record; plan display uses family plan instead. */
export interface Subscription {
  id: string
  userId: string
  stripeCustomerId: string | null
  stripeSubscriptionId: string | null
  planTier: 'free' | 'basic' | 'pro'
  billingInterval: SubscriptionBillingInterval | null
  status: SubscriptionStatus
  currentPeriodStart: string | null
  currentPeriodEnd: string | null
  cancelAtPeriodEnd: boolean
  isGrandfathered: boolean
  createdAt: string
  updatedAt: string
}

export interface SubscriptionLimits {
  planTier: PlanTier
  aiMonthlyTokenLimit: number
  storageLimit: number
  canExportData: boolean
  canUseAdvancedFeatures: boolean
  requiresByok: boolean
}

export interface CreateCheckoutSessionRequest {
  planTier: Exclude<PlanTier, 'free'>
  billingInterval: BillingInterval
  successUrl: string
  cancelUrl: string
}

export interface CheckoutSessionResponse {
  sessionId: string
  sessionUrl: string
}

export interface CreatePortalSessionRequest {
  returnUrl: string
}

export interface PortalSessionResponse {
  sessionUrl: string
}

export interface UpdateOpenRouterTokenRequest {
  openrouterApiToken: string | null
}

export interface PlanFeatures {
  tier: PlanTier
  name: string
  price: {
    monthly: number
    annual: number
    annualMonthly: number
  }
  features: string[]
  memberLimit: number | null
  popular?: boolean
}

/** Accepted PLN list prices (2026-08-03 monetization plan). */
export const PLAN_FEATURES: Record<PlanTier, PlanFeatures> = {
  free: {
    tier: 'free',
    name: 'Free',
    price: {
      monthly: 0,
      annual: 0,
      annualMonthly: 0,
    },
    features: [
      'Up to 2 family members',
      'Shared shopping lists',
      'Shared family recipes',
      'Google Keep export',
      'AI import with your own OpenRouter key',
    ],
    memberLimit: 2,
  },
  basic: {
    tier: 'basic',
    name: 'Basic',
    price: {
      monthly: 9.99,
      annual: 99,
      annualMonthly: 8.25,
    },
    features: [
      'Up to 5 family members',
      'Everything in Free',
      'AI recipe import (system key, limited)',
    ],
    memberLimit: 5,
    popular: true,
  },
  pro: {
    tier: 'pro',
    name: 'Pro',
    price: {
      monthly: 14.99,
      annual: 149,
      annualMonthly: 12.42,
    },
    features: [
      'Unlimited family members',
      'Everything in Basic',
      'Higher AI budget (system key)',
    ],
    memberLimit: null,
  },
}

export const ANNUAL_DISCOUNT_PERCENT = 17

export function formatPln(amount: number): string {
  return `${amount.toFixed(2).replace('.', ',')} zł`
}
