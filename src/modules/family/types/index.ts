export type FamilyPlan = 'free' | 'basic' | 'pro'

export type FamilyRole = 'owner' | 'member'

export interface Family {
  id: string
  name: string
  plan: FamilyPlan
  role: FamilyRole
  memberCount: number
  memberLimit: number | null
  createdAt: string
}

export interface FamilyMember {
  userId: string
  name: string
  email: string
  role: FamilyRole
  joinedAt: string
}

export interface FamilyInvitation {
  id: string
  token: string
  expiresAt: string | null
  createdAt: string
}

export interface InvitationPreview {
  familyName: string
  expiresAt: string | null
}

export interface CreateFamilyRequest {
  name: string
}
