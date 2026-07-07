/**
 * Composable for AI recipe import from URL
 */

import { useMutation } from '@tanstack/vue-query'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { RecipeImportDraft } from '../types'
import { recipeService } from '../services/recipeService'

export function useRecipeImport() {
  const { t } = useI18n()
  const { handleError } = useHandleError()

  const importMutation = useMutation({
    mutationFn: (url: string) => recipeService.importFromUrl(url),
    onSuccess: () => {
      toast.success(t('recipes.import.success'))
    },
    onError: (error) => handleError(error, { fallbackMessage: t('recipes.import.error') }),
  })

  return {
    importFromUrl: importMutation.mutateAsync,
    isImporting: computed(() => importMutation.isPending.value),
    lastDraft: computed(() => importMutation.data.value as RecipeImportDraft | undefined),
  }
}
