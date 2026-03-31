import React, { useState } from 'react';
import type { Asset } from '../api';
import { api } from '../api';
import { t, useLang } from '../i18n';

const REFINE_TYPES = [
  { value: 'edge_fix', label: 'Edge Fix' },
  { value: 'ai_edit', label: 'AI Edit' },
  { value: 'ai_inpaint', label: 'AI Inpaint' },
  { value: 'style_unify', label: 'Style Unify' },
];

const ENGINES = ['Unity', 'Godot', 'Cocos', 'Web'];

interface ActionPanelProps {
  selected: Asset[];
  onRefresh: () => void;
  onToast: (msg: string, kind: 'info' | 'success' | 'error') => void;
  onClearSelection: () => void;
}

const ActionPanel: React.FC<ActionPanelProps> = ({
  selected,
  onRefresh,
  onToast,
  onClearSelection,
}) => {
  useLang();
  const [note, setNote] = useState('');
  const [refineType, setRefineType] = useState('edge_fix');
  const [reclassifyType, setReclassifyType] = useState('icon');
  const [showReclassify, setShowReclassify] = useState(false);
  const [loading, setLoading] = useState(false);

  if (selected.length === 0) return null;

  const handleRefine = async () => {
    setLoading(true);
    try {
      for (const asset of selected) {
        const res = await api.refine(asset.name, refineType, note);
        if (res?.error) {
          onToast(`Refine error: ${res.error}`, 'error');
          return;
        }
      }
      onToast(`Refined ${selected.length} asset(s)`, 'success');
      onRefresh();
    } catch {
      onToast('Refine failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete ${selected.length} asset(s)? This cannot be undone.`)) return;
    setLoading(true);
    try {
      for (const asset of selected) {
        await api.deleteAsset(asset.name);
      }
      onToast(`Deleted ${selected.length} asset(s)`, 'success');
      onClearSelection();
      onRefresh();
    } catch {
      onToast('Delete failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleReclassify = async () => {
    setLoading(true);
    try {
      for (const asset of selected) {
        await api.updateAsset(asset.name, { type: reclassifyType });
      }
      onToast(`Reclassified ${selected.length} asset(s) as ${reclassifyType}`, 'success');
      setShowReclassify(false);
      onRefresh();
    } catch {
      onToast('Reclassify failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (engine: string) => {
    setLoading(true);
    try {
      await api.exportAssets(engine);
      onToast(`Export to ${engine} started`, 'info');
    } catch {
      onToast('Export failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAtlas = async () => {
    setLoading(true);
    try {
      const type = selected[0]?.type ?? 'all';
      await api.packAtlas(type);
      onToast('Atlas packing started', 'info');
    } catch {
      onToast('Atlas packing failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="action-panel">
      <div className="action-panel__header">
        <span className="action-panel__count">{t('action.selected')} {selected.length} {t('action.assets')}</span>
        <button className="action-panel__close" onClick={onClearSelection}>✕</button>
      </div>

      <div className="action-panel__body">
        {/* Refine section */}
        <div className="action-panel__section">
          <div className="action-panel__row">
            <select
              className="action-select"
              value={refineType}
              onChange={(e) => setRefineType(e.target.value)}
            >
              {REFINE_TYPES.map((r) => (
                <option key={r.value} value={r.value}>{r.label}</option>
              ))}
            </select>
            <input
              className="action-note"
              type="text"
              placeholder={t('action.note')}
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
            <button
              className="action-btn action-btn--primary"
              onClick={handleRefine}
              disabled={loading}
            >
              {loading ? t('action.working') : t('action.refine')}
            </button>
          </div>
        </div>

        {/* Delete + Reclassify */}
        <div className="action-panel__section">
          <div className="action-panel__row">
            <button
              className="action-btn action-btn--danger"
              onClick={handleDelete}
              disabled={loading}
            >
              {t('action.delete')}
            </button>

            <button
              className="action-btn"
              onClick={() => setShowReclassify(!showReclassify)}
              disabled={loading}
            >
              {t('action.type')}
            </button>

            {showReclassify && (
              <>
                <select
                  className="action-select"
                  value={reclassifyType}
                  onChange={(e) => setReclassifyType(e.target.value)}
                >
                  {['character', 'icon', 'ui', 'card', 'background', 'sprite', 'tileset'].map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                <button
                  className="action-btn action-btn--primary"
                  onClick={handleReclassify}
                  disabled={loading}
                >
                  {t('action.submit')}
                </button>
              </>
            )}
          </div>
        </div>

        {/* Export + Atlas */}
        <div className="action-panel__section">
          <div className="action-panel__row">
            <span className="action-label">{t('action.export')}:</span>
            {ENGINES.map((engine) => (
              <button
                key={engine}
                className="action-btn action-btn--sm"
                onClick={() => handleExport(engine)}
                disabled={loading}
              >
                {engine}
              </button>
            ))}
            <button
              className="action-btn action-btn--atlas"
              onClick={handleAtlas}
              disabled={loading}
            >
              {t('action.atlas')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActionPanel;
