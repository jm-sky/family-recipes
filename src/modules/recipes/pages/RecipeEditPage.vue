<script setup lang="ts">
import { ArrowLeft, Link2, Plus, Trash2, Upload } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Select from '@/components/ui/select/Select.vue'
import SelectContent from '@/components/ui/select/SelectContent.vue'
import SelectItem from '@/components/ui/select/SelectItem.vue'
import SelectTrigger from '@/components/ui/select/SelectTrigger.vue'
import SelectValue from '@/components/ui/select/SelectValue.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import AiPremiumFeatureAlert from '@/modules/ai/components/AiPremiumFeatureAlert.vue'
import { useAi } from '@/modules/ai/composables/useAi'
import { useRecipe } from '@/modules/recipes/composables/useRecipe'
import { useRecipeImport } from '@/modules/recipes/composables/useRecipeImport'
import { useRecipes } from '@/modules/recipes/composables/useRecipes'
import { categoryLabelKey, RecipesRoutePaths } from '@/modules/recipes/routes'
import { RECIPE_CATEGORIES, type RecipeCategory } from '@/modules/recipes/types'
import { UNITS } from '@/modules/shopping/types'
import { config } from '@/shared/config/config'

const { t } = useI18n()
const route = useRoute()
const { canUseAi } = useAi()
const aiImportEnabled = computed(() => config.features.ai.enabled)

const recipeIdParam = computed(() => {
  const id = route.params.recipeId
  return typeof id === 'string' && id !== 'new' ? id : null
})

const { recipe, isLoading, isNew, createRecipe, updateRecipe, isSaving, uploadImage } = useRecipe(recipeIdParam)
const { tags } = useRecipes()
const { importFromUrl, isImporting } = useRecipeImport()

const importUrl = ref('')

const title = ref('')
const sourceUrl = ref('')
const category = ref<RecipeCategory>('dinner')
const servings = ref('')
const ingredients = ref<{ name: string, quantity: string, unit: string }[]>([{ name: '', quantity: '', unit: '' }])
const selectedTagIds = ref<string[]>([])
const NO_UNIT = '__none__'

watch(recipe, (value) => {
  if (!value) return
  title.value = value.title
  sourceUrl.value = value.sourceUrl ?? ''
  category.value = value.category
  servings.value = value.servings ? String(value.servings) : ''
  ingredients.value = value.ingredients.map(i => ({
    name: i.name,
    quantity: i.quantity !== null ? String(i.quantity) : '',
    unit: i.unit ?? NO_UNIT,
  }))
  selectedTagIds.value = [...value.tagIds]
}, { immediate: true })

function addIngredientRow() {
  ingredients.value.push({ name: '', quantity: '', unit: NO_UNIT })
}

function removeIngredientRow(index: number) {
  if (ingredients.value.length > 1) {
    ingredients.value.splice(index, 1)
  }
}

function toggleTag(tagId: string) {
  if (selectedTagIds.value.includes(tagId)) {
    selectedTagIds.value = selectedTagIds.value.filter(id => id !== tagId)
  }
  else {
    selectedTagIds.value = [...selectedTagIds.value, tagId]
  }
}

function buildPayload() {
  const parsedIngredients = ingredients.value
    .filter(row => row.name.trim())
    .map(row => ({
      name: row.name.trim(),
      quantity: row.quantity ? Number(row.quantity.replace(',', '.')) : null,
      unit: row.unit && row.unit !== NO_UNIT ? row.unit : null,
    }))
  return {
    title: title.value.trim(),
    sourceUrl: sourceUrl.value.trim() || null,
    category: category.value,
    servings: servings.value ? Number(servings.value) : null,
    ingredients: parsedIngredients,
    tagIds: selectedTagIds.value,
  }
}

async function handleSubmit() {
  const payload = buildPayload()
  if (!payload.title || payload.ingredients.length === 0) return
  if (isNew.value) {
    await createRecipe(payload)
  }
  else {
    await updateRecipe(payload)
  }
}

async function handleImageChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || isNew.value) return
  await uploadImage(file)
  input.value = ''
}

