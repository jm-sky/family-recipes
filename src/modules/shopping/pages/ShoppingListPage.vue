<script setup lang="ts">
import { ArrowLeft, Folders, Minus, Plus, Search } from 'lucide-vue-next'
import { computed, reactive, ref, watch } from 'vue'
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
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import CategoryIcon from '@/modules/shopping/components/CategoryIcon.vue'
import ProductAddPanel from '@/modules/shopping/components/ProductAddPanel.vue'
import { useShoppingList } from '@/modules/shopping/composables/useShoppingList'
import { useShoppingLists } from '@/modules/shopping/composables/useShoppingLists'
import { ShoppingRoutePaths } from '@/modules/shopping/routes'
import { formatItemQuantity, toPreferredDisplayUnit } from '@/modules/shopping/utils/formatQuantity'
import { useIsMobile } from '@/shared/composables/useIsMobile'
import { useMobileAppBarTitle } from '@/shared/composables/useMobileAppBarTitle'
import {
  SHOPPING_LIST_GROUP_BY_CATEGORY_KEY,
  SHOPPING_LIST_SORT_KEY,
} from '@/shared/config/config'
import type { CreateItemRequest, ShoppingItem } from '@/modules/shopping/types'

type ListSort = 'category' | 'name' | 'uncheckedFirst'

const { t, locale } = useI18n()
const route = useRoute()
const isMobile = useIsMobile()

const listId = computed(() => String(route.params.listId ?? ''))
const { categories } = useShoppingLists()
const { list, isLoading, addItem, quickAdd, isAddingItem, toggleItem, updateItem, deleteItem } = useShoppingList(listId)

useMobileAppBarTitle(computed(() => (isMobile.value ? list.value?.name ?? null : null)))

const addSheetOpen = ref(false)
const nameDrafts = reactive<Record<string, string>>({})
const focusedNameId = ref<string | null>(null)
const itemFilter = ref('')

function readBool(key: string, fallback: boolean): boolean {
  try {
    const raw = localStorage.getItem(key)
    if (raw === null) return fallback
    return raw === 'true'
  }
  catch {
    return fallback
  }
}

function readSort(key: string, fallback: ListSort): ListSort {
  try {
    const raw = localStorage.getItem(key)
    if (raw === 'category' || raw === 'name' || raw === 'uncheckedFirst') return raw
    return fallback
  }
  catch {
    return fallback
  }
}

const groupByCategory = ref(readBool(SHOPPING_LIST_GROUP_BY_CATEGORY_KEY, true))
const listSort = ref<ListSort>(readSort(SHOPPING_LIST_SORT_KEY, 'category'))

watch(groupByCategory, (value) => {
  try {
    localStorage.setItem(SHOPPING_LIST_GROUP_BY_CATEGORY_KEY, String(value))
  }
  catch {
    // ignore
  }
})

watch(listSort, (value) => {
  try {
    localStorage.setItem(SHOPPING_LIST_SORT_KEY, value)
  }
  catch {
    // ignore
  }
})

watch(
  () => list.value?.items,
  (items) => {
    if (!items) return
    for (const item of items) {
      if (focusedNameId.value !== item.id) {
        nameDrafts[item.id] = item.name
      }
    }
  },
  { deep: true, immediate: true },
)

async function commitName(item: ShoppingItem) {
  if (item.isChecked) {
    nameDrafts[item.id] = item.name
    return
  }
  const name = (nameDrafts[item.id] ?? '').trim()
  if (!name) {
    nameDrafts[item.id] = item.name
    return
  }
  if (name !== item.name) {
    await updateItem({ itemId: item.id, request: { name } })
  }
}

function onNameKeyup(event: KeyboardEvent, item: ShoppingItem) {
  if (event.key === 'Escape') {
    nameDrafts[item.id] = item.name
    ;(event.target as HTMLTextAreaElement).blur()
  }
}

const categoryName = (categoryId: string | null): string => {
  if (!categoryId) return t('shopping.list.uncategorized')
  return categories.value?.find(c => c.id === categoryId)?.name ?? t('shopping.list.uncategorized')
}

const categoryIcon = (categoryId: string | null): string | null => {
  if (!categoryId) return 'shopping-basket'
  return categories.value?.find(c => c.id === categoryId)?.icon ?? 'shopping-basket'
}

const categoryOrder = computed(() => {
  const order = new Map<string, number>()
  ;(categories.value ?? []).forEach((category, index) => {
    order.set(category.id, index)
  })
  return order
})

