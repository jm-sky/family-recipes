/**
 * AI Context Composable
 * Handles context building for AI requests.
 *
 * Family Recipes does not send domain data to the AI assistant yet; the
 * context is limited to a configurable list of field names. Recipe import
 * context will plug in here in a later phase.
 */

import { computed, ref } from 'vue'
import { useAiStore } from '../store/useAiStore'

export interface IAiContext {
  fields?: string[]
}

export function useAiContext() {
  const aiStore = useAiStore()

  const selectedFields = ref<string[]>(['name', 'category', 'quantity'])

  const availableFields = computed<string[]>(() => {
    // Common fields that can be sent to AI
    return [
      'name',
      'category',
      'quantity',
      'unit',
      'notes',
    ]
  })

  const contextFields = computed<string[]>(() => {
    const settingsFields = aiStore.settings?.contextFields
    // Convert Record<string, any> to string[] by taking the keys
    if (settingsFields && typeof settingsFields === 'object' && !Array.isArray(settingsFields)) {
      return Object.keys(settingsFields)
    }
    // Fallback to selectedFields if no settings or if it's already an array (backward compatibility)
    return Array.isArray(settingsFields) ? settingsFields : selectedFields.value
  })

  const buildContext = (): IAiContext => {
    return {
      fields: selectedFields.value.length > 0 ? selectedFields.value : undefined,
    }
  }

  const buildContextData = (_ids?: string[]): Record<string, unknown> => {
    // No domain context is attached yet
    return {}
  }

  const setFields = (fields: string[]): void => {
    selectedFields.value = fields
  }

  const toggleField = (field: string): void => {
    const index = selectedFields.value.indexOf(field)
    if (index > -1) {
      selectedFields.value.splice(index, 1)
    } else {
      selectedFields.value.push(field)
    }
  }

  return {
    selectedFields,
    availableFields,
    contextFields,
    buildContext,
    buildContextData,
    setFields,
    toggleField,
  }
}
