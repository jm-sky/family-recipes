<script setup lang="ts">
import { ListChecks, Plus, Settings2, Trash2 } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import CategoryManager from '@/modules/shopping/components/CategoryManager.vue'
import { useShoppingLists } from '@/modules/shopping/composables/useShoppingLists'
import { ShoppingRoutePaths } from '@/modules/shopping/routes'
import { useConfirmSheet } from '@/shared/composables/useConfirmSheet'

const { t } = useI18n()
const { lists, isLoadingLists, createList, isCreatingList, deleteList } = useShoppingLists()
const { confirm } = useConfirmSheet()

const newListName = ref('')
const showCategories = ref(false)

async function handleCreate() {
  const name = newListName.value.trim()
  if (!name) return
  await createList(name)
  newListName.value = ''
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
    <div class="max-w-3xl mx-auto space-y-6">
      <div class="flex items-end justify-between gap-4">
        <div class="space-y-1">
          <h1 class="text-3xl font-bold tracking-tight">
            {{ t('shopping.lists.title') }}
          </h1>
          <p class="text-sm text-muted-foreground">
            {{ t('shopping.lists.subtitle') }}
          </p>
        </div>
        <Button variant="outline" @click="showCategories = !showCategories">
          <Settings2 :size="16" />
          {{ t('shopping.categories.manage') }}
        </Button>
      </div>

      <!-- Categories manager -->
      <Card v-if="showCategories">
        <CardHeader>
          <CardTitle>{{ t('shopping.categories.title') }}</CardTitle>
          <CardDescription>{{ t('shopping.categories.description') }}</CardDescription>
        </CardHeader>
        <CardContent>
          <CategoryManager />
        </CardContent>
      </Card>

      <!-- Create list -->
      <form class="flex items-center gap-2" @submit.prevent="handleCreate">
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

      <!-- Lists -->
      <div v-if="isLoadingLists" class="h-24 w-full bg-muted rounded animate-pulse" />

      <div v-else-if="lists && lists.length > 0" class="grid gap-3 sm:grid-cols-2">
        <Card v-for="list in lists" :key="list.id" class="transition-colors hover:border-primary/50">
          <CardContent class="flex items-center justify-between gap-3 p-4">
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
