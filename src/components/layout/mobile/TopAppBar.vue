<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import UserNav from '@/components/layout/UserNav.vue'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRouteNames } from '@/modules/auth/config/routes'
import { useUser } from '@/modules/user/composables/useUser'
import { isMobileBottomNavRoot } from '@/shared/config/mobileNav'

defineProps<{
  actionsClass?: string
}>()

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { profile } = useUser()
const { logout, user: authUser } = useAuth()

const user = computed(() => authUser.value ?? profile.value)

const pageTitle = computed(() => {
  const metaTitle = route.meta.title as string | undefined
  if (!metaTitle) return ''
  return t(metaTitle)
})

const showBack = computed(() => !isMobileBottomNavRoot(route.path))

function handleBack() {
  router.back()
}

async function handleLogout() {
  try {
    await logout()
    toast.success(t('auth.logout_success', 'Logged out successfully'))
    await router.push({ name: AuthRouteNames.login })
  }
  catch (error) {
    console.error('Logout error:', error)
    toast.error(t('auth.logout_error', 'Failed to logout'))
  }
}
</script>

<template>
  <header
    class="sticky top-0 z-50 border-b bg-background/95 backdrop-blur-sm pt-[env(safe-area-inset-top)]"
  >
    <div class="flex h-(--app-bar-height) items-center gap-2 px-2">
      <div class="flex min-w-11 items-center justify-start">
        <Button
          v-if="showBack"
          variant="ghost"
          size="icon"
          class="size-11"
          :aria-label="t('common.back', 'Back')"
          @click="handleBack"
        >
          <ArrowLeft class="size-5" />
        </Button>
      </div>

      <h1 class="min-w-0 flex-1 truncate text-center text-base font-semibold">
        {{ pageTitle }}
      </h1>

      <div class="flex min-w-11 items-center justify-end" :class="actionsClass">
        <slot name="actions" />
        <UserNav
          :user-name="user?.name ?? t('user.guest')"
          :user-email="user?.email"
          :user-avatar="user?.avatarUrl"
          @logout="handleLogout"
        />
      </div>
    </div>
  </header>
</template>