function compareItems(a: ShoppingItem, b: ShoppingItem): number {
  const checked = Number(a.isChecked) - Number(b.isChecked)
  if (listSort.value === 'uncheckedFirst' && checked !== 0) return checked

  if (listSort.value === 'name') {
    const byName = a.name.localeCompare(b.name, locale.value, { sensitivity: 'base' })
    if (byName !== 0) return byName
  }

  if (listSort.value === 'category' || listSort.value === 'uncheckedFirst') {
    const aOrder = a.categoryId ? (categoryOrder.value.get(a.categoryId) ?? 999) : 1000
    const bOrder = b.categoryId ? (categoryOrder.value.get(b.categoryId) ?? 999) : 1000
    if (aOrder !== bOrder) return aOrder - bOrder
    const byName = a.name.localeCompare(b.name, locale.value, { sensitivity: 'base' })
    if (byName !== 0) return byName
  }

  if (checked !== 0) return checked
  return a.position - b.position
}

const filteredItems = computed(() => {
  const items = list.value?.items ?? []
  const query = itemFilter.value.trim().toLowerCase()
  if (!query) return items
  return items.filter(item => item.name.toLowerCase().includes(query))
})

const displaySections = computed(() => {
  const items = filteredItems.value.slice().sort(compareItems)

  if (!groupByCategory.value) {
    return [{
      key: 'all',
      name: null as string | null,
      icon: null as string | null,
      items,
    }]
  }

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
    items: groups.get(key)!,
  }))
})

const progress = computed(() => {
  const total = list.value?.itemCount ?? 0
  if (total === 0) return 0
  return Math.round(((list.value?.checkedCount ?? 0) / total) * 100)
})

async function handleAdd(request: CreateItemRequest) {
  await addItem(request)
  if (isMobile.value) addSheetOpen.value = false
}

async function handleQuickAdd(text: string) {
  await quickAdd(text)
  if (isMobile.value) addSheetOpen.value = false
}

function formatQuantity(item: ShoppingItem): string {
  return formatItemQuantity(item.quantity, item.unit, locale.value)
}

async function incrementItem(item: ShoppingItem) {
  const preferred = toPreferredDisplayUnit(item.quantity ?? 0, item.unit)
  await updateItem({
    itemId: item.id,
    request: {
      quantity: preferred.quantity + 1,
      unit: preferred.unit ?? item.unit ?? 'szt',
    },
  })
}

