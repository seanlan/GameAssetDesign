import React, { useState, useRef, useCallback } from 'react';
import { api } from '../api';

const BASE_URL = 'http://localhost:8080';

interface UploadPanelProps {
  onClose: () => void;
  onToast: (msg: string, kind: 'info' | 'success' | 'error') => void;
  onRefresh: () => void;
}

const UploadPanel: React.FC<UploadPanelProps> = ({ onClose, onToast, onRefresh }) => {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [annotatedUrl, setAnnotatedUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [designId, setDesignId] = useState<string | undefined>(undefined);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    setAnnotatedUrl(null);
    setDesignId(undefined);
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
      if (res.annotated_url) {
        setAnnotatedUrl(`${BASE_URL}${res.annotated_url}`);
      } else if (res.preview_url) {
        setAnnotatedUrl(`${BASE_URL}${res.preview_url}`);
      }
      if (res.design_id) setDesignId(res.design_id);
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

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Upload Design Image</span>
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
                <span className="upload-dropzone__text">Drop image here or click to browse</span>
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
        </div>

        <div className="modal-footer">
          <button
            className="modal-btn modal-btn--secondary"
            onClick={handleAnalyze}
            disabled={!file || analyzing}
          >
            {analyzing ? 'Analyzing...' : 'Analyze'}
          </button>
          <button
            className="modal-btn modal-btn--primary"
            onClick={handleExtract}
            disabled={extracting || (!annotatedUrl && !file)}
          >
            {extracting ? 'Extracting...' : 'Extract Assets'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadPanel;
