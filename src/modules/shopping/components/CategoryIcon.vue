<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'
import { getCategoryColors } from '@/modules/shopping/utils/categoryColors'
import { getCategoryIcon } from '@/modules/shopping/utils/categoryIcons'

const props = withDefaults(defineProps<{
  icon: string | null | undefined
  size?: number
  class?: string
}>(), {
  size: 16,
})

const Icon = computed(() => getCategoryIcon(props.icon))
const colorClass = computed(() => getCategoryColors(props.icon).icon)
</script>

<template>
  <component :is="Icon" :size="size" :class="cn(colorClass, props.class)" />
</template>
