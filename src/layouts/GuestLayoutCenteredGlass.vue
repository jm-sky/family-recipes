<script setup lang="ts">
import { useRoute } from 'vue-router'
import GuestLayoutFooter from '@/components/layout/GuestLayoutFooter.vue'
import LogoText from '@/components/ui/LogoText.vue'
import { PublicRouteNames } from '@/router/publicRoutes'
import DarkModeToggle from '@/shared/components/DarkModeToggle.vue'
import LocaleToggle from '@/shared/i18n/components/LocaleToggle.vue'

defineProps<{
  backgroundImage?: string
}>()

const route = useRoute()
const layoutActionsComponent = route.meta.layoutActionsComponent
</script>

<template>
  <div class="relative flex min-h-screen flex-col bg-background">
    <div
      v-if="backgroundImage"
      class="absolute inset-0 bg-cover bg-center transition-opacity duration-500"
      :style="{ backgroundImage: `url(${backgroundImage})` }"
    >
      <div class="absolute inset-0 bg-black/30 transition-colors duration-500 dark:bg-black/50" />
    </div>
    <div
      v-else
      aria-hidden="true"
      class="ambient-canvas"
    >
      <div class="ambient-blob ambient-blob-peach" />
      <div class="ambient-blob ambient-blob-stone" />
      <div class="ambient-blob ambient-blob-parchment" />
    </div>

    <nav class="fixed top-2 right-2 z-10 flex gap-2 rounded-lg bg-card/60 p-2 backdrop-blur-md">
      <slot name="actions">
        <component :is="layoutActionsComponent" v-if="layoutActionsComponent" />
      </slot>
      <LocaleToggle />
      <DarkModeToggle />
    </nav>

    <main class="ambient-content relative z-1 flex flex-1 flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div class="mx-auto mb-8 text-center">
        <RouterLink :to="{ name: PublicRouteNames.landing }" class="block transition-all hover:opacity-80 hover:scale-105">
          <LogoText class="text-3xl" />
        </RouterLink>
      </div>

      <div class="w-full max-w-md rounded-2xl border border-border/60 bg-card/85 p-8 shadow-sm backdrop-blur-lg">
        <slot />
      </div>
    </main>

    <GuestLayoutFooter class="relative z-1" />
  </div>
</template>
