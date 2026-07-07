/**
 * Recipes API service
 */

import { apiClient } from '@/shared/services/apiClient'
import type {
  AddToListResult,
  CreateRecipeRequest,
  RecipeDetail,
  RecipeImportDraft,
  RecipeSummary,
  RecipeTag,
  UpdateRecipeRequest,
} from '../types'

export const recipeService = {
  async getRecipes(params?: { category?: string, tag?: string, q?: string }): Promise<RecipeSummary[]> {
    const response = await apiClient.get<{ recipes: RecipeSummary[] }>('/recipes', { params })
    return response.data.recipes
  },

  async getRecipe(recipeId: string): Promise<RecipeDetail> {
    const response = await apiClient.get<RecipeDetail>(`/recipes/${recipeId}`)
    return response.data
  },

  async createRecipe(request: CreateRecipeRequest): Promise<RecipeDetail> {
    const response = await apiClient.post<RecipeDetail>('/recipes', request)
    return response.data
  },

  async updateRecipe(recipeId: string, request: UpdateRecipeRequest): Promise<RecipeDetail> {
    const response = await apiClient.patch<RecipeDetail>(`/recipes/${recipeId}`, request)
    return response.data
  },

  async deleteRecipe(recipeId: string): Promise<void> {
    await apiClient.delete(`/recipes/${recipeId}`)
  },

  async uploadImage(recipeId: string, file: File): Promise<string> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post<{ imageUrl: string }>(`/recipes/${recipeId}/image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data.imageUrl
  },

  async addToList(recipeId: string, listId: string, mode: 'all' | 'missing'): Promise<AddToListResult> {
    const response = await apiClient.post<AddToListResult>(`/recipes/${recipeId}/add-to-list`, { listId }, { params: { mode } })
    return response.data
  },

  async getTags(): Promise<RecipeTag[]> {
    const response = await apiClient.get<{ tags: RecipeTag[] }>('/tags')
    return response.data.tags
  },

  async createTag(name: string): Promise<RecipeTag> {
    const response = await apiClient.post<RecipeTag>('/tags', { name })
    return response.data
  },

  async importFromUrl(url: string): Promise<RecipeImportDraft> {
    const response = await apiClient.post<RecipeImportDraft>('/ai/recipes/import', { url })
    return response.data
  },
}
