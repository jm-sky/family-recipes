import { computed, ref, toValue, watch } from 'vue'
import { familyService } from '@/modules/family/services/familyService'
import { mapInvitationErrorKey } from '@/modules/family/utils/invitationErrors'
import type { MaybeRefOrGetter } from 'vue'
import type { InvitationPreview } from '@/modules/family/types'

export function useInvitationPreview(token: MaybeRefOrGetter<string | null | undefined>) {
  const preview = ref<InvitationPreview | null>(null)
  const errorKey = ref<string | null>(null)
  const isLoading = ref(false)

  const resolvedToken = computed(() => {
    const value = toValue(token)
    return value ? String(value) : null
  })

  async function load() {
    const currentToken = resolvedToken.value
    if (!currentToken) {
      preview.value = null
      errorKey.value = null
      return
    }

    isLoading.value = true
    errorKey.value = null
    try {
      preview.value = await familyService.getInvitationPreview(currentToken)
    } catch (error) {
      preview.value = null
      errorKey.value = mapInvitationErrorKey(error)
    } finally {
      isLoading.value = false
    }
  }

  watch(resolvedToken, load, { immediate: true })

  return {
    preview,
    errorKey,
    isLoading,
    reload: load,
  }
}
