<script setup lang="ts">
import { ArrowLeft, ChevronDown, Plus, Trash2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
const showCategory = ref(false)
const detailName = ref('')
const detailQuantity = ref('')
const detailUnit = ref('')
const detailCategory = ref('')

const NO_UNIT = '__none__'
const NO_CATEGORY = '__none__'

const categoryName = (categoryId: string | null): string => {
  if (!categoryId) return t('shopping.list.uncategorized')
  return categories.value?.find(c => c.id === categoryId)?.name ?? t('shopping.list.uncategorized')
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
    items: groups.get(key)!.slice().sort((a, b) => Number(a.isChecked) - Number(b.isChecked) || a.position - b.position),
  }))
})

const progress = computed(() => {
  const total = list.value?.itemCount ?? 0
  if (total === 0) return 0
  return Math.round(((list.value?.checkedCount ?? 0) / total) * 100)
})

async function handleStructuredAdd() {
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

async function handleQuickAdd() {
  const text = quickAddText.value.trim()
  if (!text) return
  await quickAdd(text)
  quickAddText.value = ''
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

        <!-- Structured add (always visible) -->
        <Card>
          <CardContent class="space-y-3 p-4">
            <form class="space-y-3" @submit.prevent="handleStructuredAdd">
              <div class="grid gap-2 sm:grid-cols-[1fr_5.5rem_7.5rem_auto]">
                <div class="space-y-1">
                  <Label for="item-name" class="text-xs text-muted-foreground">{{ t('shopping.list.namePlaceholder') }}</Label>
                  <Input
                    id="item-name"
                    v-model="detailName"
                    :placeholder="t('shopping.list.nameExample')"
                    :disabled="isAddingItem"
                  />
                </div>
                <div class="space-y-1">
                  <Label for="item-qty" class="text-xs text-muted-foreground">{{ t('shopping.list.quantity') }}</Label>
                  <Input
                    id="item-qty"
                    v-model="detailQuantity"
                    :placeholder="t('shopping.list.quantityExample')"
                    inputmode="decimal"
                    :disabled="isAddingItem"
                  />
                </div>
                <div class="space-y-1">
                  <Label class="text-xs text-muted-foreground">{{ t('shopping.list.unit') }}</Label>
                  <Select v-model="detailUnit" :disabled="isAddingItem">
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
                </div>
                <div class="flex items-end">
                  <Button type="submit" class="w-full sm:w-auto" :disabled="!detailName.trim() || isAddingItem">
                    <Plus :size="16" />
                    {{ t('shopping.list.add') }}
                  </Button>
                </div>
              </div>

              <div>
                <button
                  type="button"
                  class="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                  @click="showCategory = !showCategory"
                >
                  <ChevronDown :size="14" class="transition-transform" :class="{ 'rotate-180': showCategory }" />
                  {{ t('shopping.list.addCategory') }}
                </button>
                <div v-if="showCategory" class="mt-2 max-w-xs">
                  <Select v-model="detailCategory" :disabled="isAddingItem">
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
                </div>
              </div>
            </form>

            <div class="border-t pt-3">
              <Label for="quick-add" class="mb-1.5 block text-xs text-muted-foreground">{{ t('shopping.list.quickAddLabel') }}</Label>
              <form class="flex items-center gap-2" @submit.prevent="handleQuickAdd">
                <Input
                  id="quick-add"
                  v-model="quickAddText"
                  :placeholder="t('shopping.list.quickAddPlaceholder')"
                  class="flex-1"
                  :disabled="isAddingItem"
                />
                <Button type="submit" variant="secondary" :disabled="!quickAddText.trim() || isAddingItem">
                  {{ t('shopping.list.quickAdd') }}
                </Button>
              </form>
            </div>
          </CardContent>
        </Card>

        <p class="text-xs text-muted-foreground">
          {{ t('shopping.list.summationHint') }}
        </p>

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
