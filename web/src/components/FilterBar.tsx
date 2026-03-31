import React from 'react';
import { t, useLang } from '../i18n';

const TYPES = ['all', 'character', 'icon', 'ui', 'card', 'background', 'sprite', 'tileset'];

const TYPE_LABEL_KEYS: Record<string, string> = {
  all: 'filter.all',
  character: 'filter.character',
  icon: 'filter.icon',
  ui: 'filter.ui',
  card: 'filter.card',
  background: 'filter.background',
  sprite: 'filter.sprite',
  tileset: 'filter.tileset',
};

interface FilterBarProps {
  activeType: string;
  search: string;
  sort: string;
  tagFilter: string;
  totalCount: number;
  selectedCount: number;
  onTypeChange: (type: string) => void;
  onSearchChange: (search: string) => void;
  onSortChange: (sort: string) => void;
  onTagFilterChange: (tag: string) => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
}

const FilterBar: React.FC<FilterBarProps> = ({
  activeType,
  search,
  sort,
  tagFilter,
  totalCount,
  selectedCount,
  onTypeChange,
  onSearchChange,
  onSortChange,
  onTagFilterChange,
  onSelectAll,
  onDeselectAll,
}) => {
  // Subscribe to language changes so labels re-render on toggle
  useLang();

  const SORT_OPTIONS = [
    { value: 'time', label: t('filter.byTime') },
    { value: 'type', label: t('filter.byType') },
    { value: 'name', label: t('filter.byName') },
  ];

  return (
    <div className="filter-bar">
      <div className="filter-bar__types">
        {TYPES.map((type) => (
          <button
            key={type}
            className={`filter-btn${activeType === type ? ' active' : ''}`}
            onClick={() => onTypeChange(type)}
          >
            {t(TYPE_LABEL_KEYS[type])}
          </button>
        ))}
      </div>

      <div className="filter-bar__controls">
        <input
          className="filter-search"
          type="text"
          placeholder={t('filter.search')}
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />

        <input
          className="filter-search filter-tag-search"
          type="text"
          placeholder={t('filter.tagFilter')}
          value={tagFilter}
          onChange={(e) => onTagFilterChange(e.target.value)}
        />

        <select
          className="filter-sort"
          value={sort}
          onChange={(e) => onSortChange(e.target.value)}
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>

        <span className="filter-bar__count">{totalCount} {t('filter.assets')}</span>

        <button
          className="filter-btn-sm"
          onClick={onSelectAll}
          disabled={totalCount === 0}
        >
          {t('filter.selectAll')}
        </button>
        <button
          className="filter-btn-sm"
          onClick={onDeselectAll}
          disabled={selectedCount === 0}
        >
          {t('filter.deselect')}
        </button>
      </div>
    </div>
  );
};

export default FilterBar;
