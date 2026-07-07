<script setup lang="ts">
import MobileShell from '@/components/layout/mobile/MobileShell.vue'
import DesktopAuthenticatedShell from '@/layouts/DesktopAuthenticatedShell.vue'
import { useIsMobile } from '@/shared/composables/useIsMobile'
import type { HTMLAttributes } from 'vue'

defineProps<{
  cardClass?: HTMLAttributes['class']
  mobileContentClass?: HTMLAttributes['class']
}>()

const isMobile = useIsMobile()
</script>

<template>
  <MobileShell v-if="isMobile" :content-class="mobileContentClass">
    <slot />
  </MobileShell>
  <DesktopAuthenticatedShell v-else :card-class="cardClass">
    <slot />
  </DesktopAuthenticatedShell>
</template>
