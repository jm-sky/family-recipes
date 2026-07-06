export interface Category {
  id: string
  name: string
  icon: string | null
  sortOrder: number
}

export interface ShoppingList {
  id: string
  name: string
  itemCount: number
  checkedCount: number
  createdAt: string
  updatedAt: string
}

export interface ShoppingItem {
  id: string
  listId: string
  name: string
  categoryId: string | null
  ingredientId: string | null
  quantity: number | null
  unit: string | null
  isChecked: boolean
  position: number
  createdAt: string
  updatedAt: string
}

export interface ShoppingListDetail extends ShoppingList {
  items: ShoppingItem[]
}

export interface CreateListRequest {
  name: string
}

export interface CreateItemRequest {
  name: string
  categoryId?: string | null
  quantity?: number | null
  unit?: string | null
}

export interface UpdateItemRequest {
  name?: string
  categoryId?: string | null
  quantity?: number | null
  unit?: string | null
  isChecked?: boolean
  position?: number
}

export interface CreateCategoryRequest {
  name: string
  icon?: string | null
  sortOrder?: number
}

export interface UpdateCategoryRequest {
  name?: string
  icon?: string | null
  sortOrder?: number
}

// Predefined units (mirrors backend app/modules/shopping/constants.py UNITS)
export const UNITS = [
  'szt',
  'g',
  'dag',
  'kg',
  'ml',
  'l',
  'szklanka',
  'łyżka',
  'łyżeczka',
  'opakowanie',
  'puszka',
  'butelka',
  'pęczek',
  'ząbek',
  'plaster',
  'garść',
  'szczypta',
] as const
