<script setup lang="ts">
import { Check, Pencil, Plus, Trash2, X } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useShoppingLists } from '@/modules/shopping/composables/useShoppingLists'
import type { Category } from '@/modules/shopping/types'

const { t } = useI18n()
const { categories, createCategory, updateCategory, deleteCategory } = useShoppingLists()

const newCategoryName = ref('')
const editingId = ref<string | null>(null)
const editingName = ref('')

async function handleCreate() {
  const name = newCategoryName.value.trim()
  if (!name) return
  await createCategory({ name })
  newCategoryName.value = ''
}

function startEdit(category: Category) {
  editingId.value = category.id
  editingName.value = category.name
}

function cancelEdit() {
  editingId.value = null
  editingName.value = ''
}

async function saveEdit(category: Category) {
  const name = editingName.value.trim()
  if (name && name !== category.name) {
    await updateCategory({ id: category.id, request: { name } })
  }
  cancelEdit()
}
</script>

<template>
  <div class="space-y-3">
    <div v-if="categories && categories.length > 0" class="space-y-2">
      <div
        v-for="category in categories"
        :key="category.id"
        class="flex items-center gap-2 rounded-md border p-2"
      >
        <template v-if="editingId === category.id">
          <Input v-model="editingName" class="h-8 flex-1" @keyup.enter="saveEdit(category)" />
          <Button size="icon" variant="ghost" @click="saveEdit(category)">
            <Check :size="16" />
          </Button>
          <Button size="icon" variant="ghost" @click="cancelEdit">
            <X :size="16" />
          </Button>
        </template>
        <template v-else>
          <span class="flex-1 text-sm">{{ category.name }}</span>
          <Button size="icon" variant="ghost" @click="startEdit(category)">
            <Pencil :size="15" />
          </Button>
          <Button size="icon" variant="ghost" @click="deleteCategory(category.id)">
            <Trash2 :size="15" class="text-destructive" />
          </Button>
        </template>
      </div>
    </div>
    <p v-else class="text-sm text-muted-foreground">
      {{ t('shopping.categories.empty') }}
    </p>

    <form class="flex items-center gap-2" @submit.prevent="handleCreate">
      <Input v-model="newCategoryName" :placeholder="t('shopping.categories.namePlaceholder')" class="h-9" />
      <Button type="submit" size="sm" :disabled="!newCategoryName.trim()">
        <Plus :size="16" />
        {{ t('shopping.categories.add') }}
      </Button>
    </form>
  </div>
</template>
