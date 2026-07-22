<script setup lang="ts">
import AppFooter from '@/components/layout/AppFooter.vue'
import DarkModeToggle from '@/shared/components/DarkModeToggle.vue'
import LocaleToggle from '@/shared/i18n/components/LocaleToggle.vue'
</script>

<template>
  <div class="relative flex min-h-screen flex-col bg-background">
    <div
      aria-hidden="true"
      class="ambient-canvas"
    >
      <div class="ambient-blob ambient-blob-peach" />
      <div class="ambient-blob ambient-blob-stone" />
      <div class="ambient-blob ambient-blob-parchment" />
    </div>

    <nav class="fixed top-2 right-2 z-10 flex gap-2 rounded-lg bg-card/60 p-2 backdrop-blur-md">
      <LocaleToggle />
      <DarkModeToggle />
    </nav>

    <main class="ambient-content relative z-1 flex flex-1 flex-col items-center justify-center gap-8 p-4">
      <slot />
    </main>

    <AppFooter class="relative z-1" />
  </div>
</template>
