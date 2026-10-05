/**
 * ==============================================================================
 * CategoryCard Component
 * ==============================================================================
 * Purpose:
 *   Interactive dashboard widget that renders category title, dynamic icon,
 *   document count, and selection styling.
 *
 * Accessibility:
 *   Supports standard keyboard navigation (`tabIndex={0}`, Enter and Space key triggers).
 * ==============================================================================
 */

import { getCategoryIcon, getCategoryTheme } from '../utils/category';
import './categorycard.css';

interface CategoryCardProps {
  name: string;
  count: number;
  icon?: string;
  onClick?: () => void;
  isSelected?: boolean;
}

function CategoryCard({ name, count, icon, onClick, isSelected }: CategoryCardProps) {
  const displayIcon = icon || getCategoryIcon(name);
  const themeClass = getCategoryTheme(name);
  const documentLabel = count === 1 ? 'document' : 'documents';

  return (
    <div
      className={`category-card ${themeClass} ${isSelected ? 'selected' : ''}`}
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      }}
      aria-label={`${name} category: ${count} ${documentLabel}`}
    >
      <div className="category-icon-wrapper" aria-hidden="true">
        <span className="category-icon">{displayIcon}</span>
      </div>
      <div className="category-info">
        <h3>{name}</h3>
        <p className="category-count">
          {count} {documentLabel}
        </p>
      </div>
      <div className="category-arrow" aria-hidden="true">
        →
      </div>
    </div>
  );
}

export default CategoryCard;
