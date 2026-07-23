<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import GuestLayoutCentered from '@/layouts/GuestLayoutCentered.vue'
import RegisterForm from '@/modules/auth/components/RegisterForm.vue'
import InvitationBanner from '@/modules/family/components/InvitationBanner.vue'
import { parseInvitationTokenFromPath } from '@/modules/family/utils/invitationUrl'

const { t } = useI18n()
const route = useRoute()

const invitationToken = computed(() => {
  const redirectTo = route.query.redirectTo
  if (typeof redirectTo !== 'string') return null
  return parseInvitationTokenFromPath(redirectTo)
})

const loginLink = computed(() => {
  if (typeof route.query.redirectTo === 'string') {
    return {
      path: '/auth/login',
      query: { redirectTo: route.query.redirectTo },
    }
  }
  return '/auth/login'
})
</script>

<template>
  <GuestLayoutCentered>
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="text-center font-display text-3xl font-normal text-foreground">
          {{ t('auth.create_account') }}
        </h2>
        <p class="mt-2 text-center text-sm text-muted-foreground">
          {{ t('auth.links.or_sign_in') }}
          <RouterLink :to="loginLink" class="font-medium text-primary hover:underline">
            {{ t('auth.links.sign_in_existing') }}
          </RouterLink>
        </p>
      </div>

      <InvitationBanner v-if="invitationToken" :token="invitationToken" />

      <div class="bg-card py-8 px-6 shadow-lg rounded-lg">
        <RegisterForm />
      </div>
    </div>
  </GuestLayoutCentered>
</template>
