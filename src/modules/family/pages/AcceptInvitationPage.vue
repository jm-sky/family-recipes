<script setup lang="ts">
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { CheckCircle2, Users, XCircle } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { familyQueryKeys } from '@/modules/family/composables/useFamily'
import { useInvitationPreview } from '@/modules/family/composables/useInvitationPreview'
import { FamilyRoutePaths } from '@/modules/family/routes'
import { familyService } from '@/modules/family/services/familyService'
import { mapInvitationErrorKey } from '@/modules/family/utils/invitationErrors'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()

const token = computed(() => String(route.params.token ?? ''))
const acceptErrorKey = ref<string | null>(null)

const { preview, errorKey: previewErrorKey, isLoading: isLoadingPreview } = useInvitationPreview(token)

const { mutateAsync, isPending, isSuccess } = useMutation({
  mutationFn: () => familyService.acceptInvitation(token.value),
  onSuccess: async () => {
    acceptErrorKey.value = null
    await queryClient.invalidateQueries({ queryKey: familyQueryKeys.all })
  },
  onError: (error) => {
    acceptErrorKey.value = mapInvitationErrorKey(error)
  },
})

const displayErrorKey = computed(() => acceptErrorKey.value ?? previewErrorKey.value)

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

function decline() {
  router.push(AuthRoutePaths.dashboard)
}
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
          <CardDescription v-if="isLoadingPreview">
            {{ t('family.invitations.banner.loading') }}
          </CardDescription>
          <CardDescription v-else-if="preview">
            {{ t('family.accept.descriptionWithName', { name: preview.familyName }) }}
          </CardDescription>
          <CardDescription v-else>
            {{ t('family.accept.description') }}
          </CardDescription>
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
          <div v-else-if="displayErrorKey" class="space-y-4">
            <div class="flex items-center gap-2 text-destructive">
              <XCircle :size="18" />
              <span class="text-sm font-medium">{{ t('family.accept.errorTitle') }}</span>
            </div>
            <p class="text-sm text-muted-foreground">
              {{ t(displayErrorKey) }}
            </p>
            <Button variant="outline" @click="decline">
              {{ t('family.accept.decline') }}
            </Button>
          </div>

          <!-- Confirmation -->
          <div v-else-if="preview" class="flex flex-col gap-2 sm:flex-row">
            <Button :disabled="isPending" @click="accept">
              {{ t('family.accept.accept') }}
            </Button>
            <Button variant="outline" :disabled="isPending" @click="decline">
              {{ t('family.accept.decline') }}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  </AuthenticatedLayout>
</template>
