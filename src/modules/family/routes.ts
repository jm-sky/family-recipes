import type { RouteRecordRaw } from 'vue-router'

export const FamilyRoutePaths = {
  family: import.meta.env.VITE_FAMILY_PATH ?? '/family',
  acceptInvitation: '/invitations/:token',
  acceptInvitationByToken: (token: string) => `/invitations/${token}`,
} as const

export const FamilyRouteNames = {
  family: 'family',
  acceptInvitation: 'acceptInvitation',
} as const

export const familyRoutes: RouteRecordRaw[] = [
  {
    path: FamilyRoutePaths.family,
    name: FamilyRouteNames.family,
    component: () => import('@/modules/family/pages/FamilyPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'family.page.title' },
  },
  {
    path: FamilyRoutePaths.acceptInvitation,
    name: FamilyRouteNames.acceptInvitation,
    component: () => import('@/modules/family/pages/AcceptInvitationPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'family.accept.title' },
  },
]
