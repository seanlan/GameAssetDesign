import React, { useState } from 'react';

interface CompareViewProps {
  beforeUrl: string;
  afterUrl: string;
  onClose: () => void;
}

const CompareView: React.FC<CompareViewProps> = ({ beforeUrl, afterUrl, onClose }) => {
  const [position, setPosition] = useState(50); // percentage

  return (
    <div className="compare-view">
      <div className="compare-view__header">
        <span className="compare-view__title">Before / After</span>
        <button className="compare-view__close" onClick={onClose}>✕</button>
      </div>
      <div
        className="compare-view__body"
        onMouseMove={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          setPosition(Math.min(100, Math.max(0, ((e.clientX - rect.left) / rect.width) * 100)));
        }}
      >
        <img src={beforeUrl} className="compare-img compare-img--before" alt="Before" />
        <img
          src={afterUrl}
          className="compare-img compare-img--after"
          alt="After"
          style={{ clipPath: `inset(0 0 0 ${position}%)` }}
        />
        <div className="compare-slider" style={{ left: `${position}%` }}>
          <div className="compare-slider__line" />
          <div className="compare-slider__handle">
            <span>&#9664;</span>
            <span>&#9654;</span>
          </div>
        </div>
        <div className="compare-label compare-label--before">Before</div>
        <div className="compare-label compare-label--after">After</div>
      </div>
    </div>
  );
};

export default CompareView;
