import React, { useRef, useEffect, useState, useCallback } from 'react';

export interface BboxItem {
  name: string;
  bbox: [number, number, number, number]; // [left, top, right, bottom]
  color?: string;
}

interface BboxEditorProps {
  imageUrl: string;
  items: BboxItem[];
  onChange: (items: BboxItem[]) => void;
}

// Colors for different boxes
const BOX_COLORS = [
  '#f0a030', '#4ac8e8', '#30d890', '#e85050', '#d050c0',
  '#a0c040', '#50a0e8', '#e8a050', '#50e8a0', '#e05090',
];

type Handle = 'move' | 'tl' | 'tr' | 'bl' | 'br' | 'l' | 'r' | 't' | 'b';

interface DragState {
  itemIdx: number;
  handle: Handle;
  startX: number;
  startY: number;
  startBbox: [number, number, number, number];
  scaleX: number;
  scaleY: number;
}

const HANDLE_SIZE = 8;
const MIN_BOX = 10;

function getHandleAtPoint(
  mx: number, my: number,
  bbox: [number, number, number, number],
  scaleX: number, scaleY: number,
): Handle | null {
  const [l, t, r, b] = bbox;
  const sl = l * scaleX, st = t * scaleY, sr = r * scaleX, sb = b * scaleY;
  const hs = HANDLE_SIZE / 2 + 3; // hit area

  // Corners
  if (Math.abs(mx - sl) <= hs && Math.abs(my - st) <= hs) return 'tl';
  if (Math.abs(mx - sr) <= hs && Math.abs(my - st) <= hs) return 'tr';
  if (Math.abs(mx - sl) <= hs && Math.abs(my - sb) <= hs) return 'bl';
  if (Math.abs(mx - sr) <= hs && Math.abs(my - sb) <= hs) return 'br';
  // Edges
  if (Math.abs(mx - sl) <= hs && my > st && my < sb) return 'l';
  if (Math.abs(mx - sr) <= hs && my > st && my < sb) return 'r';
  if (Math.abs(my - st) <= hs && mx > sl && mx < sr) return 't';
  if (Math.abs(my - sb) <= hs && mx > sl && mx < sr) return 'b';
  // Center (move) — inside box
  if (mx >= sl && mx <= sr && my >= st && my <= sb) return 'move';
  return null;
}

function getCursorForHandle(h: Handle | null): string {
  switch (h) {
    case 'tl': case 'br': return 'nwse-resize';
    case 'tr': case 'bl': return 'nesw-resize';
    case 'l': case 'r': return 'ew-resize';
    case 't': case 'b': return 'ns-resize';
    case 'move': return 'move';
    default: return 'default';
  }
}

