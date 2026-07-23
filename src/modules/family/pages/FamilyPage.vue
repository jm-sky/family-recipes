<script setup lang="ts">
import { Copy, Trash2, UserPlus, Users } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { useFamily } from '@/modules/family/composables/useFamily'

const { t } = useI18n()
const authStore = useAuthStore()

const {
  family,
  members,
  invitations,
  isLoadingFamily,
  hasNoFamily,
  isOwner,
  canInvite,
  createFamily,
  isCreatingFamily,
  createInvitation,
  isCreatingInvitation,
  removeMember,
} = useFamily()

const currentUserId = computed(() => authStore.user?.id ?? null)

const newFamilyName = ref('')

async function handleCreateFamily() {
  const name = newFamilyName.value.trim()
  if (!name) return
  await createFamily({ name })
  newFamilyName.value = ''
}

function invitationLink(token: string): string {
  return `${window.location.origin}/invitations/${token}`
}

async function copyInvitationLink(token: string) {
  await navigator.clipboard.writeText(invitationLink(token))
  toast.success(t('family.invitations.copied'))
}

function formatDate(value: string | null): string {
  if (!value) return t('family.invitations.never')
  return new Date(value).toLocaleDateString()
}

function canRemove(member: { userId: string, role: string }): boolean {
  return isOwner.value && member.role !== 'owner' && member.userId !== currentUserId.value
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-4xl mx-auto space-y-6">
      <div class="space-y-1">
        <h1 class="hidden text-page-title md:block">
          {{ t('family.page.title') }}
        </h1>
        <p class="text-sm text-muted-foreground">
          {{ t('family.page.subtitle') }}
        </p>
      </div>

      <!-- Loading -->
      <div v-if="isLoadingFamily" class="space-y-4">
        <div class="h-24 w-full bg-muted rounded animate-pulse" />
      </div>

      <!-- Onboarding: no family yet -->
      <Card v-else-if="hasNoFamily">
        <CardHeader>
          <div class="flex items-center gap-2">
            <Users :size="20" />
            <CardTitle>{{ t('family.onboarding.title') }}</CardTitle>
          </div>
          <CardDescription>{{ t('family.onboarding.description') }}</CardDescription>
        </CardHeader>
        <CardContent>
          <form class="space-y-4" @submit.prevent="handleCreateFamily">
            <div class="space-y-2">
              <Label for="family-name">{{ t('family.onboarding.nameLabel') }}</Label>
              <Input
                id="family-name"
                v-model="newFamilyName"
                :placeholder="t('family.onboarding.namePlaceholder')"
                autocomplete="off"
                maxlength="120"
              />
            </div>
            <Button type="submit" :disabled="!newFamilyName.trim() || isCreatingFamily">
              {{ t('family.onboarding.submit') }}
            </Button>
          </form>
        </CardContent>
      </Card>

      <!-- Family present -->
      <template v-else-if="family">
        <!-- Family summary -->
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <Users :size="20" />
                <CardTitle>{{ family.name }}</CardTitle>
              </div>
              <Badge variant="secondary">
                {{ t(`family.plans.${family.plan}`) }}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div class="text-muted-foreground">
                  {{ t('family.card.members') }}
                </div>
                <div class="font-medium">
                  {{ family.memberCount }}
                </div>
              </div>
              <div>
                <div class="text-muted-foreground">
                  {{ t('family.card.memberLimit') }}
                </div>
                <div class="font-medium">
                  {{ family.memberLimit === null ? t('family.card.unlimited') : family.memberLimit }}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Members -->
        <Card>
          <CardHeader>
            <CardTitle>{{ t('family.members.title') }}</CardTitle>
            <CardDescription>{{ t('family.members.description') }}</CardDescription>
          </CardHeader>
          <CardContent>
            <!-- Mobile: stacked member cards -->
            <div class="space-y-2 md:hidden">
              <div
                v-for="member in members"
                :key="member.userId"
                class="flex items-start justify-between gap-3 rounded-md border p-3"
              >
                <div class="min-w-0 flex-1 space-y-1">
                  <div class="font-medium">
                    {{ member.name }}
                    <span v-if="member.userId === currentUserId" class="text-muted-foreground">
                      ({{ t('family.members.you') }})
                    </span>
                  </div>
                  <p class="truncate text-sm text-muted-foreground">
                    {{ member.email }}
                  </p>
                  <Badge :variant="member.role === 'owner' ? 'default' : 'outline'">
                    {{ t(`family.roles.${member.role}`) }}
                  </Badge>
                </div>
                <Button
                  v-if="canRemove(member)"
                  variant="outline-destructive"
                  size="icon"
                  class="size-9 shrink-0"
                  :aria-label="t('family.members.remove')"
                  @click="removeMember(member.userId)"
                >
                  <Trash2 :size="14" />
                </Button>
              </div>
              <p v-if="!members || members.length === 0" class="text-center text-sm text-muted-foreground">
                {{ t('family.members.empty') }}
              </p>
            </div>

            <!-- Desktop: table -->
            <div class="hidden md:block">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{{ t('family.members.name') }}</TableHead>
                    <TableHead>{{ t('family.members.email') }}</TableHead>
                    <TableHead>{{ t('family.members.role') }}</TableHead>
                    <TableHead class="text-right">
                      {{ t('family.members.remove') }}
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow v-for="member in members" :key="member.userId">
                    <TableCell class="font-medium">
                      {{ member.name }}
                      <span v-if="member.userId === currentUserId" class="text-muted-foreground">
                        ({{ t('family.members.you') }})
                      </span>
                    </TableCell>
                    <TableCell class="text-muted-foreground">
                      {{ member.email }}
                    </TableCell>
                    <TableCell>
                      <Badge :variant="member.role === 'owner' ? 'default' : 'outline'">
                        {{ t(`family.roles.${member.role}`) }}
                      </Badge>
                    </TableCell>
                    <TableCell class="text-right">
                      <Button
                        v-if="canRemove(member)"
                        variant="outline-destructive"
                        size="sm"
                        @click="removeMember(member.userId)"
                      >
                        <Trash2 :size="14" />
                        {{ t('family.members.remove') }}
                      </Button>
                    </TableCell>
                  </TableRow>
                  <TableRow v-if="!members || members.length === 0">
                    <TableCell colspan="4" class="text-center text-muted-foreground">
                      {{ t('family.members.empty') }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Invitations (owner only) -->
        <Card v-if="isOwner">
          <CardHeader>
            <CardTitle>{{ t('family.invitations.title') }}</CardTitle>
            <CardDescription>{{ t('family.invitations.description') }}</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="flex items-center gap-3">
              <Button :disabled="!canInvite || isCreatingInvitation" @click="createInvitation()">
                <UserPlus :size="16" />
                {{ t('family.invitations.create') }}
              </Button>
              <span v-if="!canInvite" class="text-sm text-destructive">
                {{ t('family.invitations.limitReached') }}
              </span>
            </div>

            <div v-if="invitations && invitations.length > 0" class="space-y-2">
              <div
                v-for="invitation in invitations"
                :key="invitation.id"
                class="flex items-center justify-between gap-3 rounded-md border p-3"
              >
                <div class="min-w-0 flex-1">
                  <code class="block truncate text-xs text-muted-foreground">
                    {{ invitationLink(invitation.token) }}
                  </code>
                  <span class="text-xs text-muted-foreground">
                    {{ t('family.invitations.expiresAt') }}: {{ formatDate(invitation.expiresAt) }}
                  </span>
                </div>
                <Button variant="outline" size="sm" @click="copyInvitationLink(invitation.token)">
                  <Copy :size="14" />
                  {{ t('family.invitations.copy') }}
                </Button>
              </div>
            </div>
            <p v-else class="text-sm text-muted-foreground">
              {{ t('family.invitations.empty') }}
            </p>
          </CardContent>
        </Card>
      </template>
    </div>
  </AuthenticatedLayout>
</template>
