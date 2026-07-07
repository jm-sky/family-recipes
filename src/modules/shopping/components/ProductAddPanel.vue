<script setup lang="ts">
import { ChevronDown, Plus, Search } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Select from '@/components/ui/select/Select.vue'
import SelectContent from '@/components/ui/select/SelectContent.vue'
import SelectItem from '@/components/ui/select/SelectItem.vue'
import SelectTrigger from '@/components/ui/select/SelectTrigger.vue'
import SelectValue from '@/components/ui/select/SelectValue.vue'
import { cn } from '@/lib/utils'
import CategoryIcon from '@/modules/shopping/components/CategoryIcon.vue'
import { useProductSuggestions } from '@/modules/shopping/composables/useProductSuggestions'
import { type Category, type CreateItemRequest, type ProductSuggestion, UNITS } from '@/modules/shopping/types'
import { getCategoryColors } from '@/modules/shopping/utils/categoryColors'
import { useIsMobile } from '@/shared/composables/useIsMobile'
import { SHOPPING_ADD_PANEL_EXPANDED_KEY } from '@/shared/config/config'

const props = defineProps<{
  categories: Category[] | undefined
  disabled?: boolean
}>()

const emit = defineEmits<{
  add: [request: CreateItemRequest]
  quickAdd: [text: string]
}>()

const { t } = useI18n()
const isMobile = useIsMobile()

function readExpandedFromStorage(): boolean {
  try {
    return localStorage.getItem(SHOPPING_ADD_PANEL_EXPANDED_KEY) === 'true'
  }
  catch {
    return false
  }
}

function saveExpandedToStorage(expanded: boolean) {
  try {
    localStorage.setItem(SHOPPING_ADD_PANEL_EXPANDED_KEY, String(expanded))
  }
  catch {
    // ignore quota / private mode
  }
}

const isExpanded = ref(!isMobile.value)

watch(isMobile, (mobile) => {
  isExpanded.value = mobile ? readExpandedFromStorage() : true
}, { immediate: true })

watch(isExpanded, (expanded) => {
  if (isMobile.value) {
    saveExpandedToStorage(expanded)
  }
})

function toggleExpanded() {
  isExpanded.value = !isExpanded.value
}

const searchText = ref('')
const showDetails = ref(false)
const detailQuantity = ref('')
const detailUnit = ref('')
const detailCategory = ref('')
const categoryManuallySet = ref(false)

const NO_UNIT = '__none__'
const NO_CATEGORY = '__none__'

const { data: suggestionsData, isFetching } = useProductSuggestions(searchText)

const PARSEABLE_RE = [
  /^\s*\d/,
  /\d\s*[x×]/i,
  /[x×]\s*\d/i,
]

const chipSuggestions = computed(() => {
  if (searchText.value.trim()) return []
  return suggestionsData.value ?? []
})

const searchResults = computed(() => {
  const query = searchText.value.trim()
  if (!query) return []
  return suggestionsData.value ?? []
})

const bestSuggestion = computed(() => {
  const results = searchResults.value
  if (!results.length) return null
  return results.find(s => s.source === 'ingredient') ?? results[0]
})

const detectedCategory = computed(() => {
  const suggestion = bestSuggestion.value
  if (!suggestion?.categoryId) return null
  return props.categories?.find(c => c.id === suggestion.categoryId) ?? null
})

watch(bestSuggestion, (suggestion) => {
  if (!suggestion?.categoryId) return
  if (categoryManuallySet.value) return
  if (!detailCategory.value || detailCategory.value === NO_CATEGORY) {
    detailCategory.value = suggestion.categoryId
  }
})

const recentSuggestions = computed(() => chipSuggestions.value.filter(s => s.source === 'recent'))
const popularSuggestions = computed(() => chipSuggestions.value.filter(s => s.source !== 'recent'))

function categoryIconForSuggestion(suggestion: ProductSuggestion): string | null {
  if (suggestion.categoryIcon) return suggestion.categoryIcon
  if (suggestion.categoryId) {
    return props.categories?.find(c => c.id === suggestion.categoryId)?.icon ?? null
  }
  return null
}

function buildAddRequest(name: string, suggestion?: ProductSuggestion): CreateItemRequest {
  const request: CreateItemRequest = { name }
  if (suggestion?.categoryId) request.categoryId = suggestion.categoryId
  if (detailQuantity.value) request.quantity = Number(detailQuantity.value.replace(',', '.'))
  if (detailUnit.value && detailUnit.value !== NO_UNIT) request.unit = detailUnit.value
  if (!suggestion?.categoryId && detailCategory.value && detailCategory.value !== NO_CATEGORY) {
    request.categoryId = detailCategory.value
  }
  return request
}

function resetDetails() {
  detailQuantity.value = ''
  detailUnit.value = ''
  detailCategory.value = ''
  categoryManuallySet.value = false
  showDetails.value = false
}

function onCategoryChange(value: unknown) {
  detailCategory.value = String(value ?? '')
  categoryManuallySet.value = true
}

async function handleSuggestionSelect(suggestion: ProductSuggestion) {
  emit('add', buildAddRequest(suggestion.name, suggestion))
  searchText.value = ''
  resetDetails()
}

function hasManualDetails(): boolean {
  return Boolean(
    detailQuantity.value
    || (detailUnit.value && detailUnit.value !== NO_UNIT)
    || categoryManuallySet.value,
  )
}

function isParseable(text: string): boolean {
  return PARSEABLE_RE.some(re => re.test(text))
}

function findBestMatch(text: string): ProductSuggestion | undefined {
  const lower = text.toLowerCase()
  const results = searchResults.value
  const exact = results.find(s => s.name.toLowerCase() === lower)
  if (exact) return exact
  return results.find(s => lower.includes(s.name.toLowerCase()) || s.name.toLowerCase().includes(lower))
}

