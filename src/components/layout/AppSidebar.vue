<script setup lang="ts">
import { BookOpen, Info, LayoutDashboard, ShoppingCart, Users } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar'
import { PublicRoutePaths } from '@/router/publicRoutes'

const { t } = useI18n()

// Main navigation links (shopping lists and recipes modules plug in here)
const mainLinks = computed(() => [
  {
    to: '/dashboard',
    label: t('navigation.dashboard', 'Dashboard'),
    icon: LayoutDashboard,
  },
  {
    to: '/family',
    label: t('family.nav.title', 'Family'),
    icon: Users,
  },
  {
    to: '/recipes',
    label: t('recipes.nav.title', 'Recipes'),
    icon: BookOpen,
  },
  {
    to: '/shopping',
    label: t('shopping.nav.title', 'Shopping'),
    icon: ShoppingCart,
  },
])
</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarContent class="overflow-x-hidden max-h-[90vh] overflow-y-auto">
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('navigation.menu', 'Menu') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in mainLinks" :key="link.to">
              <RouterLink v-slot="{ href, navigate, isActive }" :to="link.to" custom>
                <SidebarMenuButton
                  :is-active="isActive"
                  as="a"
                  :href="href"
                  @click="navigate"
                >
                  <component :is="link.icon" />
                  <span>{{ link.label }}</span>
                </SidebarMenuButton>
              </RouterLink>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <RouterLink v-slot="{ href, navigate, isActive }" :to="PublicRoutePaths.about" custom>
            <SidebarMenuButton
              :is-active="isActive"
              as="a"
              :href="href"
              @click="navigate"
            >
              <Info class="size-4" />
              <span>{{ t('common.pages.about', 'About') }}</span>
            </SidebarMenuButton>
          </RouterLink>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>

    <SidebarRail />
  </Sidebar>
</template>
