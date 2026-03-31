import React, { useState } from 'react';
import { api } from '../api';

const ASSET_TYPES = [
  'character', 'icon', 'ui', 'card', 'background', 'sprite', 'tileset',
];

const STYLES = [
  { value: '', label: '(default)' },
  { value: 'pixel_art', label: 'Pixel Art' },
  { value: 'flat', label: 'Flat' },
  { value: 'cartoon', label: 'Cartoon' },
  { value: 'realistic', label: 'Realistic' },
  { value: 'hand_drawn', label: 'Hand Drawn' },
  { value: 'chibi', label: 'Chibi' },
];

interface GeneratePanelProps {
  onClose: () => void;
  onToast: (msg: string, kind: 'info' | 'success' | 'error') => void;
  onRefresh: () => void;
  onApiKeyError: () => void;
}

const GeneratePanel: React.FC<GeneratePanelProps> = ({
  onClose,
  onToast,
  onRefresh,
  onApiKeyError,
}) => {
  const [description, setDescription] = useState('');
  const [assetType, setAssetType] = useState('character');
  const [style, setStyle] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!description.trim()) {
      onToast('Please enter a description', 'error');
      return;
    }
    setLoading(true);
    try {
      const res = await api.generate(description.trim(), assetType, style || undefined);
      if (res?.error && /GEMINI_API_KEY/i.test(res.error)) {
        onApiKeyError();
      } else {
        onToast('Asset generation started', 'info');
        onRefresh();
        onClose();
      }
    } catch (err: any) {
      if (err?.message && /GEMINI_API_KEY/i.test(err.message)) {
        onApiKeyError();
      } else {
        onToast('Generation failed', 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Generate Asset</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="modal-field">
            <label className="modal-label">Description</label>
            <textarea
              className="modal-textarea"
              placeholder="A warrior with golden armor, holding a sword..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={3}
              disabled={loading}
            />
          </div>

          <div className="modal-row">
            <div className="modal-field">
              <label className="modal-label">Asset Type</label>
              <select
                className="modal-select"
                value={assetType}
                onChange={(e) => setAssetType(e.target.value)}
                disabled={loading}
              >
                {ASSET_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t.charAt(0).toUpperCase() + t.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="modal-field">
              <label className="modal-label">Style Override</label>
              <select
                className="modal-select"
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                disabled={loading}
              >
                {STYLES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="modal-btn modal-btn--secondary" onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button
            className="modal-btn modal-btn--primary"
            onClick={handleGenerate}
            disabled={loading || !description.trim()}
          >
            {loading ? (
              <span className="modal-btn__loading">
                <span className="modal-spinner" />
                Generating...
              </span>
            ) : (
              'Generate'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GeneratePanel;
