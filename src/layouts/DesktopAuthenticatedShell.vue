<script setup lang="ts">
import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar'
import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'vue'

defineProps<{
  cardClass?: HTMLAttributes['class']
}>()
</script>

<template>
  <SidebarProvider>
    <AppSidebar class="mt-(--header-height)" />
    <SidebarInset class="relative bg-background pt-14">
      <div
        aria-hidden="true"
        class="ambient-canvas"
      >
        <div class="ambient-blob ambient-blob-peach" />
        <div class="ambient-blob ambient-blob-stone" />
        <div class="ambient-blob ambient-blob-parchment" />
      </div>

      <div class="ambient-content flex min-h-screen w-full max-w-full flex-col overflow-x-hidden">
        <AppHeader />

        <main class="mx-auto w-full max-w-7xl flex-1 px-2 py-6 sm:px-6 lg:px-8">
          <div :class="cn('w-full max-w-full rounded-2xl border border-border bg-card p-4 shadow-sm sm:p-6', cardClass)">
            <slot />
          </div>
        </main>

        <AppFooter />
      </div>
    </SidebarInset>
  </SidebarProvider>
</template>
