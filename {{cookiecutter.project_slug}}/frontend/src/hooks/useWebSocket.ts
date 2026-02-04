/**
 * useWebSocket Hook
 *
 * React hook for managing WebSocket connections and subscriptions.
 * Handles connection lifecycle, automatic cleanup, and message handling.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import websocketService, { WebSocketCallback } from '../services/websocket';
import { WebSocketMessage } from '../types/projectmaker';

interface UseWebSocketOptions {
  projectId?: number;
  channelId?: string;
  agentId?: string;
  conversationId?: number;
  autoConnect?: boolean;
  onMessage?: (message: WebSocketMessage) => void;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  subscribe: (params: { projectId?: number; channelId?: string; agentId?: string; conversationId?: number }) => void;
  unsubscribe: (params: { projectId?: number; channelId?: string; agentId?: string; conversationId?: number }) => void;
}

/**
 * Hook for using WebSocket in React components
 *
 * @param options - Configuration options
 * @returns WebSocket connection interface
 *
 * @example
 * ```tsx
 * const { isConnected, sendMessage } = useWebSocket({
 *   projectId: 123,
 *   autoConnect: true,
 *   onMessage: (msg) => console.log('Received:', msg)
 * });
 * ```
 */
export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    projectId,
    channelId,
    agentId,
    conversationId,
    autoConnect = true,
    onMessage
  } = options;

  const [isConnected, setIsConnected] = useState(websocketService.isConnected());
  const messageCallbackRef = useRef<WebSocketCallback | null>(null);
  const statusCallbackRef = useRef<((connected: boolean) => void) | null>(null);
  const unsubscribeMessageRef = useRef<(() => void) | null>(null);
  const unsubscribeStatusRef = useRef<(() => void) | null>(null);

  // Connect to WebSocket
  const connect = useCallback(() => {
    websocketService.connect();
  }, []);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    websocketService.disconnect();
  }, []);

  // Send message
  const sendMessage = useCallback((message: any) => {
    websocketService.send(message);
  }, []);

  // Subscribe to updates
  const subscribe = useCallback((params: {
    projectId?: number;
    channelId?: string;
    agentId?: string;
    conversationId?: number;
  }) => {
    websocketService.subscribe({
      action: 'subscribe',
      project_id: params.projectId,
      channel_id: params.channelId,
      agent_id: params.agentId,
      conversation_id: params.conversationId,
    });
  }, []);

  // Unsubscribe from updates
  const unsubscribe = useCallback((params: {
    projectId?: number;
    channelId?: string;
    agentId?: string;
    conversationId?: number;
  }) => {
    websocketService.unsubscribe({
      project_id: params.projectId,
      channel_id: params.channelId,
      agent_id: params.agentId,
      conversation_id: params.conversationId,
    });
  }, []);

  // Set up message callback
  useEffect(() => {
    if (onMessage) {
      messageCallbackRef.current = onMessage;
      unsubscribeMessageRef.current = websocketService.onMessage(onMessage);
    }

    return () => {
      if (unsubscribeMessageRef.current) {
        unsubscribeMessageRef.current();
        unsubscribeMessageRef.current = null;
      }
    };
  }, [onMessage]);

  // Set up connection status callback
  useEffect(() => {
    statusCallbackRef.current = setIsConnected;
    unsubscribeStatusRef.current = websocketService.onConnectionStatus(setIsConnected);

    return () => {
      if (unsubscribeStatusRef.current) {
        unsubscribeStatusRef.current();
        unsubscribeStatusRef.current = null;
      }
    };
  }, []);

  // Auto-connect and subscribe
  useEffect(() => {
    if (autoConnect) {
      connect();

      // Auto-subscribe if project/channel/agent/conversation IDs provided
      if (projectId || channelId || agentId || conversationId) {
        // Wait a bit for connection to establish
        const subscribeTimer = setTimeout(() => {
          subscribe({ projectId, channelId, agentId, conversationId });
        }, 500);

        return () => {
          clearTimeout(subscribeTimer);
          // Unsubscribe on unmount
          if (projectId || channelId || agentId || conversationId) {
            unsubscribe({ projectId, channelId, agentId, conversationId });
          }
        };
      }
    }
  }, [autoConnect, projectId, channelId, agentId, conversationId, connect, subscribe, unsubscribe]);

  return {
    isConnected,
    connect,
    disconnect,
    sendMessage,
    subscribe,
    unsubscribe,
  };
}

export default useWebSocket;
