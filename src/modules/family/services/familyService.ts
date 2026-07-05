/**
 * Family API service
 */

import { apiClient } from '@/shared/services/apiClient'
import type { CreateFamilyRequest, Family, FamilyInvitation, FamilyMember } from '../types'

export const familyService = {
  /**
   * Create a new family (creator becomes owner, plan defaults to free)
   */
  async createFamily(request: CreateFamilyRequest): Promise<Family> {
    const response = await apiClient.post<Family>('/families', request)
    return response.data
  },

  /**
   * Get current user's family
   */
  async getMyFamily(): Promise<Family> {
    const response = await apiClient.get<Family>('/families/me')
    return response.data
  },

  /**
   * List members of the current user's family
   */
  async getMembers(): Promise<FamilyMember[]> {
    const response = await apiClient.get<{ members: FamilyMember[] }>('/families/me/members')
    return response.data.members
  },

  /**
   * Remove a member from the family (owner only)
   */
  async removeMember(userId: string): Promise<void> {
    await apiClient.delete(`/families/me/members/${userId}`)
  },

  /**
   * Create an invitation link (403 when the plan member limit is reached)
   */
  async createInvitation(): Promise<FamilyInvitation> {
    const response = await apiClient.post<FamilyInvitation>('/families/me/invitations')
    return response.data
  },

  /**
   * List active invitations
   */
  async getInvitations(): Promise<FamilyInvitation[]> {
    const response = await apiClient.get<{ invitations: FamilyInvitation[] }>('/families/me/invitations')
    return response.data.invitations
  },

  /**
   * Accept an invitation link and join the family
   */
  async acceptInvitation(token: string): Promise<Family> {
    const response = await apiClient.post<Family>(`/invitations/${token}/accept`)
    return response.data
  },
}
