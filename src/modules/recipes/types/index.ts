export const RECIPE_CATEGORIES = ['breakfast', 'lunch', 'dinner', 'dessert'] as const

export type RecipeCategory = typeof RECIPE_CATEGORIES[number]

export interface RecipeIngredient {
  id?: string
  name: string
  ingredientId?: string | null
  quantity: number | null
  unit: string | null
  sortOrder?: number
}

export interface RecipeTag {
  id: string
  name: string
}

export interface RecipeSummary {
  id: string
  title: string
  sourceUrl: string | null
  imageUrl: string | null
  category: RecipeCategory
  servings: number | null
  tagIds: string[]
  createdAt: string
  updatedAt: string
}

export interface RecipeDetail extends RecipeSummary {
  ingredients: RecipeIngredient[]
}

export interface CreateRecipeRequest {
  title: string
  sourceUrl?: string | null
  category: RecipeCategory
  servings?: number | null
  ingredients: { name: string, quantity?: number | null, unit?: string | null }[]
  tagIds?: string[]
}

export interface UpdateRecipeRequest {
  title?: string
  sourceUrl?: string | null
  category?: RecipeCategory
  servings?: number | null
  ingredients?: { name: string, quantity?: number | null, unit?: string | null }[]
  tagIds?: string[]
}

export interface AddToListResult {
  addedCount: number
  skippedCount: number
}
