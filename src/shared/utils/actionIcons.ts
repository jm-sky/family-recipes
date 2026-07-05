import {
  ArrowLeft,
  Copy,
  Download,
  Edit,
  Ellipsis,
  FileInput,
  FileJson,
  FileOutput,
  FileSpreadsheet,
  Globe,
  Image,
  Lock,
  Plus,
  Sparkles,
  SparklesIcon,
  Star,
  Trash2,
  Upload,
} from 'lucide-vue-next'
import type { Component } from 'vue'

/**
 * Mapping of action keys to their corresponding icon components.
 * This serves as the single source of truth for action icons across the application.
 *
 * Usage:
 * ```vue
 * <script setup>
 * import { getActionIcon } from '@/shared/utils/actionIcons'
 * const CreateIcon = getActionIcon('create')
 * </script>
 * <template>
 *   <CreateIcon class="size-4" />
 * </template>
 * ```
 */
export const ACTION_ICONS: Record<string, Component> = {
  // Navigation
  back: ArrowLeft,
  moreActions: Ellipsis,

  // CRUD Operations
  create: Plus,
  addItem: Plus,
  edit: Edit,
  clone: Copy,
  delete: Trash2,
  deleteAll: Trash2,
  publish: Globe,

  // Import/Export
  export: Download,
  import: Upload,
  importFromMarkdown: FileInput,
  exportToPrompt: FileOutput,
  exportAllToMarkdown: FileOutput,
  exportToCSV: FileSpreadsheet,
  exportToJson: FileJson,

  // AI/Automation
  ai: Sparkles, // Main AI assistant button
  aiPremium: Lock, // Premium AI assistant button (locked)
  recognizeParameters: SparklesIcon,
  recognizeParametersAll: SparklesIcon,

  // Display
  toggleItemImages: Image,

  // Item Actions
  uploadPhoto: Upload,
  starItem: Star,
}

/**
 * Get icon component for an action
 * @param action - Action key
 * @returns Icon component, throws error if action not found
 */
export function getActionIcon(action: string): Component {
  const icon = ACTION_ICONS[action]
  if (!icon) {
    throw new Error(`Action icon not found for: ${action}. Available actions: ${Object.keys(ACTION_ICONS).join(', ')}`)
  }
  return icon
}

/**
 * Type-safe action icon keys
 */
export type ActionIconKey = keyof typeof ACTION_ICONS
