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
    class="fixed inset-x-0 bottom-0 z-50 border-t bg-background/95 backdrop-blur-sm pb-[env(safe-area-inset-bottom)]"
    :aria-label="t('navigation.main', 'Navigation')"
  >
    <div class="grid h-(--bottom-nav-height) grid-cols-4 items-center">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.to"
        v-slot="{ navigate, href }"
        :to="tab.to"
        custom
      >
        <a
          :href="href"
          class="flex flex-col items-center justify-center gap-0.5 px-1 py-1 text-[0.6875rem] leading-none font-medium transition-colors"
          :class="cn(
            isMobileBottomNavActive(route.path, tab.matchPrefix)
              ? 'text-primary'
              : 'text-muted-foreground',
          )"
          @click="navigate"
        >
          <component
            :is="tab.icon"
            class="size-5"
            :class="isMobileBottomNavActive(route.path, tab.matchPrefix) ? 'text-primary' : 'text-muted-foreground'"
          />
          <span class="truncate max-w-full">{{ tab.label }}</span>
        </a>
      </RouterLink>
    </div>
  </nav>
</template>
