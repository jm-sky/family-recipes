import type { RouteRecordRaw } from 'vue-router'

export const ShoppingRoutePaths = {
  lists: import.meta.env.VITE_SHOPPING_PATH ?? '/shopping',
  list: '/shopping/:listId',
  listById: (listId: string) => `/shopping/${listId}`,
} as const

export const ShoppingRouteNames = {
  lists: 'shoppingLists',
  list: 'shoppingList',
} as const

export const shoppingRoutes: RouteRecordRaw[] = [
  {
    path: ShoppingRoutePaths.lists,
    name: ShoppingRouteNames.lists,
    component: () => import('@/modules/shopping/pages/ShoppingListsPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'shopping.lists.title' },
  },
  {
    path: ShoppingRoutePaths.list,
    name: ShoppingRouteNames.list,
    component: () => import('@/modules/shopping/pages/ShoppingListPage.vue'),
    meta: {
      layout: 'authenticated',
      requiresAuth: true,
      title: 'shopping.lists.title',
      backTo: ShoppingRoutePaths.lists,
    },
  },
]
