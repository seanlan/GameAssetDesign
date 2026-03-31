import React from 'react';
import type { Asset } from '../api';

interface StatsPanelProps {
  assets: Asset[];
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const StatsPanel: React.FC<StatsPanelProps> = ({ assets }) => {
  if (!assets || assets.length === 0) return null;

  const byType: Record<string, number> = {};
  let totalSize = 0;

  assets.forEach((a) => {
    byType[a.type] = (byType[a.type] || 0) + 1;
    totalSize += a.size_bytes || 0;
  });

  const maxCount = Math.max(...Object.values(byType));
  const types = Object.entries(byType).sort((a, b) => b[1] - a[1]);

  return (
    <div className="stats-panel">
      <div className="stats-panel__summary">
        <span className="stats-panel__total">
          <strong>{assets.length}</strong> assets
        </span>
        <span className="stats-panel__size">{formatBytes(totalSize)}</span>
      </div>
      <div className="stats-panel__bars">
        {types.map(([type, count]) => {
          const pct = maxCount > 0 ? Math.round((count / maxCount) * 100) : 0;
          return (
            <div key={type} className="stats-bar">
              <span className="stats-bar__label">{type}</span>
              <div className="stats-bar__track">
                <div className="stats-bar__fill" style={{ width: `${pct}%` }} />
              </div>
              <span className="stats-bar__count">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StatsPanel;
