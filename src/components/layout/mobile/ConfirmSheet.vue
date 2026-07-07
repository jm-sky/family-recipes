<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetDescription, SheetFooter, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { confirmSheetState, resolveConfirmSheet } from '@/shared/composables/useConfirmSheet'

const { t } = useI18n()

const open = computed({
  get: () => confirmSheetState.open,
  set: (value: boolean) => {
    if (!value) resolveConfirmSheet(false)
  },
})

const options = computed(() => confirmSheetState.options)

function handleConfirm() {
  resolveConfirmSheet(true)
}
</script>

<template>
  <Sheet v-model:open="open">
    <SheetContent
      side="bottom"
      class="rounded-t-xl pb-[max(1rem,env(safe-area-inset-bottom))] [&>button]:hidden"
    >
      <div class="mx-auto mb-3 h-1 w-10 shrink-0 rounded-full bg-muted-foreground/30" />

      <SheetHeader v-if="options" class="text-left">
        <SheetTitle>{{ options.title }}</SheetTitle>
        <SheetDescription v-if="options.description">
          {{ options.description }}
        </SheetDescription>
      </SheetHeader>

      <SheetFooter v-if="options" class="mt-4 flex-col gap-2 sm:flex-col">
        <Button
          class="min-h-(--mobile-touch-min) w-full"
          :variant="options.destructive ? 'destructive' : 'default'"
          @click="handleConfirm"
        >
          {{ options.confirmLabel ?? t('common.confirm', 'Confirm') }}
        </Button>
        <Button
          variant="outline"
          class="min-h-(--mobile-touch-min) w-full"
          @click="resolveConfirmSheet(false)"
        >
          {{ options.cancelLabel ?? t('common.cancel', 'Cancel') }}
        </Button>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>