async function decrementItem(item: ShoppingItem) {
  const preferred = toPreferredDisplayUnit(item.quantity ?? 1, item.unit)
  if (preferred.quantity <= 1) {
    await deleteItem(item)
    return
  }
  await updateItem({
    itemId: item.id,
    request: {
      quantity: preferred.quantity - 1,
      unit: preferred.unit ?? item.unit,
    },
  })
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="mx-auto max-w-2xl space-y-5">
      <RouterLink
        v-if="!isMobile"
        :to="ShoppingRoutePaths.lists"
        class="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft :size="16" />
        {{ t('shopping.list.back') }}
      </RouterLink>

      <div v-if="isLoading" class="h-24 w-full animate-pulse rounded bg-muted" />

      <template v-else-if="list">
        <div class="space-y-2">
          <h1
            class="text-2xl font-bold tracking-tight"
            :class="{ 'sr-only': isMobile }"
          >
            {{ list.name }}
          </h1>
          <div class="flex items-center gap-3">
            <Progress :model-value="progress" class="h-2 flex-1" />
            <span class="whitespace-nowrap text-xs text-muted-foreground">
              {{ list.checkedCount }}/{{ list.itemCount }} {{ t('shopping.list.checked') }}
            </span>
          </div>
        </div>

        <!-- Mobile add sheet (trigger lives in toolbar when list has items) -->
        <template v-if="isMobile">
          <Button
            v-if="list.items.length === 0"
            type="button"
            variant="outline"
            class="min-h-(--mobile-touch-min) w-full justify-start gap-2"
            @click="addSheetOpen = true"
          >
            <Plus :size="18" />
            {{ t('shopping.list.addProduct') }}
          </Button>

          <Sheet v-model:open="addSheetOpen">
            <SheetContent
              side="bottom"
              class="max-h-[85dvh] overflow-y-auto rounded-t-xl pb-[max(1rem,env(safe-area-inset-bottom))]"
            >
              <div class="mx-auto mb-2 h-1 w-10 shrink-0 rounded-full bg-muted-foreground/30" />
              <SheetHeader class="text-left">
                <SheetTitle>{{ t('shopping.list.addProduct') }}</SheetTitle>
              </SheetHeader>
              <div class="mt-3">
                <ProductAddPanel
                  :categories="categories"
                  :disabled="isAddingItem"
                  always-expanded
                  @add="handleAdd"
                  @quick-add="handleQuickAdd"
                />
              </div>
            </SheetContent>
          </Sheet>
        </template>

        <Card v-else class="py-1">
          <CardContent class="p-4">
            <ProductAddPanel
              :categories="categories"
              :disabled="isAddingItem"
              @add="handleAdd"
              @quick-add="handleQuickAdd"
            />
          </CardContent>
        </Card>

        <p v-if="!isMobile" class="text-xs text-muted-foreground">
          {{ t('shopping.list.summationHint') }}
        </p>

        <div
          v-if="list.items.length > 0"
          class="@container/list space-y-3"
        >
          <!-- Mobile: Search + Add | Group + Sort. Desktop: filter row under add panel. -->
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <div class="relative min-w-0 flex-1">
                <Search class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  v-model="itemFilter"
                  class="pl-9"
                  :placeholder="t('shopping.list.filterPlaceholder')"
                />
              </div>
              <Button
                v-if="isMobile"
                type="button"
                class="min-h-9 shrink-0 gap-1 px-3"
                @click="addSheetOpen = true"
              >
                <Plus :size="16" />
                {{ t('shopping.list.add') }}
              </Button>
            </div>
            <div class="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="icon"
                class="size-9 shrink-0"
                :aria-pressed="groupByCategory"
                :aria-label="t('shopping.list.groupByCategory')"
                :class="{ 'border-primary bg-primary/10 text-primary': groupByCategory }"
                @click="groupByCategory = !groupByCategory"
              >
                <Folders :size="16" />
              </Button>
              <Select v-model="listSort">
                <SelectTrigger class="min-w-0 flex-1" :aria-label="t('shopping.list.sortBy')">
                  <SelectValue :placeholder="t('shopping.list.sortBy')" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="category">
                    {{ t('shopping.list.sortCategory') }}
                  </SelectItem>
                  <SelectItem value="name">
                    {{ t('shopping.list.sortName') }}
                  </SelectItem>
                  <SelectItem value="uncheckedFirst">
                    {{ t('shopping.list.sortCheckedLast') }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div v-if="filteredItems.length === 0" class="text-sm text-muted-foreground">
            {{ t('shopping.list.noMatches') }}
          </div>

          <div v-else class="space-y-5">
            <div v-for="section in displaySections" :key="section.key">
              <div
                v-if="section.name"
                class="mb-2 flex items-center gap-1.5 text-xs font-semibold tracking-wide text-muted-foreground uppercase"
              >
                <CategoryIcon :icon="section.icon" :size="14" />
                {{ section.name }}
              </div>
              <div class="space-y-1">
                <div
                  v-for="item in section.items"
                  :key="item.id"
                  class="@container/item grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-2 rounded-md border p-2 sm:gap-3 sm:p-2.5"
                  :class="{ 'opacity-60': item.isChecked }"
                >
                  <Checkbox
                    :model-value="item.isChecked"
                    @update:model-value="(v) => toggleItem(item.id, !!v)"
                  />

                  <div class="flex min-w-0 items-start gap-1">
                    <textarea
                      v-model="nameDrafts[item.id]"
                      rows="1"
                      maxlength="255"
                      :disabled="item.isChecked"
                      :aria-label="t('shopping.list.rename')"
                      class="field-sizing-content max-h-24 min-h-[1.25rem] min-w-0 flex-1 resize-none overflow-y-auto bg-transparent py-0.5 text-sm leading-snug outline-none placeholder:text-muted-foreground disabled:cursor-default"
                      :class="{ 'line-through': item.isChecked }"
                      :placeholder="t('shopping.list.namePlaceholder')"
                      @focus="focusedNameId = item.id"
                      @blur="focusedNameId = null; commitName(item)"
                      @keyup="onNameKeyup($event, item)"
                    />
                    <span
                      v-if="item.ingredientId"
                      class="self-center shrink-0 text-[10px] font-medium tracking-wide text-primary/70 uppercase"
                      :title="t('shopping.list.summedHint')"
                    >
                      {{ t('shopping.list.summed') }}
                    </span>
                  </div>

                  <div
                    class="mt-0.5 grid shrink-0 grid-cols-[2rem_5.5rem_2rem] items-center justify-items-center gap-x-0.5"
                  >
                    <Button
                      type="button"
                      size="icon"
                      variant="outline"
                      class="size-8"
                      :aria-label="t('shopping.list.decrementQuantity')"
                      :disabled="item.isChecked"
                      @click="decrementItem(item)"
                    >
                      <Minus :size="14" />
                    </Button>
                    <span class="w-full truncate text-center text-xs text-muted-foreground tabular-nums">
                      {{ formatQuantity(item) || '—' }}
                    </span>
                    <Button
                      type="button"
                      size="icon"
                      variant="outline"
                      class="size-8"
                      :aria-label="t('shopping.list.incrementQuantity')"
                      :disabled="item.isChecked"
                      @click="incrementItem(item)"
                    >
                      <Plus :size="14" />
                    </Button>
                  </div>
                </div>
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
