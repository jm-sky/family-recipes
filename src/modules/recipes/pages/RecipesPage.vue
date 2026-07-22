<script setup lang="ts">
import { BookOpen, Plus, Search, Trash2 } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import Select from '@/components/ui/select/Select.vue'
import SelectContent from '@/components/ui/select/SelectContent.vue'
import SelectItem from '@/components/ui/select/SelectItem.vue'
import SelectTrigger from '@/components/ui/select/SelectTrigger.vue'
import SelectValue from '@/components/ui/select/SelectValue.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useRecipes } from '@/modules/recipes/composables/useRecipes'
import { categoryLabelKey, RecipesRouteNames, RecipesRoutePaths } from '@/modules/recipes/routes'
import { RECIPE_CATEGORIES, type RecipeCategory } from '@/modules/recipes/types'

const { t } = useI18n()
const { recipes, isLoading, categoryFilter, searchQuery, deleteRecipe } = useRecipes()

const ALL_CATEGORIES = '__all__'

async function handleDelete(recipeId: string) {
  if (window.confirm(t('recipes.list.deleteConfirm'))) {
    await deleteRecipe(recipeId)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-4xl mx-auto space-y-6">
      <div class="flex items-end justify-between gap-4">
        <div class="space-y-1">
          <h1 class="hidden text-page-title md:block">
            {{ t('recipes.list.title') }}
          </h1>
          <p class="text-sm text-muted-foreground">
            {{ t('recipes.list.subtitle') }}
          </p>
        </div>
        <RouterLink :to="{ name: RecipesRouteNames.new }">
          <Button>
            <Plus :size="16" />
            {{ t('recipes.list.create') }}
          </Button>
        </RouterLink>
      </div>

      <div class="flex flex-col gap-2 sm:flex-row">
        <div class="relative flex-1">
          <Search class="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
          <Input v-model="searchQuery" class="pl-9" :placeholder="t('recipes.list.searchPlaceholder')" />
        </div>
        <Select
          :model-value="categoryFilter || ALL_CATEGORIES"
          @update:model-value="(v) => categoryFilter = (v === ALL_CATEGORIES ? '' : v as RecipeCategory)"
        >
          <SelectTrigger class="sm:w-48">
            <SelectValue :placeholder="t('recipes.list.allCategories')" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem :value="ALL_CATEGORIES">
              {{ t('recipes.list.allCategories') }}
            </SelectItem>
            <SelectItem v-for="cat in RECIPE_CATEGORIES" :key="cat" :value="cat">
              {{ t(categoryLabelKey(cat)) }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div v-if="isLoading" class="h-24 w-full bg-muted rounded animate-pulse" />

      <div v-else-if="recipes && recipes.length > 0" class="grid gap-3 sm:grid-cols-2">
        <Card v-for="recipe in recipes" :key="recipe.id" class="overflow-hidden">
          <CardContent class="p-0">
            <div class="flex gap-3 p-4">
              <div class="size-16 shrink-0 overflow-hidden rounded-md bg-muted">
                <img
                  v-if="recipe.imageUrl"
                  :src="recipe.imageUrl"
                  :alt="recipe.title"
                  class="size-full object-cover"
                />
                <div v-else class="flex size-full items-center justify-center text-muted-foreground">
                  <BookOpen :size="24" />
                </div>
              </div>
              <div class="min-w-0 flex-1 space-y-1">
                <RouterLink :to="RecipesRoutePaths.detailById(recipe.id)" class="block truncate font-medium hover:underline">
                  {{ recipe.title }}
                </RouterLink>
                <p class="text-xs text-muted-foreground">
                  {{ t(categoryLabelKey(recipe.category)) }}
                  <span v-if="recipe.servings"> · {{ t('recipes.list.servings', { n: recipe.servings }) }}</span>
                </p>
              </div>
              <Button size="icon" variant="ghost" @click="handleDelete(recipe.id)">
                <Trash2 :size="16" class="text-destructive" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <p v-else class="text-sm text-muted-foreground">
        {{ t('recipes.list.empty') }}
      </p>
    </div>
  </AuthenticatedLayout>
</template>
