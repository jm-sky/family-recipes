export interface KeepStatus {
  connected: boolean
  googleEmail: string | null
  lastSyncAt: string | null
  lastError: string | null
}

export interface KeepConnectRequest {
  email: string
  masterToken: string
  deviceId?: string
}

export interface KeepMirror {
  id: string
  shoppingListId: string
  keepNoteId: string
  autoSync: boolean
  lastPushedAt: string | null
}

export interface KeepMirrorCreateRequest {
  shoppingListId: string
  createNewNote?: boolean
}

export interface KeepSyncAllResultItem {
  mirrorId: string
  success: boolean
  error: string | null
}
