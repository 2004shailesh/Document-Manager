/**
 * ==============================================================================
 * Category Visual & Theme Mappings Utility
 * ==============================================================================
 * Purpose:
 *   Provides deterministic emoji icons and CSS gradient theme classes for
 *   standard and custom category names across the application.
 * ==============================================================================
 */

export const CATEGORY_ICON_MAP: Record<string, string> = {
  invoice: '🧾',
  invoices: '🧾',
  contracts: '📜',
  contract: '📜',
  reports: '📊',
  report: '📊',
  notes: '📝',
  note: '📝',
  medical: '🩺',
  others: '📁',
  other: '📁',
};

export function getCategoryIcon(name: string): string {
  const normalized = (name || '').toLowerCase().trim();
  return CATEGORY_ICON_MAP[normalized] || '📁';
}

export function getCategoryTheme(name: string): string {
  const normalized = (name || '').toLowerCase().trim();
  if (normalized.includes('invoice')) return 'theme-invoice';
  if (normalized.includes('contract')) return 'theme-contracts';
  if (normalized.includes('report')) return 'theme-reports';
  if (normalized.includes('note')) return 'theme-notes';
  if (normalized.includes('medical')) return 'theme-medical';
  return 'theme-others';
}
