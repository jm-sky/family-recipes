import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { FamilyRoutePaths } from '@/modules/family/routes'
import { RecipesRoutePaths } from '@/modules/recipes/routes'
import { ShoppingRoutePaths } from '@/modules/shopping/routes'

export const MOBILE_BOTTOM_NAV_TABS = [
  { to: AuthRoutePaths.dashboard, matchPrefix: AuthRoutePaths.dashboard },
  { to: FamilyRoutePaths.family, matchPrefix: FamilyRoutePaths.family },
  { to: RecipesRoutePaths.list, matchPrefix: RecipesRoutePaths.list },
  { to: ShoppingRoutePaths.lists, matchPrefix: ShoppingRoutePaths.lists },
] as const

export const MOBILE_BOTTOM_NAV_ROOTS = MOBILE_BOTTOM_NAV_TABS.map(tab => tab.to)

export function isMobileBottomNavRoot(path: string): boolean {
  return (MOBILE_BOTTOM_NAV_ROOTS as readonly string[]).includes(path)
}

export function isMobileBottomNavActive(path: string, matchPrefix: string): boolean {
  return path === matchPrefix || path.startsWith(`${matchPrefix}/`)
}
