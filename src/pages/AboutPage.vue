<script setup lang="ts">
import { Check, Copy } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'

const { t } = useI18n()
const copied = ref(false)

const aiContextMarkdown = computed(() => {
  return `# Family Recipes - AI Context

## Overview
Family Recipes is a full-stack web application for families that plan meals and shopping together. It combines shared shopping lists with a family recipe collection.

## Key Capabilities
- **Family Platform** - Secure user accounts grouped into families with shared data
- **PWA Architecture** - Installable app that also works offline with local cache
- **Smart Shopping Lists** - Multiple lists, editable categories, quantities and units
- **Ingredient Awareness** - Per-ingredient unit conversions merge duplicate items automatically
- **Recipes with Sources** - Ingredients stored in the app, full instructions behind a source link

## Core Features

### Shopping Lists
- Multiple lists (home, weekend, party) shared within the family
- Editable categories with icons and custom ordering
- Quick add from text with quantity and unit recognition
- Automatic merging - the same ingredient added twice becomes one item with a summed quantity (cup of flour + 130 g of flour = one item)
- Check off items as you shop

### Recipes
- Recipes with ingredients, servings, category (breakfast/lunch/dinner/dessert) and tags
- Link to the source page for full preparation steps
- Recipe photo upload
- Add all or missing ingredients to a shopping list in one click

## Business Features

### User Management & Security
- Email/password authentication with secure password hashing
- OAuth social login (Google)
- Email verification
- Two-factor authentication (2FA) - TOTP and WebAuthn (passkeys)
- Password management - reset and change
- reCAPTCHA v3 protection
- JWT tokens with automatic refresh
- GDPR-compliant account deletion

### Family & Plans
- One user belongs to one family; invitations via link
- Plans (Free/Basic/Pro) limit the number of family members

### Multi-Language Support
- English and Polish fully supported
- Automatic locale detection, manual switching
- All UI text, validation messages, and emails localized

### Theming
- Dark mode with system preference detection
- Theme persistence per user account

## Technical Stack

### Frontend
- Vue 3.5+ with TypeScript & Composition API
- Pinia for state management
- Vue Router for navigation
- TailwindCSS v4 + shadcn-vue components
- VeeValidate + Zod for form validation
- TanStack Query for server state management
- vue-i18n for internationalization

### Backend
- FastAPI (Python) with async/await
- PostgreSQL database
- SQLAlchemy ORM with async support
- JWT authentication with refresh tokens
- Rate limiting and reCAPTCHA protection
- Modular architecture (auth, two-factor, family, shopping, recipes, ingredients)`
})

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(aiContextMarkdown.value)
    copied.value = true
    toast.success(t('aiContext.copied', 'Context copied to clipboard'))
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error copying to clipboard:', error)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-8">
      <div class="space-y-2">
        <h1 class="text-3xl font-bold tracking-tight">
          {{ t('about.title', 'About Family Recipes') }}
        </h1>
        <p class="text-muted-foreground">
          {{ t('about.subtitle', 'Shared shopping lists and family recipes in one app') }}
        </p>
      </div>

      <!-- Table of Contents -->
      <nav class="flex flex-row flex-wrap items-center gap-2 text-sm text-muted-foreground">
        <a href="#overview" class="text-primary hover:underline">
          {{ t('about.overview.title', 'Overview') }}
        </a>
        <span>|</span>
        <a href="#capabilities" class="text-primary hover:underline">
          {{ t('about.capabilities.title', 'Key Capabilities') }}
        </a>
        <span>|</span>
        <a href="#core-features" class="text-primary hover:underline">
          {{ t('about.coreFeatures.title', 'Core Features') }}
        </a>
        <span>|</span>
        <a href="#technical-stack" class="text-primary hover:underline">
          {{ t('about.technical.title', 'Technical Stack') }}
        </a>
        <span>|</span>
        <a href="#ai-context" class="text-primary hover:underline">
          {{ t('aiContext.title', 'AI Context') }}
        </a>
      </nav>

      <!-- Overview -->
      <section id="overview" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.overview.title', 'Overview') }}
        </h2>
        <p class="text-muted-foreground">
          {{ t('about.overview.description', 'Family Recipes is a full-stack application for families that want to plan meals and shopping together.') }}
        </p>
      </section>

      <!-- Key Capabilities -->
      <section id="capabilities" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.capabilities.title', 'Key Capabilities') }}
        </h2>
        <ul class="list-disc list-inside space-y-2 text-muted-foreground">
          <li>{{ t('about.capabilities.multiUser', 'Family Platform - Secure user accounts grouped into families with shared data') }}</li>
          <li>{{ t('about.capabilities.hybrid', 'PWA Architecture - Installable app that also works offline with local cache') }}</li>
          <li>{{ t('about.capabilities.organization', 'Smart Shopping Lists - Multiple lists, editable categories, quantities and units') }}</li>
          <li>{{ t('about.capabilities.metadata', 'Ingredient Awareness - Unit conversions per ingredient merge duplicate items automatically') }}</li>
          <li>{{ t('about.capabilities.portability', 'Recipes with Sources - Store ingredients and link to the original recipe for full instructions') }}</li>
        </ul>
      </section>

      <!-- Core Features -->
      <section id="core-features" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.coreFeatures.title', 'Core Features') }}
        </h2>
        <div class="space-y-6">
          <div id="shopping-lists" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.shopping.title', 'Shopping Lists') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.shopping.multiple', 'Multiple lists (home, weekend, party) shared within the family') }}</li>
              <li>{{ t('about.coreFeatures.shopping.categories', 'Editable categories with icons and custom ordering') }}</li>
              <li>{{ t('about.coreFeatures.shopping.quickAdd', 'Quick add from text with quantity and unit recognition') }}</li>
              <li>{{ t('about.coreFeatures.shopping.merging', 'Automatic merging - the same ingredient added twice becomes one item with a summed quantity') }}</li>
              <li>{{ t('about.coreFeatures.shopping.checking', 'Check off items as you shop') }}</li>
            </ul>
          </div>

          <div id="recipes" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.recipes.title', 'Recipes') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.recipes.rich', 'Recipes with ingredients, servings, category and tags') }}</li>
              <li>{{ t('about.coreFeatures.recipes.source', 'Link to the source page for full preparation steps') }}</li>
              <li>{{ t('about.coreFeatures.recipes.photo', 'Recipe photo upload') }}</li>
              <li>{{ t('about.coreFeatures.recipes.addToList', 'Add all or missing ingredients to a shopping list in one click') }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Technical Stack -->
      <section id="technical-stack" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.technical.title', 'Technical Stack') }}
        </h2>
        <div class="space-y-4">
          <div id="frontend" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.technical.frontend.title', 'Frontend') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>Vue 3.5+ with TypeScript & Composition API</li>
              <li>Pinia for state management</li>
              <li>Vue Router for navigation</li>
              <li>TailwindCSS v4 + shadcn-vue components</li>
              <li>VeeValidate + Zod for form validation</li>
              <li>TanStack Query for server state management</li>
              <li>vue-i18n for internationalization</li>
            </ul>
          </div>

          <div id="backend" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.technical.backend.title', 'Backend') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>FastAPI (Python) with async/await</li>
              <li>PostgreSQL database</li>
              <li>SQLAlchemy ORM with async support</li>
              <li>JWT authentication with refresh tokens</li>
              <li>Rate limiting and reCAPTCHA protection</li>
              <li>Modular architecture (auth, two-factor, family, shopping, recipes, ingredients)</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- AI Context -->
      <section id="ai-context" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('aiContext.title', 'AI Context') }}
        </h2>
        <p class="text-muted-foreground">
          {{ t('aiContext.subtitle', 'Short description of Family Recipes in Markdown format for AI assistants like ChatGPT') }}
        </p>

        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle>
                  {{ t('aiContext.card.title', 'Copy Context to Clipboard') }}
                </CardTitle>
                <CardDescription>
                  {{ t('aiContext.card.description', 'Click the button below to copy the context description.') }}
                </CardDescription>
              </div>
              <Button @click="handleCopy">
                <Copy v-if="!copied" class="size-4" />
                <Check v-else class="size-4" />
                {{ copied ? t('common.copyToClipboard.copied') : t('common.copyToClipboard.copy') }}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <pre class="whitespace-pre-wrap text-sm font-mono bg-muted p-4 rounded-md border overflow-x-auto max-h-[600px] overflow-y-auto">{{ aiContextMarkdown }}</pre>
          </CardContent>
        </Card>
      </section>
    </div>
  </AuthenticatedLayout>
</template>