async function handleSubmit() {
  const text = searchText.value.trim()
  if (!text) return

  if (isParseable(text) || !hasManualDetails()) {
    emit('quickAdd', text)
  }
  else {
    const matched = findBestMatch(text)
    emit('add', buildAddRequest(matched?.name ?? text, matched))
  }

  searchText.value = ''
  resetDetails()
}
</script>

<template>
  <div :class="isMobile && !isExpanded ? '' : 'space-y-3'">
    <button
      v-if="isMobile && !isExpanded"
      type="button"
      class="flex w-full items-center gap-2 text-left text-sm leading-tight font-medium"
      @click="toggleExpanded"
    >
      <Plus :size="18" class="shrink-0 text-primary" />
      <span class="flex-1">{{ t('shopping.list.addProduct') }}</span>
      <ChevronDown :size="16" class="shrink-0 text-muted-foreground" />
    </button>

    <form v-else class="space-y-3" @submit.prevent="handleSubmit">
      <button
        v-if="isMobile"
        type="button"
        class="flex w-full items-center gap-2 text-left text-sm font-medium"
        @click="toggleExpanded"
      >
        <Plus :size="18" class="shrink-0 text-primary" />
        <span class="flex-1">{{ t('shopping.list.addProduct') }}</span>
        <ChevronDown :size="16" class="shrink-0 text-muted-foreground transition-transform rotate-180" />
      </button>

      <div class="space-y-1">
        <Label v-if="!isMobile" for="product-search" class="text-xs text-muted-foreground">
          {{ t('shopping.list.addProduct') }}
        </Label>
        <div class="relative">
          <Search :size="16" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            id="product-search"
            v-model="searchText"
            :placeholder="t('shopping.list.searchPlaceholder')"
            class="pl-9"
            :disabled="disabled"
            autocomplete="off"
          />
        </div>
        <p v-if="detectedCategory" class="text-xs text-muted-foreground">
          {{ t('shopping.list.detectedCategory', { category: detectedCategory.name }) }}
        </p>
      </div>

      <div v-if="searchResults.length > 0" class="rounded-md border bg-popover p-1 shadow-sm">
        <button
          v-for="suggestion in searchResults"
          :key="`${suggestion.source}-${suggestion.name}`"
          type="button"
          class="flex w-full items-center gap-2 rounded-sm px-2 py-2 text-left text-sm hover:bg-accent"
          :disabled="disabled"
          @click="handleSuggestionSelect(suggestion)"
        >
          <CategoryIcon :icon="categoryIconForSuggestion(suggestion)" :size="16" class="shrink-0" />
          <span class="flex-1">{{ suggestion.name }}</span>
        </button>
      </div>

      <div v-else-if="isFetching && searchText.trim()" class="text-xs text-muted-foreground">
        {{ t('shopping.list.searching') }}
      </div>

      <div v-if="chipSuggestions.length > 0" class="space-y-2">
        <div v-if="recentSuggestions.length > 0" class="space-y-1.5">
          <p class="text-xs font-medium text-muted-foreground">
            {{ t('shopping.list.recentSuggestions') }}
          </p>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="suggestion in recentSuggestions"
              :key="`recent-${suggestion.name}`"
              type="button"
              :class="cn(
                'inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-opacity hover:opacity-80',
                getCategoryColors(categoryIconForSuggestion(suggestion)).chip,
              )"
              :disabled="disabled"
              @click="handleSuggestionSelect(suggestion)"
            >
              <CategoryIcon :icon="categoryIconForSuggestion(suggestion)" :size="12" />
              {{ suggestion.name }}
            </button>
          </div>
        </div>

        <div v-if="popularSuggestions.length > 0" class="space-y-1.5">
          <p class="text-xs font-medium text-muted-foreground">
            {{ t('shopping.list.popularSuggestions') }}
          </p>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="suggestion in popularSuggestions"
              :key="`popular-${suggestion.name}`"
              type="button"
              :class="cn(
                'inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-opacity hover:opacity-80',
                getCategoryColors(categoryIconForSuggestion(suggestion)).chip,
              )"
              :disabled="disabled"
              @click="handleSuggestionSelect(suggestion)"
            >
              <CategoryIcon :icon="categoryIconForSuggestion(suggestion)" :size="12" />
              {{ suggestion.name }}
            </button>
          </div>
        </div>
      </div>

      <div>
        <button
          type="button"
          class="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
          @click="showDetails = !showDetails"
        >
          <ChevronDown :size="14" class="transition-transform" :class="{ 'rotate-180': showDetails }" />
          {{ t('shopping.list.moreOptions') }}
        </button>

        <div v-if="showDetails" class="mt-2 grid gap-2 sm:grid-cols-3">
          <div class="space-y-1">
            <Label for="item-qty" class="text-xs text-muted-foreground">{{ t('shopping.list.quantity') }}</Label>
            <Input
              id="item-qty"
              v-model="detailQuantity"
              :placeholder="t('shopping.list.quantityExample')"
              inputmode="decimal"
              :disabled="disabled"
            />
          </div>
          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">{{ t('shopping.list.unit') }}</Label>
            <Select v-model="detailUnit" :disabled="disabled">
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
          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">{{ t('shopping.list.category') }}</Label>
            <Select :model-value="detailCategory" :disabled="disabled" @update:model-value="onCategoryChange">
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
      </div>

      <Button type="submit" :disabled="!searchText.trim() || disabled">
        <Plus :size="16" />
        {{ t('shopping.list.add') }}
      </Button>
    </form>
  </div>
</template>
