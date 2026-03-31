import { useState, useEffect, useCallback, useRef } from 'react';
import type { Asset } from './api';
import { api } from './api';
import AssetCard from './components/AssetCard';
import FilterBar from './components/FilterBar';
import ActionPanel from './components/ActionPanel';
import DetailPanel from './components/DetailPanel';
import ProgressBar from './components/ProgressBar';
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
  const [detailAsset, setDetailAsset] = useState<Asset | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [progressItems, setProgressItems] = useState<ProgressItem[]>([]);
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
        // Support object format: { character: { required: 5, completed: 3 }, ... }
        const items: ProgressItem[] = Object.entries(data).map(([type, val]: [string, any]) => ({
          type,
          required: val.required ?? 0,
          completed: val.completed ?? 0,
          label: val.label,
        }));
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

  const selectedAssets = assets.filter((a) => selectedNames.has(a.name));

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
        totalCount={assets.length}
        selectedCount={selectedNames.size}
        onTypeChange={(t) => {
          setActiveType(t);
          setSelectedNames(new Set());
        }}
        onSearchChange={setSearch}
        onSortChange={setSort}
        onSelectAll={() => setSelectedNames(new Set(assets.map((a) => a.name)))}
        onDeselectAll={() => setSelectedNames(new Set())}
      />

      {/* Main area */}
      <div className="main-area">
        <div className={`asset-grid-wrap${detailAsset ? ' with-detail' : ''}`}>
          {loading ? (
            <div className="loading-state">
              <div className="spinner" />
              <span>Loading assets...</span>
            </div>
          ) : assets.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state__icon">📦</div>
              <div>No assets found</div>
            </div>
          ) : (
            <div className="asset-grid">
              {assets.map((asset) => (
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
