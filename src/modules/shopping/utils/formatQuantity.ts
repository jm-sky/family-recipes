/**
 * Format a shopping item quantity + unit for display.
 * Uses locale-aware number formatting and prefers shopping-friendly units
 * (e.g. 4000 ml → 4 l, 1500 g → 1.5 kg).
 */
export function formatItemQuantity(
  quantity: number | null,
  unit: string | null,
  locale: string,
): string {
  if (quantity === null) return ''
  const { quantity: displayQty, unit: displayUnit } = toPreferredDisplayUnit(quantity, unit)
  const formatted = new Intl.NumberFormat(locale, {
    maximumFractionDigits: 2,
    minimumFractionDigits: Number.isInteger(displayQty) ? 0 : undefined,
  }).format(displayQty)
  return displayUnit ? `${formatted}\u00a0${displayUnit}` : formatted
}

/** Prefer l/kg for large metric amounts stored in ml/g. */
export function toPreferredDisplayUnit(
  quantity: number,
  unit: string | null,
): { quantity: number, unit: string | null } {
  const normalized = unit?.toLowerCase() ?? null
  if (normalized === 'ml' && quantity >= 1000) {
    return { quantity: quantity / 1000, unit: 'l' }
  }
  if (normalized === 'g' && quantity >= 1000) {
    return { quantity: quantity / 1000, unit: 'kg' }
  }
  return { quantity, unit: normalized }
}
