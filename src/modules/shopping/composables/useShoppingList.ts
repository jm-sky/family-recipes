/**
 * Composable for a single shopping list and its items.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { CreateItemRequest, UpdateItemRequest } from '../types'
import { shoppingService } from '../services/shoppingService'
import { shoppingSuggestionKeys } from './useProductSuggestions'
import { shoppingKeys } from './useShoppingLists'

export function useShoppingList(listIdRef: MaybeRefOrGetter<string>) {
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const { handleError } = useHandleError()

  const listId = computed(() => toValue(listIdRef))

  const { data: list, isLoading, error } = useQuery({
    queryKey: computed(() => shoppingKeys.list(listId.value)),
    queryFn: () => shoppingService.getList(listId.value),
    enabled: computed(() => !!listId.value),
  })

  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey: shoppingKeys.list(listId.value) })
    await queryClient.invalidateQueries({ queryKey: shoppingKeys.lists })
    await queryClient.invalidateQueries({ queryKey: shoppingSuggestionKeys.all })
  }

  const addItemMutation = useMutation({
    mutationFn: (request: CreateItemRequest) => shoppingService.addItem(listId.value, request),
    onSuccess: invalidate,
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.itemError') }),
  })

  const quickAddMutation = useMutation({
    mutationFn: (text: string) => shoppingService.quickAdd(listId.value, text),
    onSuccess: invalidate,
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.itemError') }),
  })

  const updateItemMutation = useMutation({
    mutationFn: ({ itemId, request }: { itemId: string, request: UpdateItemRequest }) => shoppingService.updateItem(listId.value, itemId, request),
    onSuccess: invalidate,
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.itemError') }),
  })

  const deleteItemMutation = useMutation({
    mutationFn: (itemId: string) => shoppingService.deleteItem(listId.value, itemId),
    onSuccess: async () => {
      toast.success(t('shopping.toasts.itemDeleted'))
      await invalidate()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.itemError') }),
  })

  const renameListMutation = useMutation({
    mutationFn: (name: string) => shoppingService.renameList(listId.value, name),
    onSuccess: async () => {
      toast.success(t('shopping.toasts.listRenamed'))
      await invalidate()
    },
    onError: (error) => handleError(error, { fallbackMessage: t('shopping.toasts.listError') }),
  })

  return {
    list,
    isLoading,
    error,
    addItem: addItemMutation.mutateAsync,
    isAddingItem: computed(() => addItemMutation.isPending.value || quickAddMutation.isPending.value),
    quickAdd: quickAddMutation.mutateAsync,
    updateItem: updateItemMutation.mutateAsync,
    toggleItem: (itemId: string, isChecked: boolean) => updateItemMutation.mutateAsync({ itemId, request: { isChecked } }),
    deleteItem: deleteItemMutation.mutateAsync,
    renameList: renameListMutation.mutateAsync,
  }
}
