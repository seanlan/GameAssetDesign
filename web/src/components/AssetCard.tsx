import React from 'react';
import type { Asset } from '../api';
import { api } from '../api';

interface AssetCardProps {
  asset: Asset;
  selected: boolean;
  onClick: (asset: Asset) => void;
  onDoubleClick: (asset: Asset) => void;
}

const TYPE_COLORS: Record<string, string> = {
  character: '#e94560',
  icon: '#0f9b8e',
  ui: '#5b7fcb',
  card: '#a06cd5',
  background: '#2d8a4e',
  sprite: '#e08c2a',
  tileset: '#c44b4b',
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)}MB`;
}

const AssetCard: React.FC<AssetCardProps> = ({ asset, selected, onClick, onDoubleClick }) => {
  const badgeColor = TYPE_COLORS[asset.type] ?? '#666';

  return (
    <div
      className={`asset-card${selected ? ' selected' : ''}`}
      onClick={() => onClick(asset)}
      onDoubleClick={() => onDoubleClick(asset)}
    >
      <div className="asset-card__thumb">
        <img
          src={api.getImageUrl(asset)}
          alt={asset.name}
          loading="lazy"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
      </div>

      <div className="asset-card__info">
        <div className="asset-card__name" title={asset.name}>
          {asset.name}
        </div>
        <div className="asset-card__meta">
          <span
            className="asset-card__badge"
            style={{ backgroundColor: badgeColor }}
          >
            {asset.type}
          </span>
          <span className="asset-card__dims">
            {asset.width}×{asset.height}
          </span>
          <span className="asset-card__size">{formatSize(asset.size_bytes)}</span>
        </div>
      </div>

      {selected && <div className="asset-card__check">✓</div>}
    </div>
  );
};

export default AssetCard;
