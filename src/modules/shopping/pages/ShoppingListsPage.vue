<script setup lang="ts">
import { ListChecks, Plus, Settings2, Trash2 } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Sheet,
  SheetContent,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import CategoryManager from '@/modules/shopping/components/CategoryManager.vue'
import { useShoppingLists } from '@/modules/shopping/composables/useShoppingLists'
import { ShoppingRoutePaths } from '@/modules/shopping/routes'
import { useConfirmSheet } from '@/shared/composables/useConfirmSheet'
import { useIsMobile } from '@/shared/composables/useIsMobile'

const { t } = useI18n()
const isMobile = useIsMobile()
const { lists, isLoadingLists, createList, isCreatingList, deleteList } = useShoppingLists()
const { confirm } = useConfirmSheet()

const newListName = ref('')
const showCategories = ref(false)
const createSheetOpen = ref(false)

async function handleCreate() {
  const name = newListName.value.trim()
  if (!name) return
  await createList(name)
  newListName.value = ''
  createSheetOpen.value = false
}

async function handleDelete(listId: string) {
  const confirmed = await confirm({
    title: t('shopping.lists.deleteConfirm'),
    destructive: true,
    confirmLabel: t('common.delete'),
  })
  if (confirmed) {
    await deleteList(listId)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="mx-auto max-w-3xl space-y-6">
      <div class="flex items-end justify-between gap-3">
        <div class="min-w-0 flex-1 space-y-1">
          <h1 class="hidden text-page-title md:block">
            {{ t('shopping.lists.title') }}
          </h1>
          <p class="text-sm text-muted-foreground">
            {{ t('shopping.lists.subtitle') }}
          </p>
        </div>
        <Button
          variant="outline"
          :size="isMobile ? 'icon' : 'default'"
          :aria-label="t('shopping.categories.manage')"
          @click="showCategories = !showCategories"
        >
          <Settings2 :size="16" />
          <span v-if="!isMobile">{{ t('shopping.categories.manage') }}</span>
        </Button>
      </div>

      <Card v-if="showCategories">
        <CardHeader>
          <CardTitle>{{ t('shopping.categories.title') }}</CardTitle>
          <CardDescription>{{ t('shopping.categories.description') }}</CardDescription>
        </CardHeader>
        <CardContent>
          <CategoryManager />
        </CardContent>
      </Card>

      <!-- Desktop: inline create -->
      <form
        v-if="!isMobile"
        class="flex items-center gap-2"
        @submit.prevent="handleCreate"
      >
        <Input
          v-model="newListName"
          :placeholder="t('shopping.lists.namePlaceholder')"
          class="flex-1"
          maxlength="255"
        />
        <Button type="submit" :disabled="!newListName.trim() || isCreatingList">
          <Plus :size="16" />
          {{ t('shopping.lists.create') }}
        </Button>
      </form>

      <!-- Mobile: New list opens sheet -->
      <template v-else>
        <Button
          type="button"
          class="min-h-(--mobile-touch-min) w-full"
          @click="createSheetOpen = true"
        >
          <Plus :size="16" />
          {{ t('shopping.lists.create') }}
        </Button>

        <Sheet v-model:open="createSheetOpen">
          <SheetContent
            side="bottom"
            class="rounded-t-xl pb-[max(1rem,env(safe-area-inset-bottom))]"
          >
            <div class="mx-auto mb-2 h-1 w-10 shrink-0 rounded-full bg-muted-foreground/30" />
            <SheetHeader class="text-left">
              <SheetTitle>{{ t('shopping.lists.createTitle') }}</SheetTitle>
            </SheetHeader>
            <form class="mt-4 space-y-4" @submit.prevent="handleCreate">
              <Input
                v-model="newListName"
                :placeholder="t('shopping.lists.namePlaceholderShort')"
                maxlength="255"
                autofocus
              />
              <SheetFooter class="flex-col gap-2 sm:flex-col">
                <Button
                  type="submit"
                  class="min-h-(--mobile-touch-min) w-full"
                  :disabled="!newListName.trim() || isCreatingList"
                >
                  <Plus :size="16" />
                  {{ t('shopping.lists.create') }}
                </Button>
              </SheetFooter>
            </form>
          </SheetContent>
        </Sheet>
      </template>

      <div v-if="isLoadingLists" class="h-24 w-full animate-pulse rounded bg-muted" />

      <div v-else-if="lists && lists.length > 0" class="grid gap-2 sm:grid-cols-2 sm:gap-3">
        <Card
          v-for="list in lists"
          :key="list.id"
          class="transition-colors hover:border-primary/50"
        >
          <CardContent class="flex items-center justify-between gap-3 p-3 sm:p-4">
            <RouterLink :to="ShoppingRoutePaths.listById(list.id)" class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <ListChecks :size="18" class="shrink-0 text-muted-foreground" />
                <span class="truncate font-medium">{{ list.name }}</span>
              </div>
              <span class="text-xs text-muted-foreground">
                {{ list.checkedCount }}/{{ list.itemCount }} {{ t('shopping.lists.items') }}
              </span>
            </RouterLink>
            <Button size="icon" variant="ghost" @click="handleDelete(list.id)">
              <Trash2 :size="16" class="text-destructive" />
            </Button>
          </CardContent>
        </Card>
      </div>

      <p v-else class="text-sm text-muted-foreground">
        {{ t('shopping.lists.empty') }}
      </p>
    </div>
  </AuthenticatedLayout>
</template>
