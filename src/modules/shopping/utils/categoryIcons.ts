import {
  Beef,
  Carrot,
  Croissant,
  CupSoda,
  Milk,
  ShoppingBasket,
  Snowflake,
  SprayCan,
  Wheat,
} from 'lucide-vue-next'
import type { Component } from 'vue'

export const CATEGORY_ICONS: Record<string, Component> = {
  carrot: Carrot,
  milk: Milk,
  croissant: Croissant,
  beef: Beef,
  wheat: Wheat,
  'cup-soda': CupSoda,
  snowflake: Snowflake,
  'spray-can': SprayCan,
  'shopping-basket': ShoppingBasket,
}

export function getCategoryIcon(iconKey: string | null | undefined): Component {
  if (!iconKey) return ShoppingBasket
  return CATEGORY_ICONS[iconKey] ?? ShoppingBasket
}
