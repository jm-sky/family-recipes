<script setup lang="ts">
import { ArrowLeft, ExternalLink, Pencil, ShoppingCart } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Select from '@/components/ui/select/Select.vue'
import SelectContent from '@/components/ui/select/SelectContent.vue'
import SelectItem from '@/components/ui/select/SelectItem.vue'
import SelectTrigger from '@/components/ui/select/SelectTrigger.vue'
import SelectValue from '@/components/ui/select/SelectValue.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useRecipe } from '@/modules/recipes/composables/useRecipe'
import { categoryLabelKey, RecipesRoutePaths } from '@/modules/recipes/routes'
import { useShoppingLists } from '@/modules/shopping/composables/useShoppingLists'
import { formatItemQuantity } from '@/modules/shopping/utils/formatQuantity'

const { t, locale } = useI18n()
const route = useRoute()

const recipeId = computed(() => String(route.params.recipeId ?? ''))
const { recipe, isLoading, addToList, isAddingToList } = useRecipe(recipeId)
const { lists } = useShoppingLists()

const selectedListId = ref('')

async function handleAddToList(mode: 'all' | 'missing') {
  if (!selectedListId.value) return
  await addToList({ listId: selectedListId.value, mode })
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-2xl mx-auto space-y-5">
      <RouterLink :to="RecipesRoutePaths.list" class="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft :size="16" />
        {{ t('recipes.detail.back') }}
      </RouterLink>

      <div v-if="isLoading" class="h-32 w-full bg-muted rounded animate-pulse" />

      <template v-else-if="recipe">
        <div v-if="recipe.imageUrl" class="overflow-hidden rounded-lg">
          <img :src="recipe.imageUrl" :alt="recipe.title" class="w-full max-h-64 object-cover" />
        </div>

        <div class="flex items-start justify-between gap-4">
          <div class="space-y-1">
            <h1 class="text-2xl font-bold tracking-tight">
              {{ recipe.title }}
            </h1>
            <p class="text-sm text-muted-foreground">
              {{ t(categoryLabelKey(recipe.category)) }}
              <span v-if="recipe.servings"> · {{ t('recipes.list.servings', { n: recipe.servings }) }}</span>
            </p>
            <a
              v-if="recipe.sourceUrl"
              :href="recipe.sourceUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-1 text-sm text-primary hover:underline"
            >
              <ExternalLink :size="14" />
              {{ t('recipes.detail.sourceLink') }}
            </a>
          </div>
          <RouterLink :to="RecipesRoutePaths.editById(recipe.id)">
            <Button variant="outline" size="sm">
              <Pencil :size="14" />
              {{ t('recipes.detail.edit') }}
            </Button>
          </RouterLink>
        </div>

        <Card>
          <CardHeader>
            <CardTitle class="text-base">
              {{ t('recipes.detail.ingredients') }}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul class="space-y-1.5">
              <li v-for="ingredient in recipe.ingredients" :key="ingredient.id" class="flex justify-between text-sm">
                <span>{{ ingredient.name }}</span>
                <span class="tabular-nums text-muted-foreground">
                  {{ formatItemQuantity(ingredient.quantity, ingredient.unit, locale) }}
                </span>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
            <Select v-model="selectedListId">
              <SelectTrigger class="flex-1">
                <SelectValue :placeholder="t('recipes.detail.selectList')" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="list in lists ?? []" :key="list.id" :value="list.id">
                  {{ list.name }}
                </SelectItem>
              </SelectContent>
            </Select>
            <Button
              :disabled="!selectedListId || isAddingToList || !(lists?.length)"
              @click="handleAddToList('all')"
            >
              <ShoppingCart :size="16" />
              {{ t('recipes.detail.addToList') }}
            </Button>
            <Button
              variant="secondary"
              :disabled="!selectedListId || isAddingToList || !(lists?.length)"
              @click="handleAddToList('missing')"
            >
              {{ t('recipes.detail.addMissing') }}
            </Button>
          </CardContent>
          <p v-if="lists && lists.length === 0" class="px-4 pb-4 text-xs text-muted-foreground">
            {{ t('recipes.detail.noLists') }}
          </p>
        </Card>
      </template>
    </div>
  </AuthenticatedLayout>
</template>
