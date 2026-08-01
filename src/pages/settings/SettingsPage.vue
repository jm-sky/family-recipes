<script setup lang="ts">
import KeepIntegrationCard from '@/modules/settings/components/KeepIntegrationCard.vue'
import SettingsPageCore from '@/modules/settings/pages/SettingsPage.vue'
import { config } from '@/shared/config/config'
</script>

<template>
  <SettingsPageCore>
    <template #after>
      <KeepIntegrationCard v-if="config.features.keepSync.enabled" />
    </template>
  </SettingsPageCore>
</template>