const BboxEditor: React.FC<BboxEditorProps> = ({ imageUrl, items, onChange }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const [imgLoaded, setImgLoaded] = useState(false);
  const [imgNaturalW, setImgNaturalW] = useState(1);
  const [imgNaturalH, setImgNaturalH] = useState(1);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const [hoverHandle, setHoverHandle] = useState<Handle | null>(null);
  const dragRef = useRef<DragState | null>(null);

  // Load image
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      imgRef.current = img;
      setImgNaturalW(img.naturalWidth);
      setImgNaturalH(img.naturalHeight);
      setImgLoaded(true);
    };
    img.src = imageUrl;
    return () => { img.onload = null; };
  }, [imageUrl]);

  // Compute canvas display size
  const canvasW = 600;
  const canvasH = imgNaturalH > 0 ? Math.round(canvasW * imgNaturalH / imgNaturalW) : 400;
  const scaleX = imgNaturalW > 0 ? canvasW / imgNaturalW : 1;
  const scaleY = imgNaturalH > 0 ? canvasH / imgNaturalH : 1;

  // Draw everything
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvasW, canvasH);

    // Draw image
    if (imgRef.current && imgLoaded) {
      ctx.drawImage(imgRef.current, 0, 0, canvasW, canvasH);
    } else {
      ctx.fillStyle = '#12121e';
      ctx.fillRect(0, 0, canvasW, canvasH);
    }

    // Draw boxes
    items.forEach((item, idx) => {
      const color = item.color ?? BOX_COLORS[idx % BOX_COLORS.length];
      const [l, t, r, b] = item.bbox;
      const sl = l * scaleX, st = t * scaleY;
      const sw = (r - l) * scaleX, sh = (b - t) * scaleY;
      const isSelected = idx === selectedIdx;

      // Box fill
      ctx.fillStyle = color + '22';
      ctx.fillRect(sl, st, sw, sh);

      // Box stroke
      ctx.strokeStyle = color;
      ctx.lineWidth = isSelected ? 2 : 1;
      ctx.setLineDash(isSelected ? [] : [4, 3]);
      ctx.strokeRect(sl, st, sw, sh);
      ctx.setLineDash([]);

      // Label background
      const label = item.name;
      ctx.font = '11px JetBrains Mono, monospace';
      const textW = ctx.measureText(label).width;
      const labelX = sl;
      const labelY = Math.max(0, st - 18);
      ctx.fillStyle = color + 'cc';
      ctx.fillRect(labelX, labelY, textW + 8, 16);
      ctx.fillStyle = '#08080e';
      ctx.fillText(label, labelX + 4, labelY + 11);

      // Handles (only on selected)
      if (isSelected) {
        const handles: Array<[number, number]> = [
          [sl, st], [sl + sw, st], [sl, st + sh], [sl + sw, st + sh],
          [sl, st + sh / 2], [sl + sw, st + sh / 2],
          [sl + sw / 2, st], [sl + sw / 2, st + sh],
        ];
        handles.forEach(([hx, hy]) => {
          ctx.fillStyle = '#08080e';
          ctx.fillRect(hx - HANDLE_SIZE / 2, hy - HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE);
          ctx.strokeStyle = color;
          ctx.lineWidth = 1.5;
          ctx.strokeRect(hx - HANDLE_SIZE / 2, hy - HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE);
        });
      }
    });
  }, [items, selectedIdx, canvasW, canvasH, scaleX, scaleY, imgLoaded]);

  useEffect(() => {
    draw();
  }, [draw]);

  const getPos = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current!.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left) * (canvasW / rect.width),
      y: (e.clientY - rect.top) * (canvasH / rect.height),
    };
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getPos(e);

    // Check selected item first (handles)
    if (selectedIdx !== null) {
      const item = items[selectedIdx];
      const h = getHandleAtPoint(x, y, item.bbox, scaleX, scaleY);
      if (h) {
        dragRef.current = {
          itemIdx: selectedIdx,
          handle: h,
          startX: x,
          startY: y,
          startBbox: [...item.bbox] as [number, number, number, number],
          scaleX,
          scaleY,
        };
        return;
      }
    }

    // Check all items for click (reverse order = top layer first)
    for (let i = items.length - 1; i >= 0; i--) {
      const item = items[i];
      const h = getHandleAtPoint(x, y, item.bbox, scaleX, scaleY);
      if (h) {
        setSelectedIdx(i);
        dragRef.current = {
          itemIdx: i,
          handle: h,
          startX: x,
          startY: y,
          startBbox: [...item.bbox] as [number, number, number, number],
          scaleX,
          scaleY,
        };
        return;
      }
    }

    // Click on empty space — deselect
    setSelectedIdx(null);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getPos(e);

    // Update hover cursor
    if (!dragRef.current) {
      let found: Handle | null = null;
      const checkIdx = selectedIdx !== null ? selectedIdx : -1;
      if (checkIdx >= 0) {
        found = getHandleAtPoint(x, y, items[checkIdx].bbox, scaleX, scaleY);
      }
      if (!found) {
        for (let i = items.length - 1; i >= 0; i--) {
          const h = getHandleAtPoint(x, y, items[i].bbox, scaleX, scaleY);
          if (h) { found = h; break; }
        }
      }
      setHoverHandle(found);
      return;
    }

    // Dragging
    const drag = dragRef.current;
    const dx = (x - drag.startX) / drag.scaleX;
    const dy = (y - drag.startY) / drag.scaleY;
    const [ol, ot, or_, ob] = drag.startBbox;
    let [nl, nt, nr, nb] = [ol, ot, or_, ob];

    switch (drag.handle) {
      case 'move':
        nl = ol + dx; nt = ot + dy; nr = or_ + dx; nb = ob + dy;
        break;
      case 'tl': nl = Math.min(ol + dx, or_ - MIN_BOX); nt = Math.min(ot + dy, ob - MIN_BOX); break;
      case 'tr': nr = Math.max(or_ + dx, ol + MIN_BOX); nt = Math.min(ot + dy, ob - MIN_BOX); break;
      case 'bl': nl = Math.min(ol + dx, or_ - MIN_BOX); nb = Math.max(ob + dy, ot + MIN_BOX); break;
      case 'br': nr = Math.max(or_ + dx, ol + MIN_BOX); nb = Math.max(ob + dy, ot + MIN_BOX); break;
      case 'l':  nl = Math.min(ol + dx, or_ - MIN_BOX); break;
      case 'r':  nr = Math.max(or_ + dx, ol + MIN_BOX); break;
      case 't':  nt = Math.min(ot + dy, ob - MIN_BOX); break;
      case 'b':  nb = Math.max(ob + dy, ot + MIN_BOX); break;
    }

    // Clamp to image bounds
    const iw = imgNaturalW, ih = imgNaturalH;
    nl = Math.max(0, nl); nt = Math.max(0, nt);
    nr = Math.min(iw, nr); nb = Math.min(ih, nb);

    const updated = items.map((item, idx) =>
      idx === drag.itemIdx
        ? { ...item, bbox: [Math.round(nl), Math.round(nt), Math.round(nr), Math.round(nb)] as [number, number, number, number] }
        : item
    );
    onChange(updated);
  };

  const handleMouseUp = () => {
    dragRef.current = null;
  };

  return (
    <div className="bbox-editor-canvas">
      <canvas
        ref={canvasRef}
        width={canvasW}
        height={canvasH}
        style={{ cursor: getCursorForHandle(hoverHandle), maxWidth: '100%' }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      />
      {selectedIdx !== null && items[selectedIdx] && (
        <div className="bbox-editor-canvas__info">
          <span className="bbox-editor-canvas__sel-name">{items[selectedIdx].name}</span>
          <span className="bbox-editor-canvas__coords">
            L:{items[selectedIdx].bbox[0]}
            &nbsp;T:{items[selectedIdx].bbox[1]}
            &nbsp;R:{items[selectedIdx].bbox[2]}
            &nbsp;B:{items[selectedIdx].bbox[3]}
          </span>
        </div>
      )}
    </div>
  );
};

export default BboxEditor;
