<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { Notebook } from 'lucide-vue-next'
import { useForm } from 'vee-validate'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import z from 'zod'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { FormControl, FormField, FormItem, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useKeepIntegration } from '../composables/useKeepIntegration'

const { t } = useI18n()
const { status, isStatusLoading, connect, isConnecting, disconnect, isDisconnecting } = useKeepIntegration()

const understood = ref(false)

const { handleSubmit, resetForm, isSubmitting } = useForm({
  initialValues: { email: '', masterToken: '', deviceId: '' },
  validationSchema: toTypedSchema(z.object({
    email: z.string().email(t('settings.integrations.keep.form.emailInvalid')),
    masterToken: z.string().min(10, t('settings.integrations.keep.form.tokenRequired')),
    deviceId: z.string().optional(),
  })),
})

const handleConnect = handleSubmit(async (values) => {
  await connect({
    email: values.email,
    masterToken: values.masterToken,
    deviceId: values.deviceId || undefined,
  })
  resetForm()
  understood.value = false
})

const handleDisconnect = async () => {
  if (confirm(t('settings.integrations.keep.confirmDisconnect'))) {
    await disconnect()
  }
}

const lastSyncLabel = computed(() => {
  const lastSyncAt = status.value?.lastSyncAt
  if (!lastSyncAt) return null
  return new Date(lastSyncAt).toLocaleString()
})
</script>

<template>
  <Card v-if="!isStatusLoading">
    <CardHeader>
      <div class="flex items-center gap-2">
        <Notebook :size="20" />
        <CardTitle>{{ t('settings.integrations.keep.title') }}</CardTitle>
      </div>
      <CardDescription>{{ t('settings.integrations.keep.description') }}</CardDescription>
    </CardHeader>
    <CardContent>
      <div v-if="status?.connected" class="space-y-3">
        <div class="rounded-md border bg-muted/50 p-3">
          <div class="flex items-center justify-between gap-2">
            <div>
              <p class="text-sm font-medium">
                {{ t('settings.integrations.keep.connected', { email: status.googleEmail }) }}
              </p>
              <p v-if="lastSyncLabel" class="text-xs text-muted-foreground">
                {{ t('settings.integrations.keep.lastSync', { time: lastSyncLabel }) }}
              </p>
              <p v-if="status.lastError" class="text-xs text-destructive">
                {{ status.lastError }}
              </p>
            </div>
            <Button
              variant="destructive"
              size="sm"
              :loading="isDisconnecting"
              @click="handleDisconnect"
            >
              {{ t('settings.integrations.keep.disconnect') }}
            </Button>
          </div>
        </div>
      </div>

      <form v-else class="space-y-3" @submit.prevent="handleConnect">
        <ol class="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
          <li>{{ t('settings.integrations.keep.instructions.step1') }}</li>
          <li>{{ t('settings.integrations.keep.instructions.step2') }}</li>
          <li>{{ t('settings.integrations.keep.instructions.step3') }}</li>
        </ol>

        <FormField v-slot="{ componentField }" name="email">
          <FormItem>
            <Label for="keep-email">{{ t('settings.integrations.keep.form.email') }}</Label>
            <FormControl>
              <Input
                id="keep-email"
                v-bind="componentField"
                type="email"
                :disabled="isSubmitting"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="masterToken">
          <FormItem>
            <Label for="keep-master-token">{{ t('settings.integrations.keep.form.masterToken') }}</Label>
            <FormControl>
              <Input
                id="keep-master-token"
                v-bind="componentField"
                type="password"
                class="font-mono text-sm"
                :disabled="isSubmitting"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="deviceId">
          <FormItem>
            <Label for="keep-device-id">{{ t('settings.integrations.keep.form.deviceId') }}</Label>
            <FormControl>
              <Input
                id="keep-device-id"
                v-bind="componentField"
                :placeholder="t('settings.integrations.keep.form.deviceIdPlaceholder')"
                :disabled="isSubmitting"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <div class="flex items-start space-x-2">
          <Checkbox
            id="keep-understood"
            v-model="understood"
          />
          <Label for="keep-understood" class="text-xs text-muted-foreground font-normal">
            {{ t('settings.integrations.keep.form.understood') }}
          </Label>
        </div>

        <p class="text-xs text-muted-foreground">
          {{ t('settings.integrations.keep.form.revokeHint') }}
        </p>

        <Button
          type="submit"
          :loading="isSubmitting || isConnecting"
          :disabled="!understood"
        >
          {{ t('settings.integrations.keep.form.connect') }}
        </Button>
      </form>
    </CardContent>
  </Card>
</template>
