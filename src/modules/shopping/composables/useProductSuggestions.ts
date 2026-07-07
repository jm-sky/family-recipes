import { useQuery } from '@tanstack/vue-query'
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { shoppingService } from '@/modules/shopping/services/shoppingService'

export const shoppingSuggestionKeys = {
  all: ['shopping-suggestions'] as const,
  list: (query: string) => [...shoppingSuggestionKeys.all, query] as const,
}

export function useProductSuggestions(searchRef: MaybeRefOrGetter<string>) {
  const search = computed(() => toValue(searchRef).trim())

  return useQuery({
    queryKey: computed(() => shoppingSuggestionKeys.list(search.value)),
    queryFn: () => shoppingService.getSuggestions(search.value || undefined),
    staleTime: 60_000,
  })
}
