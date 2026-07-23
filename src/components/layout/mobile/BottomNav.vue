<script setup lang="ts">
import { BookOpen, LayoutDashboard, ShoppingCart, Users } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import { cn } from '@/lib/utils'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { FamilyRoutePaths } from '@/modules/family/routes'
import { RecipesRoutePaths } from '@/modules/recipes/routes'
import { ShoppingRoutePaths } from '@/modules/shopping/routes'
import { isMobileBottomNavActive } from '@/shared/config/mobileNav'

const { t } = useI18n()
const route = useRoute()

const tabs = computed(() => [
  {
    to: AuthRoutePaths.dashboard,
    matchPrefix: AuthRoutePaths.dashboard,
    label: t('navigation.dashboard', 'Dashboard'),
    icon: LayoutDashboard,
  },
  {
    to: FamilyRoutePaths.family,
    matchPrefix: FamilyRoutePaths.family,
    label: t('family.nav.title', 'Family'),
    icon: Users,
  },
  {
    to: RecipesRoutePaths.list,
    matchPrefix: RecipesRoutePaths.list,
    label: t('recipes.nav.title', 'Recipes'),
    icon: BookOpen,
  },
  {
    to: ShoppingRoutePaths.lists,
    matchPrefix: ShoppingRoutePaths.lists,
    label: t('shopping.nav.title', 'Shopping'),
    icon: ShoppingCart,
  },
])
</script>

<template>
  <nav
    class="fixed inset-x-0 bottom-0 z-50 border-t bg-background/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-sm"
    :aria-label="t('navigation.main', 'Navigation')"
  >
    <div class="flex h-[var(--bottom-nav-height)] items-center justify-around px-0.5">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.to"
        v-slot="{ navigate, href }"
        :to="tab.to"
        custom
      >
        <a
          :href="href"
          class="flex min-h-[var(--mobile-touch-min)] min-w-0 flex-1 flex-col items-center justify-center gap-1 px-0.5 text-xs leading-none transition-colors"
          :class="cn(
            isMobileBottomNavActive(route.path, tab.matchPrefix)
              ? 'font-semibold text-primary'
              : 'font-medium text-muted-foreground',
          )"
          @click="navigate"
        >
          <span
            class="flex size-9 items-center justify-center rounded-full transition-colors"
            :class="isMobileBottomNavActive(route.path, tab.matchPrefix) ? 'bg-primary/15' : ''"
          >
            <component
              :is="tab.icon"
              class="size-6 shrink-0"
              :stroke-width="isMobileBottomNavActive(route.path, tab.matchPrefix) ? 2.25 : 1.75"
              :class="isMobileBottomNavActive(route.path, tab.matchPrefix) ? 'text-primary' : 'text-muted-foreground'"
            />
          </span>
          <span class="max-w-full truncate">{{ tab.label }}</span>
        </a>
      </RouterLink>
    </div>
  </nav>
</template>
