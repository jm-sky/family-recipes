<script setup lang="ts">
import { ArrowLeft, Trash2 } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import CategoryIcon from '@/modules/shopping/components/CategoryIcon.vue'
import ProductAddPanel from '@/modules/shopping/components/ProductAddPanel.vue'
import { useShoppingList } from '@/modules/shopping/composables/useShoppingList'
import { useShoppingLists } from '@/modules/shopping/composables/useShoppingLists'
import { ShoppingRoutePaths } from '@/modules/shopping/routes'
import { formatItemQuantity } from '@/modules/shopping/utils/formatQuantity'
import type { CreateItemRequest, ShoppingItem } from '@/modules/shopping/types'

const { t, locale } = useI18n()
const route = useRoute()

const listId = computed(() => String(route.params.listId ?? ''))
const { categories } = useShoppingLists()
const { list, isLoading, addItem, quickAdd, isAddingItem, toggleItem, deleteItem } = useShoppingList(listId)

const categoryName = (categoryId: string | null): string => {
  if (!categoryId) return t('shopping.list.uncategorized')
  return categories.value?.find(c => c.id === categoryId)?.name ?? t('shopping.list.uncategorized')
}

const categoryIcon = (categoryId: string | null): string | null => {
  if (!categoryId) return 'shopping-basket'
  return categories.value?.find(c => c.id === categoryId)?.icon ?? 'shopping-basket'
}

const groupedItems = computed(() => {
  const items = list.value?.items ?? []
  const groups = new Map<string, ShoppingItem[]>()
  for (const item of items) {
    const key = item.categoryId ?? ''
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(item)
  }
  const orderedKeys = (categories.value ?? []).map(c => c.id).filter(id => groups.has(id))
  if (groups.has('')) orderedKeys.push('')
  return orderedKeys.map(key => ({
    key,
    name: categoryName(key || null),
    icon: categoryIcon(key || null),
    items: groups.get(key)!.slice().sort((a, b) => Number(a.isChecked) - Number(b.isChecked) || a.position - b.position),
  }))
})

const progress = computed(() => {
  const total = list.value?.itemCount ?? 0
  if (total === 0) return 0
  return Math.round(((list.value?.checkedCount ?? 0) / total) * 100)
})

async function handleAdd(request: CreateItemRequest) {
  await addItem(request)
}

async function handleQuickAdd(text: string) {
  await quickAdd(text)
}

function formatQuantity(item: ShoppingItem): string {
  return formatItemQuantity(item.quantity, item.unit, locale.value)
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-2xl mx-auto space-y-5">
      <RouterLink :to="ShoppingRoutePaths.lists" class="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft :size="16" />
        {{ t('shopping.list.back') }}
      </RouterLink>

      <div v-if="isLoading" class="h-24 w-full bg-muted rounded animate-pulse" />

      <template v-else-if="list">
        <div class="space-y-2">
          <h1 class="text-2xl font-bold tracking-tight">
            {{ list.name }}
          </h1>
          <div class="flex items-center gap-3">
            <Progress :model-value="progress" class="h-2 flex-1" />
            <span class="text-xs text-muted-foreground whitespace-nowrap">
              {{ list.checkedCount }}/{{ list.itemCount }} {{ t('shopping.list.checked') }}
            </span>
          </div>
        </div>

        <Card>
          <CardContent class="p-4">
            <ProductAddPanel
              :categories="categories"
              :disabled="isAddingItem"
              @add="handleAdd"
              @quick-add="handleQuickAdd"
            />
          </CardContent>
        </Card>

        <p class="text-xs text-muted-foreground">
          {{ t('shopping.list.summationHint') }}
        </p>

        <div v-if="list.items.length > 0" class="space-y-5">
          <div v-for="group in groupedItems" :key="group.key">
            <div class="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              <CategoryIcon :icon="group.icon" :size="14" />
              {{ group.name }}
            </div>
            <div class="space-y-1">
              <div
                v-for="item in group.items"
                :key="item.id"
                class="flex items-center gap-3 rounded-md border p-2.5"
                :class="{ 'opacity-60': item.isChecked }"
              >
                <Checkbox :model-value="item.isChecked" @update:model-value="(v) => toggleItem(item.id, !!v)" />
                <span class="flex-1 text-sm" :class="{ 'line-through': item.isChecked }">
                  {{ item.name }}
                  <span
                    v-if="item.ingredientId"
                    class="ml-1.5 text-[10px] font-medium uppercase tracking-wide text-primary/70"
                    :title="t('shopping.list.summedHint')"
                  >
                    {{ t('shopping.list.summed') }}
                  </span>
                </span>
                <span v-if="formatQuantity(item)" class="shrink-0 text-xs tabular-nums text-muted-foreground">
                  {{ formatQuantity(item) }}
                </span>
                <Button
                  size="icon"
                  variant="ghost"
                  class="size-7"
                  @click="deleteItem(item.id)"
                >
                  <Trash2 :size="14" class="text-destructive" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        <p v-else class="text-sm text-muted-foreground">
          {{ t('shopping.list.empty') }}
        </p>
      </template>
    </div>
  </AuthenticatedLayout>
</template>
