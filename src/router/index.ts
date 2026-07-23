import { nextTick } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { i18n } from '@/i18n'
import { protectAdminRoutes } from '@/modules/admin/guards/adminGuard'
import { protectRoutes } from '@/modules/auth/guards/authGuard'
import { ShoppingRouteNames, ShoppingRoutePaths } from '@/modules/shopping/routes'
import { setLastShoppingPath } from '@/modules/shopping/utils/lastShoppingPath'
import { config } from '@/shared/config/config'
import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  async scrollBehavior(to, from, savedPosition) {
    // Poczekaj na zaktualizowanie DOM
    await nextTick()
    
    // Jeśli mamy zapisaną pozycję (np. przycisk wstecz/przód), przywróć ją
    if (savedPosition) {
      return savedPosition
    }
    
    // Jeśli mamy hash w URL, przewiń do elementu z tym id
    if (to.hash) {
      // Czekamy dodatkowo, aby upewnić się, że strona jest w pełni zrenderowana
      await new Promise(resolve => setTimeout(resolve, 100))
      
      const element = document.querySelector(to.hash)
      if (element) {
        return {
          el: to.hash,
          behavior: 'smooth',
        }
      }
    }
    
    // W przeciwnym razie przewiń na górę
    return { top: 0, left: 0 }
  },
})

// Install auth guard (only active when backend is enabled)
protectRoutes(router)
// Install admin guard (checks admin access after auth)
protectAdminRoutes(router)

// Set page title on route change; remember last shopping path for nav
router.afterEach((to) => {
  if (to.name === ShoppingRouteNames.list) {
    const listId = String(to.params.listId ?? '')
    if (listId) setLastShoppingPath(ShoppingRoutePaths.listById(listId))
  }
  else if (to.name === ShoppingRouteNames.lists) {
    setLastShoppingPath(ShoppingRoutePaths.lists)
  }

  if (typeof document === 'undefined') return

  const metaTitle = to.meta.title as string | undefined
  if (metaTitle) {
    // Use type assertion to handle union type compatibility
    const title = (i18n.global.t as (key: string) => string)(metaTitle)
    document.title = `${title} | ${config.app.name}`
  } else {
    document.title = config.app.name
  }
})

export default router
