/**
 * Composable for recipe collection with TanStack Query
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { RecipeCategory } from '../types'
import { recipeService } from '../services/recipeService'

export const recipeKeys = {
  all: ['recipes'] as const,
  list: (filters: { category?: string, q?: string }) => ['recipes', 'list', filters] as const,
  detail: (id: string) => ['recipes', 'detail', id] as const,
  tags: ['recipes', 'tags'] as const,
}

export function useRecipes() {
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const { handleError } = useHandleError()

  const categoryFilter = ref<RecipeCategory | ''>('')
  const searchQuery = ref('')

  const filters = computed(() => ({
    category: categoryFilter.value || undefined,
    q: searchQuery.value.trim() || undefined,
  }))

  const { data: recipes, isLoading } = useQuery({
    queryKey: computed(() => recipeKeys.list(filters.value)),
    queryFn: () => recipeService.getRecipes(filters.value),
  })

  const { data: tags } = useQuery({
    queryKey: recipeKeys.tags,
    queryFn: () => recipeService.getTags(),
  })

  const deleteMutation = useMutation({
    mutationFn: (recipeId: string) => recipeService.deleteRecipe(recipeId),
    onSuccess: async () => {
      toast.success(t('recipes.toasts.deleted'))
      await queryClient.invalidateQueries({ queryKey: recipeKeys.all })
    },
    onError: (error) => handleError(error, { fallbackMessage: t('recipes.toasts.error') }),
  })

  return {
    recipes,
    tags,
    isLoading,
    categoryFilter,
    searchQuery,
    deleteRecipe: deleteMutation.mutateAsync,
  }
}
