import React from 'react';

const TYPES = ['all', 'character', 'icon', 'ui', 'card', 'background', 'sprite', 'tileset'];

const SORT_OPTIONS = [
  { value: 'time', label: 'By Time' },
  { value: 'type', label: 'By Type' },
  { value: 'name', label: 'By Name' },
];

interface FilterBarProps {
  activeType: string;
  search: string;
  sort: string;
  totalCount: number;
  selectedCount: number;
  onTypeChange: (type: string) => void;
  onSearchChange: (search: string) => void;
  onSortChange: (sort: string) => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
}

const FilterBar: React.FC<FilterBarProps> = ({
  activeType,
  search,
  sort,
  totalCount,
  selectedCount,
  onTypeChange,
  onSearchChange,
  onSortChange,
  onSelectAll,
  onDeselectAll,
}) => {
  return (
    <div className="filter-bar">
      <div className="filter-bar__types">
        {TYPES.map((t) => (
          <button
            key={t}
            className={`filter-btn${activeType === t ? ' active' : ''}`}
            onClick={() => onTypeChange(t)}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="filter-bar__controls">
        <input
          className="filter-search"
          type="text"
          placeholder="Search assets..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
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

        <span className="filter-bar__count">{totalCount} assets</span>

        <button
          className="filter-btn-sm"
          onClick={onSelectAll}
          disabled={totalCount === 0}
        >
          Select All
        </button>
        <button
          className="filter-btn-sm"
          onClick={onDeselectAll}
          disabled={selectedCount === 0}
        >
          Deselect
        </button>
      </div>
    </div>
  );
};

export default FilterBar;
