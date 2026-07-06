/**
 * Shopping API service (lists, categories, items).
 */

import { apiClient } from '@/shared/services/apiClient'
import type {
  Category,
  CreateCategoryRequest,
  CreateItemRequest,
  CreateListRequest,
  ShoppingItem,
  ShoppingList,
  ShoppingListDetail,
  UpdateCategoryRequest,
  UpdateItemRequest,
} from '../types'

export const shoppingService = {
  // ---- Lists ----
  async getLists(): Promise<ShoppingList[]> {
    const response = await apiClient.get<{ lists: ShoppingList[] }>('/shopping-lists')
    return response.data.lists
  },

  async createList(request: CreateListRequest): Promise<ShoppingList> {
    const response = await apiClient.post<ShoppingList>('/shopping-lists', request)
    return response.data
  },

  async getList(listId: string): Promise<ShoppingListDetail> {
    const response = await apiClient.get<ShoppingListDetail>(`/shopping-lists/${listId}`)
    return response.data
  },

  async renameList(listId: string, name: string): Promise<ShoppingList> {
    const response = await apiClient.patch<ShoppingList>(`/shopping-lists/${listId}`, { name })
    return response.data
  },

  async deleteList(listId: string): Promise<void> {
    await apiClient.delete(`/shopping-lists/${listId}`)
  },

  // ---- Items ----
  async addItem(listId: string, request: CreateItemRequest): Promise<ShoppingItem> {
    const response = await apiClient.post<ShoppingItem>(`/shopping-lists/${listId}/items`, request)
    return response.data
  },

  async quickAdd(listId: string, text: string): Promise<ShoppingItem> {
    const response = await apiClient.post<ShoppingItem>(`/shopping-lists/${listId}/items/quick-add`, { text })
    return response.data
  },

  async updateItem(listId: string, itemId: string, request: UpdateItemRequest): Promise<ShoppingItem> {
    const response = await apiClient.patch<ShoppingItem>(`/shopping-lists/${listId}/items/${itemId}`, request)
    return response.data
  },

  async deleteItem(listId: string, itemId: string): Promise<void> {
    await apiClient.delete(`/shopping-lists/${listId}/items/${itemId}`)
  },

  async reorder(listId: string, items: { id: string, position: number }[]): Promise<void> {
    await apiClient.post(`/shopping-lists/${listId}/items/reorder`, { items })
  },

  // ---- Categories ----
  async getCategories(): Promise<Category[]> {
    const response = await apiClient.get<{ categories: Category[] }>('/categories')
    return response.data.categories
  },

  async createCategory(request: CreateCategoryRequest): Promise<Category> {
    const response = await apiClient.post<Category>('/categories', request)
    return response.data
  },

  async updateCategory(categoryId: string, request: UpdateCategoryRequest): Promise<Category> {
    const response = await apiClient.patch<Category>(`/categories/${categoryId}`, request)
    return response.data
  },

  async deleteCategory(categoryId: string): Promise<void> {
    await apiClient.delete(`/categories/${categoryId}`)
  },
}
