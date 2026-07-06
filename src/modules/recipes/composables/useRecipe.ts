/**
 * Composable for a single recipe (detail, edit, add-to-list)
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { CreateRecipeRequest, UpdateRecipeRequest } from '../types'
import { RecipesRoutePaths } from '../routes'
import { recipeService } from '../services/recipeService'
import { recipeKeys } from './useRecipes'

export function useRecipe(recipeIdRef: MaybeRefOrGetter<string | null>) {
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const router = useRouter()
  const { handleError } = useHandleError()

  const recipeId = computed(() => toValue(recipeIdRef))
  const isNew = computed(() => !recipeId.value)

  const { data: recipe, isLoading } = useQuery({
    queryKey: computed(() => recipeKeys.detail(recipeId.value ?? '')),
    queryFn: () => recipeService.getRecipe(recipeId.value!),
    enabled: computed(() => !!recipeId.value),
  })

  const invalidate = async () => {
    if (recipeId.value) {
      await queryClient.invalidateQueries({ queryKey: recipeKeys.detail(recipeId.value) })
    }
    await queryClient.invalidateQueries({ queryKey: recipeKeys.all })
  }

  const createMutation = useMutation({
    mutationFn: (request: CreateRecipeRequest) => recipeService.createRecipe(request),
    onSuccess: async (created) => {
      toast.success(t('recipes.toasts.created'))
      await queryClient.invalidateQueries({ queryKey: recipeKeys.all })
      await router.push(RecipesRoutePaths.detailById(created.id))
    },
    onError: (error) => handleError(error, { fallbackMessage: t('recipes.toasts.error') }),
  })

  const updateMutation = useMutation({
    mutationFn: (request: UpdateRecipeRequest) => recipeService.updateRecipe(recipeId.value!, request),
    onSuccess: async () => {
      toast.success(t('recipes.toasts.saved'))
      await invalidate()
      await router.push(RecipesRoutePaths.detailById(recipeId.value!))
    },
    onError: (error) => handleError(error, { fallbackMessage: t('recipes.toasts.error') }),
  })

  const uploadImageMutation = useMutation({
    mutationFn: (file: File) => recipeService.uploadImage(recipeId.value!, file),
    onSuccess: async () => {
      toast.success(t('recipes.toasts.imageUploaded'))
      await invalidate()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('recipes.toasts.error') }),
  })

  const addToListMutation = useMutation({
    mutationFn: ({ listId, mode }: { listId: string, mode: 'all' | 'missing' }) =>
      recipeService.addToList(recipeId.value!, listId, mode),
    onSuccess: (result) => {
      toast.success(t('recipes.detail.addToListSuccess', { added: result.addedCount, skipped: result.skippedCount }))
    },
    onError: (error) => handleError(error, { fallbackMessage: t('recipes.toasts.error') }),
  })

  return {
    recipe,
    isLoading,
    isNew,
    createRecipe: createMutation.mutateAsync,
    updateRecipe: updateMutation.mutateAsync,
    isSaving: computed(() => createMutation.isPending.value || updateMutation.isPending.value),
    uploadImage: uploadImageMutation.mutateAsync,
    isUploadingImage: computed(() => uploadImageMutation.isPending.value),
    addToList: addToListMutation.mutateAsync,
    isAddingToList: computed(() => addToListMutation.isPending.value),
  }
}