async function handleImport() {
  const url = importUrl.value.trim()
  if (!url) return
  const draft = await importFromUrl(url)
  title.value = draft.title
  sourceUrl.value = draft.sourceUrl
  category.value = draft.category
  servings.value = draft.servings ? String(draft.servings) : ''
  ingredients.value = draft.ingredients.map(i => ({
    name: i.name,
    quantity: i.quantity !== null ? String(i.quantity) : '',
    unit: i.unit ?? NO_UNIT,
  }))
  if (ingredients.value.length === 0) {
    ingredients.value = [{ name: '', quantity: '', unit: NO_UNIT }]
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-2xl mx-auto space-y-5">
      <RouterLink
        :to="isNew ? RecipesRoutePaths.list : RecipesRoutePaths.detailById(recipeIdParam!)"
        class="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft :size="16" />
        {{ t('recipes.edit.back') }}
      </RouterLink>

      <h1 class="text-2xl font-bold tracking-tight">
        {{ t(isNew ? 'recipes.edit.newTitle' : 'recipes.edit.title') }}
      </h1>

      <div v-if="!isNew && isLoading" class="h-24 w-full bg-muted rounded animate-pulse" />

      <form v-else class="space-y-5" @submit.prevent="handleSubmit">
        <Card v-if="isNew && aiImportEnabled">
          <CardHeader>
            <CardTitle class="text-base flex items-center gap-2">
              <Link2 :size="18" />
              {{ t('recipes.import.title') }}
            </CardTitle>
            <CardDescription>
              {{ t('recipes.import.description') }}
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-3">
            <AiPremiumFeatureAlert
              v-if="!canUseAi"
              :description="t('recipes.import.premiumRequired')"
              show-token-option
            />
            <template v-else>
              <div class="space-y-2">
                <Label for="import-url">{{ t('recipes.import.urlLabel') }}</Label>
                <Input
                  id="import-url"
                  v-model="importUrl"
                  type="url"
                  :placeholder="t('recipes.import.urlPlaceholder')"
                />
              </div>
              <Button
                type="button"
                variant="secondary"
                :disabled="isImporting || !importUrl.trim()"
                @click="handleImport"
              >
                {{ isImporting ? t('recipes.import.importing') : t('recipes.import.button') }}
              </Button>
            </template>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="grid gap-4 p-4">
            <div class="space-y-2">
              <Label for="title">{{ t('recipes.edit.titleLabel') }}</Label>
              <Input
                id="title"
                v-model="title"
                :placeholder="t('recipes.edit.titlePlaceholder')"
                required
              />
            </div>
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="space-y-2">
                <Label>{{ t('recipes.edit.categoryLabel') }}</Label>
                <Select v-model="category">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="cat in RECIPE_CATEGORIES" :key="cat" :value="cat">
                      {{ t(categoryLabelKey(cat)) }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-2">
                <Label for="servings">{{ t('recipes.edit.servingsLabel') }}</Label>
                <Input id="servings" v-model="servings" inputmode="numeric" />
              </div>
            </div>
            <div class="space-y-2">
              <Label for="source">{{ t('recipes.edit.sourceUrlLabel') }}</Label>
              <Input
                id="source"
                v-model="sourceUrl"
                type="url"
                :placeholder="t('recipes.edit.sourceUrlPlaceholder')"
              />
            </div>
          </CardContent>
        </Card>

        <Card v-if="!isNew">
          <CardHeader>
            <CardTitle class="text-base">
              {{ t('recipes.edit.imageLabel') }}
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <img
              v-if="recipe?.imageUrl"
              :src="recipe.imageUrl"
              :alt="recipe.title"
              class="max-h-48 rounded-md object-cover"
            />
            <label class="inline-flex cursor-pointer items-center gap-2 text-sm">
              <Upload :size="16" />
              {{ t('recipes.edit.uploadImage') }}
              <input
                type="file"
                accept="image/*"
                class="sr-only"
                @change="handleImageChange"
              />
            </label>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="flex flex-row items-center justify-between">
            <CardTitle class="text-base">
              {{ t('recipes.edit.ingredientsLabel') }}
            </CardTitle>
            <Button
              type="button"
              size="sm"
              variant="outline"
              @click="addIngredientRow"
            >
              <Plus :size="14" />
              {{ t('recipes.edit.addIngredient') }}
            </Button>
          </CardHeader>
          <CardContent class="space-y-2">
            <div
              v-for="(row, index) in ingredients"
              :key="index"
              class="grid gap-2 sm:grid-cols-[1fr_5rem_8rem_auto]"
            >
              <Input v-model="row.name" :placeholder="t('recipes.edit.ingredientName')" required />
              <Input v-model="row.quantity" :placeholder="t('recipes.edit.ingredientQty')" inputmode="decimal" />
              <Select v-model="row.unit">
                <SelectTrigger>
                  <SelectValue :placeholder="t('recipes.edit.ingredientUnit')" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem :value="NO_UNIT">
                    —
                  </SelectItem>
                  <SelectItem v-for="unit in UNITS" :key="unit" :value="unit">
                    {{ unit }}
                  </SelectItem>
                </SelectContent>
              </Select>
              <Button
                type="button"
                size="icon"
                variant="ghost"
                :disabled="ingredients.length <= 1"
                @click="removeIngredientRow(index)"
              >
                <Trash2 :size="14" class="text-destructive" />
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card v-if="tags && tags.length > 0">
          <CardHeader>
            <CardTitle class="text-base">
              {{ t('recipes.edit.tagsLabel') }}
            </CardTitle>
          </CardHeader>
          <CardContent class="flex flex-wrap gap-2">
            <Button
              v-for="tag in tags"
              :key="tag.id"
              type="button"
              size="sm"
              :variant="selectedTagIds.includes(tag.id) ? 'default' : 'outline'"
              @click="toggleTag(tag.id)"
            >
              {{ tag.name }}
            </Button>
          </CardContent>
        </Card>

        <Button type="submit" :disabled="isSaving || !title.trim()">
          {{ isSaving ? t('recipes.edit.saving') : t('recipes.edit.save') }}
        </Button>
      </form>
    </div>
  </AuthenticatedLayout>
</template>
