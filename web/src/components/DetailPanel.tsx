import React, { useState, useEffect } from 'react';
import type { Asset } from '../api';
import { api } from '../api';

interface Version {
  version: number;
  created_at: string;
  note?: string;
}

interface DetailPanelProps {
  asset: Asset;
  onClose: () => void;
  onRefresh: () => void;
  onToast: (msg: string, kind: 'info' | 'success' | 'error') => void;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

const DetailPanel: React.FC<DetailPanelProps> = ({ asset, onClose, onRefresh, onToast }) => {
  const [versions, setVersions] = useState<Version[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);
  const [rollingBack, setRollingBack] = useState<number | null>(null);

  useEffect(() => {
    setLoadingVersions(true);
    api.getVersions(asset.name)
      .then((data) => setVersions(Array.isArray(data) ? data : []))
      .catch(() => setVersions([]))
      .finally(() => setLoadingVersions(false));
  }, [asset.name]);

  const handleRollback = async (version: number) => {
    if (!confirm(`Rollback ${asset.name} to version ${version}?`)) return;
    setRollingBack(version);
    try {
      await api.rollback(asset.name, version);
      onToast(`Rolled back to version ${version}`, 'success');
      onRefresh();
    } catch {
      onToast('Rollback failed', 'error');
    } finally {
      setRollingBack(null);
    }
  };

  const relationships = asset.relationships ?? {};

  return (
    <div className="detail-panel">
      <div className="detail-panel__header">
        <h3 className="detail-panel__title" title={asset.name}>{asset.name}</h3>
        <button className="detail-panel__close" onClick={onClose}>✕</button>
      </div>

      <div className="detail-panel__preview">
        <img
          src={api.getImageUrl(asset)}
          alt={asset.name}
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
      </div>

      <div className="detail-panel__meta">
        <table className="detail-table">
          <tbody>
            <tr>
              <td>Type</td>
              <td><span className="detail-badge">{asset.type}</span></td>
            </tr>
            <tr>
              <td>Dimensions</td>
              <td>{asset.width} × {asset.height}</td>
            </tr>
            <tr>
              <td>Size</td>
              <td>{formatSize(asset.size_bytes)}</td>
            </tr>
            <tr>
              <td>Model</td>
              <td>{asset.model || '—'}</td>
            </tr>
            <tr>
              <td>Style</td>
              <td>{asset.style || '—'}</td>
            </tr>
            <tr>
              <td>Generated</td>
              <td>{formatDate(asset.generated_at)}</td>
            </tr>
          </tbody>
        </table>

        {asset.prompt && (
          <div className="detail-section">
            <div className="detail-section__label">Prompt</div>
            <div className="detail-section__text">{asset.prompt}</div>
          </div>
        )}

        {Object.keys(relationships).length > 0 && (
          <div className="detail-section">
            <div className="detail-section__label">Relationships</div>
            {Object.entries(relationships).map(([key, val]) => (
              <div key={key} className="detail-relation">
                <span className="detail-relation__key">{key}:</span>
                <span className="detail-relation__val">
                  {Array.isArray(val) ? val.join(', ') : String(val)}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="detail-section">
          <div className="detail-section__label">Version History</div>
          {loadingVersions ? (
            <div className="detail-loading">Loading...</div>
          ) : versions.length === 0 ? (
            <div className="detail-empty">No version history</div>
          ) : (
            <ul className="detail-versions">
              {versions.map((v) => (
                <li key={v.version} className="detail-version">
                  <span className="detail-version__num">v{v.version}</span>
                  <span className="detail-version__date">{formatDate(v.created_at)}</span>
                  {v.note && <span className="detail-version__note">{v.note}</span>}
                  <button
                    className="detail-version__rollback"
                    onClick={() => handleRollback(v.version)}
                    disabled={rollingBack === v.version}
                  >
                    {rollingBack === v.version ? '...' : 'Rollback'}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default DetailPanel;
