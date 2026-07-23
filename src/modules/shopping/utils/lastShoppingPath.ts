/**
 * Persists the last visited shopping path so nav (bottom bar / sidebar)
 * can reopen the list the user left, or the lists index after they return there.
 */

import { ref } from 'vue'
import { SHOPPING_LAST_PATH_KEY } from '@/shared/config/config'
import { ShoppingRoutePaths } from '../routes'

const LIST_ID_PATTERN = /^[A-Za-z0-9_-]{1,36}$/

function isValidShoppingPath(path: string): boolean {
  const lists = ShoppingRoutePaths.lists
  if (path === lists) return true
  if (!path.startsWith(`${lists}/`)) return false
  const listId = path.slice(lists.length + 1)
  return LIST_ID_PATTERN.test(listId)
}

function readStoredPath(): string {
  try {
    const raw = localStorage.getItem(SHOPPING_LAST_PATH_KEY)
    if (raw && isValidShoppingPath(raw)) return raw
  }
  catch {
    // ignore
  }
  return ShoppingRoutePaths.lists
}

const lastShoppingPath = ref(readStoredPath())

export function getLastShoppingPath(): string {
  return lastShoppingPath.value
}

export function setLastShoppingPath(path: string): void {
  const next = isValidShoppingPath(path) ? path : ShoppingRoutePaths.lists
  lastShoppingPath.value = next
  try {
    localStorage.setItem(SHOPPING_LAST_PATH_KEY, next)
  }
  catch {
    // ignore
  }
}

export function clearLastShoppingPath(): void {
  setLastShoppingPath(ShoppingRoutePaths.lists)
}
