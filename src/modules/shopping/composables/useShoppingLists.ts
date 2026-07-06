/**
 * Composable for the collection of shopping lists and family categories.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { CreateCategoryRequest, UpdateCategoryRequest } from '../types'
import { shoppingService } from '../services/shoppingService'

export const shoppingKeys = {
  all: ['shopping'] as const,
  lists: ['shopping', 'lists'] as const,
  list: (id: string) => ['shopping', 'lists', id] as const,
  categories: ['shopping', 'categories'] as const,
}

export function useShoppingLists() {
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const { handleError } = useHandleError()

  const { data: lists, isLoading: isLoadingLists } = useQuery({
    queryKey: shoppingKeys.lists,
    queryFn: () => shoppingService.getLists(),
  })

  const { data: categories } = useQuery({
    queryKey: shoppingKeys.categories,
    queryFn: () => shoppingService.getCategories(),
  })

  const invalidateLists = () => queryClient.invalidateQueries({ queryKey: shoppingKeys.lists })
  const invalidateCategories = () => queryClient.invalidateQueries({ queryKey: shoppingKeys.categories })

  const createListMutation = useMutation({
    mutationFn: (name: string) => shoppingService.createList({ name }),
    onSuccess: async () => {
      toast.success(t('shopping.toasts.listCreated'))
      await invalidateLists()
      await invalidateCategories()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.listError') }),
  })

  const deleteListMutation = useMutation({
    mutationFn: (listId: string) => shoppingService.deleteList(listId),
    onSuccess: async () => {
      toast.success(t('shopping.toasts.listDeleted'))
      await invalidateLists()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.listError') }),
  })

  const createCategoryMutation = useMutation({
    mutationFn: (request: CreateCategoryRequest) => shoppingService.createCategory(request),
    onSuccess: async () => {
      toast.success(t('shopping.toasts.categorySaved'))
      await invalidateCategories()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.categoryError') }),
  })

  const updateCategoryMutation = useMutation({
    mutationFn: ({ id, request }: { id: string, request: UpdateCategoryRequest }) => shoppingService.updateCategory(id, request),
    onSuccess: async () => {
      toast.success(t('shopping.toasts.categorySaved'))
      await invalidateCategories()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.categoryError') }),
  })

  const deleteCategoryMutation = useMutation({
    mutationFn: (categoryId: string) => shoppingService.deleteCategory(categoryId),
    onSuccess: async () => {
      toast.success(t('shopping.toasts.categoryDeleted'))
      await invalidateCategories()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.categoryError') }),
  })

  return {
    lists,
    categories,
    isLoadingLists,
    createList: createListMutation.mutateAsync,
    isCreatingList: computed(() => createListMutation.isPending.value),
    deleteList: deleteListMutation.mutateAsync,
    createCategory: createCategoryMutation.mutateAsync,
    updateCategory: updateCategoryMutation.mutateAsync,
    deleteCategory: deleteCategoryMutation.mutateAsync,
  }
}
