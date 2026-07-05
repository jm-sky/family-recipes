/**
 * AI Actions Composable
 * Handles executing actions from AI structured output.
 *
 * No structured actions are supported yet in Family Recipes — the AI assistant
 * is conversational only. Recipe import will plug in here in a later phase.
 */

import type { IAiStructuredOutput } from '../types'

export function useAiActions() {
  const executeAction = async (
    structuredOutput: IAiStructuredOutput | null,
    _containerId?: string,
  ): Promise<boolean> => {
    if (!structuredOutput || !structuredOutput.action || structuredOutput.action === 'None') {
      return false
    }

    // No actions supported yet
    return false
  }

  return {
    executeAction,
  }
}
