import { useState, useEffect, useCallback, useRef } from 'react';
import type { Asset } from './api';
import { api } from './api';
import AssetCard from './components/AssetCard';
import FilterBar from './components/FilterBar';
import ActionPanel from './components/ActionPanel';
import DetailPanel from './components/DetailPanel';
import ProgressBar from './components/ProgressBar';
import StatsPanel from './components/StatsPanel';
import UploadPanel from './components/UploadPanel';
import GeneratePanel from './components/GeneratePanel';
import ApiKeyModal from './components/ApiKeyModal';
import { useWebSocket } from './hooks/useWebSocket';
import './App.css';

interface Toast {
  id: number;
  message: string;
  kind: 'info' | 'success' | 'error';
}

interface ProgressItem {
  type: string;
  required: number;
  completed: number;
  label?: string;
}

let toastIdCounter = 0;

function App() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeType, setActiveType] = useState('all');
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('time');
  const [selectedNames, setSelectedNames] = useState<Set<string>>(new Set());
  const [tagFilter, setTagFilter] = useState('');
  const [detailAsset, setDetailAsset] = useState<Asset | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [progressItems, setProgressItems] = useState<ProgressItem[]>([]);
  const [showUpload, setShowUpload] = useState(false);
  const [showGenerate, setShowGenerate] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const addToast = useCallback((message: string, kind: 'info' | 'success' | 'error') => {
    const id = ++toastIdCounter;
    setToasts((prev) => [...prev, { id, message, kind }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const fetchAssets = useCallback(async (type: string, searchVal: string, sortVal: string) => {
    setLoading(true);
    try {
      const data = await api.getAssets(
        type === 'all' ? undefined : type,
        searchVal || undefined,
        sortVal
      );
      const list = Array.isArray(data) ? data : (data?.assets ?? []);
      setAssets(list);
    } catch {
      addToast('Failed to load assets', 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  const fetchProgress = useCallback(async () => {
    try {
      const data = await api.getProgress();
      if (Array.isArray(data)) {
        setProgressItems(data);
      } else if (data && typeof data === 'object') {
        // API format: { configured: bool, has_requirements: bool, progress: { characters: {total, done}, ... } }
        const progressMap: Record<string, any> = data.progress ?? data;
        const boolKeys = new Set(['configured', 'has_requirements']);
        const items: ProgressItem[] = Object.entries(progressMap)
          .filter(([key]) => !boolKeys.has(key))
          .map(([type, val]: [string, any]) => {
            if (val && typeof val === 'object') {
              const total = val.total ?? val.required ?? 0;
              const done = val.done ?? val.completed ?? 0;
              const label = type.charAt(0).toUpperCase() + type.slice(1);
              return { type, required: total, completed: done, label };
            }
            return null;
          })
          .filter(Boolean) as ProgressItem[];
        setProgressItems(items);
      }
    } catch {
      // Progress endpoint optional
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchAssets(activeType, search, sort);
    fetchProgress();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Re-fetch when filters change (debounce search)
  useEffect(() => {
    if (searchTimer.current) clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(() => {
      fetchAssets(activeType, search, sort);
    }, 300);
    return () => {
      if (searchTimer.current) clearTimeout(searchTimer.current);
    };
  }, [activeType, search, sort, fetchAssets]);

  const refresh = useCallback(() => {
    fetchAssets(activeType, search, sort);
    fetchProgress();
  }, [fetchAssets, fetchProgress, activeType, search, sort]);

  useWebSocket({ onRefresh: refresh, onToast: addToast });

  // Selection helpers
  const toggleSelect = useCallback((asset: Asset) => {
    setSelectedNames((prev) => {
      const next = new Set(prev);
      if (next.has(asset.name)) {
        next.delete(asset.name);
      } else {
        next.add(asset.name);
      }
      return next;
    });
  }, []);

  const openDetail = useCallback((asset: Asset) => {
    setDetailAsset(asset);
  }, []);

  // Apply tag filter client-side (tag filter is purely frontend)
  const filteredAssets = tagFilter
    ? assets.filter((a) => (a.tags ?? []).some((t) => t.toLowerCase().includes(tagFilter.toLowerCase())))
    : assets;

  const selectedAssets = filteredAssets.filter((a) => selectedNames.has(a.name));

  return (
    <div className="app">
      {/* Top bar */}
      <header className="topbar">
        <div className="topbar__brand">
          <span className="topbar__icon">🎮</span>
          <span className="topbar__title">Game Asset Manager</span>
        </div>
        <div className="topbar__progress">
          <ProgressBar items={progressItems} />
        </div>
        <div className="topbar__actions">
          <button className="topbar__btn topbar__btn--upload" onClick={() => setShowUpload(true)}>
            Upload
          </button>
          <button className="topbar__btn topbar__btn--generate" onClick={() => setShowGenerate(true)}>
            Generate
          </button>
          <button className="topbar__refresh" onClick={refresh} title="Refresh">
            ↺
          </button>
        </div>
      </header>

      {/* Filter bar */}
      <FilterBar
        activeType={activeType}
        search={search}
        sort={sort}
        tagFilter={tagFilter}
        totalCount={filteredAssets.length}
        selectedCount={selectedNames.size}
        onTypeChange={(t) => {
          setActiveType(t);
          setSelectedNames(new Set());
        }}
        onSearchChange={setSearch}
        onSortChange={setSort}
        onTagFilterChange={setTagFilter}
        onSelectAll={() => setSelectedNames(new Set(filteredAssets.map((a) => a.name)))}
        onDeselectAll={() => setSelectedNames(new Set())}
      />

      {/* Stats panel */}
      <StatsPanel assets={assets} />

      {/* Main area */}
      <div className="main-area">
        <div className={`asset-grid-wrap${detailAsset ? ' with-detail' : ''}`}>
          {loading ? (
            <div className="loading-state">
              <div className="spinner" />
              <span>Loading assets...</span>
            </div>
          ) : filteredAssets.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state__icon">📦</div>
              <div>No assets found</div>
            </div>
          ) : (
            <div className="asset-grid">
              {filteredAssets.map((asset) => (
                <AssetCard
                  key={asset.name}
                  asset={asset}
                  selected={selectedNames.has(asset.name)}
                  onClick={toggleSelect}
                  onDoubleClick={openDetail}
                />
              ))}
            </div>
          )}
        </div>

        {/* Detail panel */}
        {detailAsset && (
          <DetailPanel
            asset={detailAsset}
            onClose={() => setDetailAsset(null)}
            onRefresh={refresh}
            onToast={addToast}
          />
        )}
      </div>

      {/* Action panel (bottom) */}
      <ActionPanel
        selected={selectedAssets}
        onRefresh={refresh}
        onToast={addToast}
        onClearSelection={() => setSelectedNames(new Set())}
      />

      {/* Modals */}
      {showUpload && (
        <UploadPanel
          onClose={() => setShowUpload(false)}
          onToast={addToast}
          onRefresh={refresh}
        />
      )}
      {showGenerate && (
        <GeneratePanel
          onClose={() => setShowGenerate(false)}
          onToast={addToast}
          onRefresh={refresh}
          onApiKeyError={() => setShowApiKey(true)}
        />
      )}
      {showApiKey && (
        <ApiKeyModal onClose={() => setShowApiKey(false)} />
      )}

      {/* Toast notifications */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast--${t.kind}`}>
            {t.message}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
