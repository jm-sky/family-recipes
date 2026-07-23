<script setup lang="ts">
import { BookOpen, CookingPot, ShoppingCart, Users } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Card, CardContent } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import UpgradePromptBanner from '@/modules/billing/components/UpgradePromptBanner.vue'
import { FamilyRoutePaths } from '@/modules/family/routes'
import { RecipesRoutePaths } from '@/modules/recipes/routes'
import { ShoppingRoutePaths } from '@/modules/shopping/routes'
import { config } from '@/shared/config/config'

const { t } = useI18n()
const { isAuthenticated } = useAuth()

const shortcuts = [
  {
    to: ShoppingRoutePaths.lists,
    titleKey: 'dashboard.shortcuts.shopping',
    descriptionKey: 'dashboard.shortcuts.shoppingDescription',
    icon: ShoppingCart,
  },
  {
    to: FamilyRoutePaths.family,
    titleKey: 'dashboard.shortcuts.family',
    descriptionKey: 'dashboard.shortcuts.familyDescription',
    icon: Users,
  },
  {
    to: RecipesRoutePaths.list,
    titleKey: 'dashboard.shortcuts.recipes',
    descriptionKey: 'dashboard.shortcuts.recipesDescription',
    icon: BookOpen,
  },
] as const
</script>

<template>
  <AuthenticatedLayout>
    <div class="mx-auto max-w-3xl space-y-6">
      <UpgradePromptBanner v-if="isAuthenticated && config.backend.enabled" />

      <div class="space-y-3 text-center md:space-y-4">
        <div class="flex justify-center">
          <div class="rounded-full bg-accent/60 p-3 md:p-6">
            <CookingPot class="size-10 text-accent-foreground md:size-16" />
          </div>
        </div>
        <h1 class="text-page-title md:text-4xl">
          {{ t('dashboard.title', 'Family Recipes') }}
        </h1>
        <p class="mx-auto max-w-2xl text-sm text-muted-foreground md:text-lg">
          {{ t('dashboard.subtitle', 'Shared shopping lists and recipes for your family') }}
        </p>
      </div>

      <div class="grid gap-3 sm:grid-cols-3">
        <RouterLink
          v-for="shortcut in shortcuts"
          :key="shortcut.to"
          :to="shortcut.to"
          class="block"
        >
          <Card class="h-full transition-colors hover:border-primary/50">
            <CardContent class="flex items-start gap-3 p-4">
              <div class="rounded-md bg-primary/10 p-2 text-primary">
                <component :is="shortcut.icon" class="size-5" />
              </div>
              <div class="min-w-0 space-y-0.5">
                <div class="font-medium">
                  {{ t(shortcut.titleKey) }}
                </div>
                <p class="text-xs text-muted-foreground">
                  {{ t(shortcut.descriptionKey) }}
                </p>
              </div>
            </CardContent>
          </Card>
        </RouterLink>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
