export interface CategoryColorClasses {
  chip: string
  icon: string
}

export const CATEGORY_COLORS: Record<string, CategoryColorClasses> = {
  carrot: { chip: 'bg-orange-100 text-orange-900 dark:bg-orange-950 dark:text-orange-100', icon: 'text-orange-600 dark:text-orange-400' },
  milk: { chip: 'bg-sky-100 text-sky-900 dark:bg-sky-950 dark:text-sky-100', icon: 'text-sky-600 dark:text-sky-400' },
  croissant: { chip: 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-100', icon: 'text-amber-600 dark:text-amber-400' },
  beef: { chip: 'bg-rose-100 text-rose-900 dark:bg-rose-950 dark:text-rose-100', icon: 'text-rose-600 dark:text-rose-400' },
  wheat: { chip: 'bg-yellow-100 text-yellow-900 dark:bg-yellow-950 dark:text-yellow-100', icon: 'text-yellow-700 dark:text-yellow-300' },
  'cup-soda': { chip: 'bg-cyan-100 text-cyan-900 dark:bg-cyan-950 dark:text-cyan-100', icon: 'text-cyan-600 dark:text-cyan-400' },
  snowflake: { chip: 'bg-blue-100 text-blue-900 dark:bg-blue-950 dark:text-blue-100', icon: 'text-blue-600 dark:text-blue-400' },
  'spray-can': { chip: 'bg-violet-100 text-violet-900 dark:bg-violet-950 dark:text-violet-100', icon: 'text-violet-600 dark:text-violet-400' },
  'shopping-basket': { chip: 'bg-muted text-muted-foreground', icon: 'text-muted-foreground' },
}

export function getCategoryColors(iconKey: string | null | undefined): CategoryColorClasses {
  if (!iconKey) return CATEGORY_COLORS['shopping-basket']
  return CATEGORY_COLORS[iconKey] ?? CATEGORY_COLORS['shopping-basket']
}
