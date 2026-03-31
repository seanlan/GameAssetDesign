import React from 'react';
import { t, useLang } from '../i18n';

interface ApiKeyModalProps {
  onClose: () => void;
}

const ApiKeyModal: React.FC<ApiKeyModalProps> = ({ onClose }) => {
  useLang();
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel modal-panel--narrow" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">{t('apikey.title')}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <p className="modal-text">
            The <code className="modal-code">GEMINI_API_KEY</code> environment variable is not set.
            The server cannot generate images without it.
          </p>

          <div className="modal-steps">
            <div className="modal-step">
              <span className="modal-step__num">1</span>
              <span>Get a Gemini API key from <strong>Google AI Studio</strong> (aistudio.google.com)</span>
            </div>
            <div className="modal-step">
              <span className="modal-step__num">2</span>
              <span>Stop the server, then restart it with:</span>
            </div>
          </div>

          <div className="modal-code-block">
            <code>GEMINI_API_KEY=your_key_here python3 server.py</code>
          </div>

          <p className="modal-text modal-text--dim">
            Or export it in your shell before running the server:
          </p>

          <div className="modal-code-block">
            <code>export GEMINI_API_KEY=your_key_here</code>
          </div>
        </div>

        <div className="modal-footer">
          <button className="modal-btn modal-btn--primary" onClick={onClose}>
            {t('apikey.dismiss')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApiKeyModal;
