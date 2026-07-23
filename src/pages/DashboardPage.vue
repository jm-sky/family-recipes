<script setup lang="ts">
import { CookingPot } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import UpgradePromptBanner from '@/modules/billing/components/UpgradePromptBanner.vue'
import { config } from '@/shared/config/config'

const { t } = useI18n()
const { isAuthenticated } = useAuth()
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-8">
      <!-- Upgrade Prompt Banner (only for authenticated FREE users) -->
      <UpgradePromptBanner v-if="isAuthenticated && config.backend.enabled" />

      <!-- Header -->
      <div class="text-center space-y-4">
        <div class="flex justify-center">
          <div class="rounded-full bg-accent/60 p-6">
            <CookingPot class="size-16 text-accent-foreground" />
          </div>
        </div>
        <h1 class="text-page-title md:text-4xl">
          {{ t('dashboard.title', 'Family Recipes') }}
        </h1>
        <p class="text-muted-foreground text-lg max-w-2xl mx-auto">
          {{ t('dashboard.subtitle', 'Shared shopping lists and recipes for your family') }}
        </p>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
