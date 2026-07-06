<script setup lang="ts">
import { ArrowLeft, Plus, Trash2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import Select from '@/components/ui/select/Select.vue'
import SelectContent from '@/components/ui/select/SelectContent.vue'
import SelectItem from '@/components/ui/select/SelectItem.vue'
import SelectTrigger from '@/components/ui/select/SelectTrigger.vue'
import SelectValue from '@/components/ui/select/SelectValue.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useShoppingList } from '@/modules/shopping/composables/useShoppingList'
import { useShoppingLists } from '@/modules/shopping/composables/useShoppingLists'
import { ShoppingRoutePaths } from '@/modules/shopping/routes'
import { UNITS } from '@/modules/shopping/types'
import { formatItemQuantity } from '@/modules/shopping/utils/formatQuantity'
import type { ShoppingItem } from '@/modules/shopping/types'

const { t, locale } = useI18n()
const route = useRoute()

const listId = computed(() => String(route.params.listId ?? ''))
const { categories } = useShoppingLists()
const { list, isLoading, addItem, quickAdd, isAddingItem, toggleItem, deleteItem } = useShoppingList(listId)

const quickAddText = ref('')
const showDetailed = ref(false)
const detailName = ref('')
const detailQuantity = ref<string>('')
const detailUnit = ref<string>('')
const detailCategory = ref<string>('')

const NO_UNIT = '__none__'
const NO_CATEGORY = '__none__'

const categoryName = (categoryId: string | null): string => {
  if (!categoryId) return t('shopping.list.uncategorized')
  return categories.value?.find(c => c.id === categoryId)?.name ?? t('shopping.list.uncategorized')
}

// Group items by category, preserving category sort order; uncategorized last.
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
    items: groups.get(key)!.slice().sort((a, b) => Number(a.isChecked) - Number(b.isChecked) || a.position - b.position),
  }))
})

const progress = computed(() => {
  const total = list.value?.itemCount ?? 0
  if (total === 0) return 0
  return Math.round(((list.value?.checkedCount ?? 0) / total) * 100)
})

async function handleQuickAdd() {
  const text = quickAddText.value.trim()
  if (!text) return
  await quickAdd(text)
  quickAddText.value = ''
}

async function handleDetailedAdd() {
  const name = detailName.value.trim()
  if (!name) return
  await addItem({
    name,
    quantity: detailQuantity.value ? Number(detailQuantity.value.replace(',', '.')) : null,
    unit: detailUnit.value && detailUnit.value !== NO_UNIT ? detailUnit.value : null,
    categoryId: detailCategory.value && detailCategory.value !== NO_CATEGORY ? detailCategory.value : null,
  })
  detailName.value = ''
  detailQuantity.value = ''
  detailUnit.value = ''
  detailCategory.value = ''
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

        <!-- Quick add -->
        <form class="flex items-center gap-2" @submit.prevent="handleQuickAdd">
          <Input
            v-model="quickAddText"
            :placeholder="t('shopping.list.quickAddPlaceholder')"
            class="flex-1"
            :disabled="isAddingItem"
          />
          <Button type="submit" :disabled="!quickAddText.trim() || isAddingItem">
            <Plus :size="16" />
            {{ t('shopping.list.add') }}
          </Button>
        </form>

        <div>
          <button type="button" class="text-xs text-muted-foreground hover:text-foreground" @click="showDetailed = !showDetailed">
            {{ t('shopping.list.addDetailed') }}
          </button>
        </div>

        <!-- Detailed add -->
        <Card v-if="showDetailed">
          <CardContent class="p-4">
            <form class="grid gap-2 sm:grid-cols-[1fr_5rem_8rem_10rem_auto]" @submit.prevent="handleDetailedAdd">
              <Input v-model="detailName" :placeholder="t('shopping.list.namePlaceholder')" />
              <Input v-model="detailQuantity" :placeholder="t('shopping.list.quantity')" inputmode="decimal" />
              <Select v-model="detailUnit">
                <SelectTrigger>
                  <SelectValue :placeholder="t('shopping.list.noUnit')" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem :value="NO_UNIT">
                    {{ t('shopping.list.noUnit') }}
                  </SelectItem>
                  <SelectItem v-for="unit in UNITS" :key="unit" :value="unit">
                    {{ unit }}
                  </SelectItem>
                </SelectContent>
              </Select>
              <Select v-model="detailCategory">
                <SelectTrigger>
                  <SelectValue :placeholder="t('shopping.list.noCategory')" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem :value="NO_CATEGORY">
                    {{ t('shopping.list.noCategory') }}
                  </SelectItem>
                  <SelectItem v-for="category in categories ?? []" :key="category.id" :value="category.id">
                    {{ category.name }}
                  </SelectItem>
                </SelectContent>
              </Select>
              <Button type="submit" :disabled="!detailName.trim() || isAddingItem">
                <Plus :size="16" />
              </Button>
            </form>
          </CardContent>
        </Card>

        <!-- Items grouped by category -->
        <div v-if="list.items.length > 0" class="space-y-5">
          <div v-for="group in groupedItems" :key="group.key">
            <h2 class="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {{ group.name }}
            </h2>
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
