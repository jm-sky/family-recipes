<script setup lang="ts">
import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'vue'

const props = defineProps<{
  title?: string
  description?: string
  withHeader?: boolean
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div :class="cn('max-w-md w-full space-y-8', props.class)">
    <div class="space-y-4 rounded-2xl border border-border/60 bg-card/85 px-6 py-8 shadow-sm backdrop-blur-lg">
      <slot v-if="withHeader || $slots['header-description']" name="header">
        <h2 v-if="title" class="text-center font-display text-2xl font-normal text-card-foreground">
          {{ title }}
        </h2>
        <slot name="header-description">
          <p v-if="description" class="mt-2 text-center text-sm text-muted-foreground">
            {{ description }}
          </p>
        </slot>
      </slot>
      <slot />
    </div>

    <div v-if="$slots.footer" class="text-center">
      <slot name="footer" />
    </div>

    <slot name="after" />
  </div>
</template>
