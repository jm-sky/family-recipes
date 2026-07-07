<script setup lang="ts">
import BottomNav from '@/components/layout/mobile/BottomNav.vue'
import TopAppBar from '@/components/layout/mobile/TopAppBar.vue'
import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'vue'

defineProps<{
  contentClass?: HTMLAttributes['class']
}>()
</script>

<template>
  <div class="flex min-h-svh flex-col bg-background">
    <TopAppBar>
      <template v-if="$slots.actions" #actions>
        <slot name="actions" />
      </template>
    </TopAppBar>

    <main
      :class="cn(
        'flex-1 overflow-x-hidden px-3 py-4',
        'pb-[calc(var(--bottom-nav-height)+env(safe-area-inset-bottom)+1rem)]',
        contentClass,
      )"
    >
      <slot />
    </main>

    <BottomNav />
  </div>
</template>
