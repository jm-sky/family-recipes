<script setup lang="ts">
import { Rocket } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import GuestLayoutFooter from '@/components/layout/GuestLayoutFooter.vue'
import LogoText from '@/components/ui/LogoText.vue'
import { PublicRouteNames } from '@/router/publicRoutes'
import DarkModeToggle from '@/shared/components/DarkModeToggle.vue'
import LocaleToggle from '@/shared/i18n/components/LocaleToggle.vue'

defineProps<{
  brandingTitle?: string
  brandingTagline?: string
  brandingMessage?: string
  backgroundImage?: string
}>()

const route = useRoute()
const layoutActionsComponent = route.meta.layoutActionsComponent
</script>

<template>
  <div class="relative grid min-h-screen bg-background lg:grid-cols-2">
    <div
      aria-hidden="true"
      class="ambient-canvas"
    >
      <div class="ambient-blob ambient-blob-peach" />
      <div class="ambient-blob ambient-blob-stone" />
    </div>

    <!-- Left Column - Branding Panel (hidden on mobile) -->
    <div class="relative hidden overflow-hidden bg-accent/35 lg:flex dark:bg-accent/20">
      <div
        v-if="backgroundImage"
        class="absolute inset-0 bg-cover bg-center opacity-20"
        :style="{ backgroundImage: `url(${backgroundImage})` }"
      />

      <div class="relative z-10 flex w-full flex-col items-center justify-center p-12 text-accent-foreground">
        <div class="max-w-md space-y-6 text-center">
          <div class="mb-8">
            <LogoText class="text-4xl" />
          </div>

          <h1 class="font-display text-3xl font-normal">
            {{ brandingTitle ?? 'Welcome to Vue Blocks Registry' }}
          </h1>
          <p class="text-lg opacity-90">
            {{ brandingTagline ?? 'Build faster with reusable Vue components' }}
          </p>

          <div class="flex flex-col items-center justify-center gap-3 pt-6">
            <Rocket class="size-8" />
            <p class="text-base">
              {{ brandingMessage ?? 'Get started in minutes with our powerful component library' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Column - Content Area -->
    <div class="relative flex min-h-screen flex-col bg-background/80 backdrop-blur-sm">
      <div class="fixed top-4 right-4 z-10 flex items-center gap-2">
        <slot name="actions">
          <component :is="layoutActionsComponent" v-if="layoutActionsComponent" />
        </slot>
        <LocaleToggle />
        <DarkModeToggle />
      </div>

      <main class="ambient-content relative z-1 flex flex-1 flex-col items-center justify-center p-8 sm:p-12">
        <div class="mb-8 lg:hidden">
          <RouterLink :to="{ name: PublicRouteNames.landing }" class="block transition-all hover:opacity-80 hover:scale-105">
            <LogoText class="text-2xl" />
          </RouterLink>
        </div>

        <div class="w-full max-w-md">
          <slot />
        </div>
      </main>

      <GuestLayoutFooter />
    </div>
  </div>
</template>
