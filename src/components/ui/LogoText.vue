<script setup lang="ts">
import { CookingPot } from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import { config } from '@/shared/config/config'
import type { PrimitiveProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'

const props = withDefaults(defineProps<{
  as?: PrimitiveProps['as']
  class?: HTMLAttributes['class']
}>(), {
  as: 'span',
})
</script>

<template>
  <component :is="props.as" :class="cn('inline-flex items-center gap-1.5 whitespace-nowrap font-display text-2xl font-normal text-foreground', props.class)">
    <CookingPot class="size-[1em] shrink-0 text-accent-foreground" aria-hidden="true" />
    <span>{{ config.app.name }}</span>
  </component>
</template>
