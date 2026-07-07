import { reactive } from 'vue'

export interface ConfirmSheetOptions {
  title: string
  description?: string
  confirmLabel?: string
  cancelLabel?: string
  destructive?: boolean
}

interface ConfirmSheetState {
  open: boolean
  options: ConfirmSheetOptions | null
  resolve: ((value: boolean) => void) | null
}

export const confirmSheetState = reactive<ConfirmSheetState>({
  open: false,
  options: null,
  resolve: null,
})

function closeConfirmSheet() {
  confirmSheetState.open = false
  confirmSheetState.options = null
  confirmSheetState.resolve = null
}

export function resolveConfirmSheet(confirmed: boolean) {
  confirmSheetState.resolve?.(confirmed)
  closeConfirmSheet()
}

export function useConfirmSheet() {
  function confirm(options: ConfirmSheetOptions): Promise<boolean> {
    return new Promise((resolve) => {
      confirmSheetState.options = options
      confirmSheetState.resolve = resolve
      confirmSheetState.open = true
    })
  }

  return { confirm }
}
