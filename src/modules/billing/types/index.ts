/**
 * TypeScript types for billing / family plan display
 */

export type PlanTier = 'free' | 'basic' | 'pro'

export type BillingInterval = 'monthly' | 'annual'

export type SubscriptionStatus = 'active' | 'canceled' | 'past_due' | 'unpaid' | 'incomplete'

/** Stripe subscription record (gear-stack); plan display uses family plan instead. */
export interface Subscription {
  id: string
  userId: string
  stripeCustomerId: string | null
  stripeSubscriptionId: string | null
  planTier: 'free' | 'pro' | 'pro_plus'
  billingInterval: BillingInterval | null
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
    ],
    memberLimit: 2,
  },
  basic: {
    tier: 'basic',
    name: 'Basic',
    price: {
      monthly: 5,
      annual: 50,
      annualMonthly: 4.17,
    },
    features: [
      'Up to 5 family members',
      'Everything in Free',
      'Shared shopping lists and recipes',
    ],
    memberLimit: 5,
    popular: true,
  },
  pro: {
    tier: 'pro',
    name: 'Pro',
    price: {
      monthly: 10,
      annual: 100,
      annualMonthly: 8.33,
    },
    features: [
      'Unlimited family members',
      'Everything in Basic',
      'AI-powered recipe import',
    ],
    memberLimit: null,
  },
}

export const ANNUAL_DISCOUNT_PERCENT = 17
