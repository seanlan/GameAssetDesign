import React, { useState, useRef, useCallback } from 'react';
import { api } from '../api';
import BboxEditor from './BboxEditor';
import type { BboxItem } from './BboxEditor';
import { t, useLang } from '../i18n';

const BASE_URL = 'http://localhost:8080';

interface UploadPanelProps {
  onClose: () => void;
  onToast: (msg: string, kind: 'info' | 'success' | 'error') => void;
  onRefresh: () => void;
}

interface ElementEntry {
  name: string;
  type: string;
  bbox: [number, number, number, number];
  needs_remove_bg?: boolean;
}

interface ElementsData {
  source: string;
  source_size: [number, number];
  layers: {
    bottom: ElementEntry[];
    middle: ElementEntry[];
    top: ElementEntry[];
  };
  shared_assets: any[];
  [key: string]: any;
}

const ELEMENT_TYPES = ['background', 'character', 'icon', 'ui', 'other'];
const LAYERS = ['bottom', 'middle', 'top'] as const;
type LayerKey = typeof LAYERS[number];

const UploadPanel: React.FC<UploadPanelProps> = ({ onClose, onToast, onRefresh }) => {
  useLang();
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [annotatedUrl, setAnnotatedUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [designId, setDesignId] = useState<string | undefined>(undefined);
  const [elements, setElements] = useState<ElementsData | null>(null);
  const [elementsPath, setElementsPath] = useState<string | null>(null);
  const [savingElements, setSavingElements] = useState(false);
  const [visualEditor, setVisualEditor] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    setAnnotatedUrl(null);
    setDesignId(undefined);
    setElements(null);
    setElementsPath(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreviewUrl(e.target?.result as string);
    reader.readAsDataURL(f);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const f = e.dataTransfer.files[0];
      if (f && f.type.startsWith('image/')) handleFile(f);
    },
    [handleFile]
  );

  const handleAnalyze = async () => {
    if (!file) return;
    setAnalyzing(true);
    try {
      const res = await api.analyzeDesign(file);
      if (res.annotated_image) {
        setAnnotatedUrl(`${BASE_URL}${res.annotated_image}?t=${Date.now()}`);
      } else if (res.annotated_url) {
        setAnnotatedUrl(`${BASE_URL}${res.annotated_url}?t=${Date.now()}`);
      } else if (res.preview_url) {
        setAnnotatedUrl(`${BASE_URL}${res.preview_url}?t=${Date.now()}`);
      }
      if (res.design_id) setDesignId(res.design_id);
      if (res.elements) setElements(res.elements);
      if (res.elements_path) setElementsPath(res.elements_path);
      onToast('Design analyzed successfully', 'success');
    } catch {
      onToast('Analysis failed', 'error');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleExtract = async () => {
    setExtracting(true);
    try {
      await api.extractAssets(designId);
      onToast('Extraction started', 'info');
      onRefresh();
      onClose();
    } catch {
      onToast('Extraction failed', 'error');
    } finally {
      setExtracting(false);
    }
  };

  const handleQuickPipeline = async () => {
    if (!file) return;
    setExtracting(true);
    try {
      const res = await api.runPipeline(file);
      if (res.annotated_url) {
        setAnnotatedUrl(`${BASE_URL}${res.annotated_url}?t=${Date.now()}`);
      }
      onToast(`Pipeline complete: ${res.total} assets extracted`, 'success');
      onRefresh();
    } catch {
      onToast('Pipeline failed', 'error');
    } finally {
      setExtracting(false);
    }
  };

  // --- Element editing helpers ---

  const updateElement = (layer: LayerKey, idx: number, patch: Partial<ElementEntry>) => {
    if (!elements) return;
    setElements((prev) => {
      if (!prev) return prev;
      const updated = { ...prev, layers: { ...prev.layers } };
      updated.layers[layer] = prev.layers[layer].map((e, i) =>
        i === idx ? { ...e, ...patch } : e
      );
      return updated;
    });
  };

  const updateBbox = (layer: LayerKey, idx: number, bboxIdx: number, value: string) => {
    if (!elements) return;
    const elem = elements.layers[layer][idx];
    const newBbox = [...elem.bbox] as [number, number, number, number];
    newBbox[bboxIdx] = parseInt(value, 10) || 0;
    updateElement(layer, idx, { bbox: newBbox });
  };

  const deleteElement = (layer: LayerKey, idx: number) => {
    if (!elements) return;
    setElements((prev) => {
      if (!prev) return prev;
      const updated = { ...prev, layers: { ...prev.layers } };
      updated.layers[layer] = prev.layers[layer].filter((_, i) => i !== idx);
      return updated;
    });
  };

  const addElement = (layer: LayerKey) => {
    if (!elements) return;
    const newElem: ElementEntry = {
      name: `element_${Date.now()}`,
      type: 'ui',
      bbox: [0, 0, 100, 100],
      needs_remove_bg: false,
    };
    setElements((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        layers: {
          ...prev.layers,
          [layer]: [...prev.layers[layer], newElem],
        },
      };
    });
  };

  // Build flat list for BboxEditor
  const allBboxItems: BboxItem[] = elements
    ? LAYERS.flatMap((layer) =>
        (elements.layers[layer] ?? []).map((e) => ({
          name: `${layer}/${e.name}`,
          bbox: e.bbox,
        }))
      )
    : [];

  const handleBboxChange = (updated: BboxItem[]) => {
    if (!elements) return;
    // Rebuild layers from flat list
    let flatIdx = 0;
    setElements((prev) => {
      if (!prev) return prev;
      const newLayers = { ...prev.layers };
      LAYERS.forEach((layer) => {
        newLayers[layer] = (prev.layers[layer] ?? []).map((e) => {
          const item = updated[flatIdx++];
          return item ? { ...e, bbox: item.bbox } : e;
        });
      });
      return { ...prev, layers: newLayers };
    });
  };

  const handleSaveAndReannotate = async () => {
    if (!elements) return;
    setSavingElements(true);
    try {
      const saveRes = await api.saveElements(elements);
      const savedPath = saveRes.saved || elementsPath;

      // Re-annotate to refresh preview
      if (savedPath && elements.source) {
        const annRes = await api.annotateImage(elements.source, savedPath);
        if (annRes.annotated_url) {
          setAnnotatedUrl(`${BASE_URL}${annRes.annotated_url}?t=${Date.now()}`);
        }
      }
      onToast('Elements saved', 'success');
    } catch {
      onToast('Save failed', 'error');
    } finally {
      setSavingElements(false);
    }
  };

  const totalElements = elements
    ? LAYERS.reduce((sum, l) => sum + (elements.layers[l]?.length ?? 0), 0)
    : 0;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel modal-panel--wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">{t('upload.title')}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Drop zone */}
          <div
            className={`upload-dropzone${dragging ? ' upload-dropzone--active' : ''}${file ? ' upload-dropzone--has-file' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
            />
            {file ? (
              <span className="upload-dropzone__filename">{file.name}</span>
            ) : (
              <>
                <span className="upload-dropzone__icon">⬆</span>
                <span className="upload-dropzone__text">{t('upload.dragDrop')}</span>
              </>
            )}
          </div>

          {/* Preview images */}
          {(previewUrl || annotatedUrl) && (
            <div className="upload-previews">
              {previewUrl && (
                <div className="upload-preview">
                  <div className="upload-preview__label">Original</div>
                  <img src={previewUrl} alt="Original" />
                </div>
              )}
              {annotatedUrl && (
                <div className="upload-preview">
                  <div className="upload-preview__label">Annotated</div>
                  <img src={annotatedUrl} alt="Annotated" />
                </div>
              )}
            </div>
          )}

          {/* BBox editor — shown after analysis */}
          {elements && (
            <div className="bbox-editor">
              <div className="bbox-editor__header">
                <span className="bbox-editor__title">
                  {t('upload.detected')} ({totalElements})
                </span>
                <div className="bbox-editor__header-actions">
                  {annotatedUrl && (
                    <button
                      className={`bbox-editor__toggle-btn${visualEditor ? ' active' : ''}`}
                      onClick={() => setVisualEditor((v) => !v)}
                      title="Toggle visual bbox editor"
                    >
                      {visualEditor ? t('upload.numeric') : t('upload.visual')}
                    </button>
                  )}
                  <button
                    className="bbox-editor__save-btn"
                    onClick={handleSaveAndReannotate}
                    disabled={savingElements}
                  >
                    {savingElements ? t('upload.saving') : t('upload.save')}
                  </button>
                </div>
              </div>

              {/* Visual canvas editor */}
              {visualEditor && annotatedUrl && (
                <BboxEditor
                  imageUrl={annotatedUrl}
                  items={allBboxItems}
                  onChange={handleBboxChange}
                />
              )}

              {/* Numeric editor — hidden in visual mode */}
              {!visualEditor && LAYERS.map((layer) => {
                const layerElems = elements.layers[layer] ?? [];
                return (
                  <div key={layer} className="bbox-layer">
                    <div className="bbox-layer__title">
                      {t('upload.layer')}: <strong>{layer}</strong> ({layerElems.length})
                    </div>

                    {layerElems.map((elem, idx) => (
                      <div key={idx} className="bbox-row">
                        {/* Name */}
                        <input
                          className="bbox-row__name"
                          value={elem.name}
                          placeholder="name"
                          onChange={(e) => updateElement(layer, idx, { name: e.target.value })}
                        />

                        {/* Type */}
                        <select
                          className="bbox-row__type"
                          value={elem.type}
                          onChange={(e) => updateElement(layer, idx, { type: e.target.value })}
                        >
                          {ELEMENT_TYPES.map((t) => (
                            <option key={t} value={t}>{t}</option>
                          ))}
                        </select>

                        {/* BBox inputs: left top right bottom */}
                        <span className="bbox-row__label">L</span>
                        <input
                          className="bbox-row__coord"
                          type="number"
                          value={elem.bbox[0]}
                          onChange={(e) => updateBbox(layer, idx, 0, e.target.value)}
                        />
                        <span className="bbox-row__label">T</span>
                        <input
                          className="bbox-row__coord"
                          type="number"
                          value={elem.bbox[1]}
                          onChange={(e) => updateBbox(layer, idx, 1, e.target.value)}
                        />
                        <span className="bbox-row__label">R</span>
                        <input
                          className="bbox-row__coord"
                          type="number"
                          value={elem.bbox[2]}
                          onChange={(e) => updateBbox(layer, idx, 2, e.target.value)}
                        />
                        <span className="bbox-row__label">B</span>
                        <input
                          className="bbox-row__coord"
                          type="number"
                          value={elem.bbox[3]}
                          onChange={(e) => updateBbox(layer, idx, 3, e.target.value)}
                        />

                        {/* Delete */}
                        <button
                          className="bbox-row__delete"
                          title="Delete element"
                          onClick={() => deleteElement(layer, idx)}
                        >
                          ✕
                        </button>
                      </div>
                    ))}

                    {/* Add element to this layer */}
                    <button
                      className="bbox-layer__add-btn"
                      onClick={() => addElement(layer)}
                    >
                      + {t('upload.addElement')} {layer}
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button
            className="modal-btn modal-btn--accent"
            onClick={handleQuickPipeline}
            disabled={!file || extracting}
            title="Auto-detect → extract → chromakey → trim (one step)"
          >
            {extracting ? t('upload.processing') : t('upload.quickExtract')}
          </button>
          <button
            className="modal-btn modal-btn--secondary"
            onClick={handleAnalyze}
            disabled={!file || analyzing}
          >
            {analyzing ? t('upload.analyzing') : t('upload.analyze')}
          </button>
          <button
            className="modal-btn modal-btn--primary"
            onClick={handleExtract}
            disabled={extracting || (!annotatedUrl && !file)}
          >
            {extracting ? t('upload.extracting') : t('upload.extract')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadPanel;
