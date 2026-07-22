<script setup lang="ts">
import { type RouteLocationRaw, RouterLink } from 'vue-router'
import { cn } from '@/lib/utils'

defineProps<{
  to: RouteLocationRaw
  ariaLabel?: string
  activeClass?: string
  exactActiveClass?: string
}>()
</script>

<template>
  <RouterLink
    :to
    :aria-label="ariaLabel"
    class="relative text-foreground/80 transition-colors before:absolute before:-bottom-0.5 before:h-0.5 before:w-0 before:rounded-md before:bg-foreground before:transition-all before:duration-300 before:ease-in-out hover:text-foreground hover:before:w-full"
    :active-class="cn('before:w-full text-foreground', activeClass)"
    :exact-active-class="cn('before:w-full text-foreground', exactActiveClass)"
  >
    <slot />
  </RouterLink>
</template>
