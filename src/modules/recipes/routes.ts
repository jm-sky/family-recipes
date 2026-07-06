import type { RouteRecordRaw } from 'vue-router'
import type { RecipeCategory } from '@/modules/recipes/types'

export const RecipesRoutePaths = {
  list: import.meta.env.VITE_RECIPES_PATH ?? '/recipes',
  new: '/recipes/new',
  detail: '/recipes/:recipeId',
  edit: '/recipes/:recipeId/edit',
  detailById: (recipeId: string) => `/recipes/${recipeId}`,
  editById: (recipeId: string) => `/recipes/${recipeId}/edit`,
} as const

export const RecipesRouteNames = {
  list: 'recipesList',
  new: 'recipeNew',
  detail: 'recipeDetail',
  edit: 'recipeEdit',
} as const

export const recipeRoutes = [
  {
    path: RecipesRoutePaths.list,
    name: RecipesRouteNames.list,
    component: () => import('@/modules/recipes/pages/RecipesPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'recipes.list.title' },
  },
  {
    path: RecipesRoutePaths.new,
    name: RecipesRouteNames.new,
    component: () => import('@/modules/recipes/pages/RecipeEditPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'recipes.edit.newTitle' },
  },
  {
    path: RecipesRoutePaths.detail,
    name: RecipesRouteNames.detail,
    component: () => import('@/modules/recipes/pages/RecipeDetailPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'recipes.detail.title' },
  },
  {
    path: RecipesRoutePaths.edit,
    name: RecipesRouteNames.edit,
    component: () => import('@/modules/recipes/pages/RecipeEditPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, title: 'recipes.edit.title' },
  },
] as const satisfies readonly RouteRecordRaw[]

export function categoryLabelKey(category: RecipeCategory): string {
  return `recipes.categories.${category}`
}
