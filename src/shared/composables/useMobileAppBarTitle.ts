import { onUnmounted, ref, toValue, watch, type MaybeRefOrGetter } from 'vue'

/** Shared override for the mobile TopAppBar title (null = use route.meta.title). */
export const mobileAppBarTitle = ref<string | null>(null)

/**
 * Bind a page's dynamic title into the mobile app bar for the lifetime of the caller.
 */
export function useMobileAppBarTitle(title: MaybeRefOrGetter<string | null | undefined>) {
  watch(
    () => toValue(title),
    (value) => {
      mobileAppBarTitle.value = value ?? null
    },
    { immediate: true },
  )

  onUnmounted(() => {
    mobileAppBarTitle.value = null
  })
}
