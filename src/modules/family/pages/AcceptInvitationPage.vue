<script setup lang="ts">
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { isAxiosError } from 'axios'
import { CheckCircle2, Users, XCircle } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { familyQueryKeys } from '@/modules/family/composables/useFamily'
import { FamilyRoutePaths } from '@/modules/family/routes'
import { familyService } from '@/modules/family/services/familyService'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()

const token = computed(() => String(route.params.token ?? ''))
const errorKey = ref<string | null>(null)

const { mutateAsync, isPending, isSuccess } = useMutation({
  mutationFn: () => familyService.acceptInvitation(token.value),
  onSuccess: async () => {
    errorKey.value = null
    await queryClient.invalidateQueries({ queryKey: familyQueryKeys.all })
  },
  onError: (error) => {
    errorKey.value = mapErrorKey(error)
  },
})

function mapErrorKey(error: unknown): string {
  if (isAxiosError(error)) {
    switch (error.response?.status) {
      case 403: return 'family.accept.errors.limitReached'
      case 404: return 'family.accept.errors.notFound'
      case 409: {
        const detail = String(error.response?.data?.detail ?? '')
        return detail.toLowerCase().includes('already a member') || detail.toLowerCase().includes('already in')
          ? 'family.accept.errors.alreadyInFamily'
          : 'family.accept.errors.alreadyAccepted'
      }
      case 410: return 'family.accept.errors.expired'
    }
  }
  return 'family.accept.errors.generic'
}

async function accept() {
  try {
    await mutateAsync()
  } catch {
    // handled in onError
  }
}

function goToFamily() {
  router.push(FamilyRoutePaths.family)
}

onMounted(() => {
  if (token.value) accept()
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-md mx-auto mt-12">
      <Card>
        <CardHeader>
          <div class="flex items-center gap-2">
            <Users :size="20" />
            <CardTitle>{{ t('family.accept.title') }}</CardTitle>
          </div>
          <CardDescription>{{ t('family.accept.description') }}</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <!-- In progress -->
          <p v-if="isPending" class="text-sm text-muted-foreground">
            {{ t('family.accept.joining') }}
          </p>

          <!-- Success -->
          <div v-else-if="isSuccess" class="space-y-4">
            <div class="flex items-center gap-2 text-success">
              <CheckCircle2 :size="18" />
              <span class="text-sm font-medium">{{ t('family.accept.success') }}</span>
            </div>
            <Button @click="goToFamily">
              {{ t('family.accept.goToFamily') }}
            </Button>
          </div>

          <!-- Error -->
          <div v-else-if="errorKey" class="space-y-4">
            <div class="flex items-center gap-2 text-destructive">
              <XCircle :size="18" />
              <span class="text-sm font-medium">{{ t('family.accept.errorTitle') }}</span>
            </div>
            <p class="text-sm text-muted-foreground">
              {{ t(errorKey) }}
            </p>
            <Button variant="outline" @click="goToFamily">
              {{ t('family.accept.goToFamily') }}
            </Button>
          </div>

          <!-- Fallback (no token / manual) -->
          <Button v-else :disabled="isPending" @click="accept">
            {{ t('family.accept.accept') }}
          </Button>
        </CardContent>
      </Card>
    </div>
  </AuthenticatedLayout>
</template>
