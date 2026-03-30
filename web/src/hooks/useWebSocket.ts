import { useEffect, useRef, useCallback } from 'react';

export interface WsMessage {
  type: 'task_start' | 'task_complete' | 'task_error' | 'asset_updated' | string;
  message?: string;
  asset?: string;
  [key: string]: any;
}

interface UseWebSocketOptions {
  onRefresh: () => void;
  onToast: (msg: string, kind: 'info' | 'success' | 'error') => void;
}

export function useWebSocket({ onRefresh, onToast }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    try {
      const ws = new WebSocket('ws://localhost:8080/ws');
      wsRef.current = ws;

      ws.onopen = () => {
        // Connection established silently
      };

      ws.onmessage = (event) => {
        try {
          const data: WsMessage = JSON.parse(event.data);

          if (data.type === 'task_start') {
            onToast(data.message ?? 'Task started', 'info');
          } else if (data.type === 'task_complete') {
            onToast(data.message ?? 'Task completed', 'success');
            onRefresh();
          } else if (data.type === 'task_error') {
            onToast(data.message ?? 'Task failed', 'error');
          } else if (data.type === 'asset_updated') {
            onRefresh();
          }
        } catch {
          // Ignore non-JSON messages
        }
      };

      ws.onclose = () => {
        if (mountedRef.current) {
          // Reconnect after 3 seconds
          reconnectTimer.current = setTimeout(connect, 3000);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      // WebSocket unavailable, retry later
      if (mountedRef.current) {
        reconnectTimer.current = setTimeout(connect, 5000);
      }
    }
  }, [onRefresh, onToast]);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
    };
  }, [connect]);
}
