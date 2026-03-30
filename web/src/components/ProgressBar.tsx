import React from 'react';

interface ProgressItem {
  type: string;
  required: number;
  completed: number;
  label?: string;
}

interface ProgressBarProps {
  items: ProgressItem[];
}

const ProgressBar: React.FC<ProgressBarProps> = ({ items }) => {
  if (!items || items.length === 0) return null;

  return (
    <div className="progress-bars">
      {items.map((item) => {
        const pct = item.required > 0
          ? Math.min(100, Math.round((item.completed / item.required) * 100))
          : 0;
        const done = item.completed >= item.required;

        return (
          <div key={item.type} className="progress-item">
            <div className="progress-item__label">
              <span>{item.label ?? item.type}</span>
              <span className={`progress-item__fraction ${done ? 'done' : ''}`}>
                {item.completed}/{item.required}
              </span>
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${done ? 'done' : ''}`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ProgressBar;
