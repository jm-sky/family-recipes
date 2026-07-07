<script setup lang="ts">
import { Users } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Alert from '@/components/ui/alert/Alert.vue'
import AlertDescription from '@/components/ui/alert/AlertDescription.vue'
import AlertTitle from '@/components/ui/alert/AlertTitle.vue'
import { useInvitationPreview } from '@/modules/family/composables/useInvitationPreview'

const props = defineProps<{
  token: string
}>()

const { t } = useI18n()
const { preview, errorKey, isLoading } = useInvitationPreview(() => props.token)
</script>

<template>
  <Alert v-if="isLoading" variant="info">
    <Users />
    <AlertTitle>{{ t('family.invitations.banner.title') }}</AlertTitle>
    <AlertDescription>{{ t('family.invitations.banner.loading') }}</AlertDescription>
  </Alert>

  <Alert v-else-if="preview" variant="info">
    <Users />
    <AlertTitle>{{ t('family.invitations.banner.title') }}</AlertTitle>
    <AlertDescription>
      {{ t('family.invitations.banner.description', { name: preview.familyName }) }}
    </AlertDescription>
  </Alert>

  <Alert v-else-if="errorKey" variant="destructive">
    <Users />
    <AlertTitle>{{ t('family.accept.errorTitle') }}</AlertTitle>
    <AlertDescription>{{ t(errorKey) }}</AlertDescription>
  </Alert>
</template>
