/**
 * Format a shopping item quantity + unit for display.
 * Uses locale-aware number formatting (e.g. comma decimal separator in pl-PL).
 */
export function formatItemQuantity(
  quantity: number | null,
  unit: string | null,
  locale: string,
): string {
  if (quantity === null) return ''
  const formatted = new Intl.NumberFormat(locale, {
    maximumFractionDigits: 2,
    minimumFractionDigits: Number.isInteger(quantity) ? 0 : undefined,
  }).format(quantity)
  return unit ? `${formatted}\u00a0${unit}` : formatted
}
