/**
 * useFunctionCallNotifications Hook
 *
 * Listens for real-time function call notifications via WebSocket
 * and displays them as toast notifications.
 */

import { useCallback, useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { WebSocketMessage } from '../types/websocket';
import toast from 'react-hot-toast';

interface FunctionCallNotificationData {
  type: 'function_call';
  agent_id: number;
  agent_name: string;
  action: 'created' | 'updated' | 'deleted';
  item_type: string;
  item_id?: number;
  item_title: string;
  success: boolean;
  message: string;
}

interface UseFunctionCallNotificationsOptions {
  conversationId?: number;
  projectId?: number;
  enabled?: boolean;
  onFunctionCall?: (data: FunctionCallNotificationData) => void;
}

const getActionEmoji = (action: string): string => {
  switch (action) {
    case 'created':
      return '+';
    case 'updated':
      return '~';
    case 'deleted':
      return '-';
    default:
      return '*';
  }
};

const getItemTypeIcon = (itemType: string): string => {
  switch (itemType) {
    case 'epic':
      return '🎯';
    case 'user_story':
      return '📖';
    case 'task':
      return '✓';
    case 'bug':
      return '🐛';
    case 'resource':
      return '📄';
    default:
      return '📌';
  }
};

export function useFunctionCallNotifications({
  conversationId,
  projectId,
  enabled = true,
  onFunctionCall,
}: UseFunctionCallNotificationsOptions = {}) {
  const handleMessage = useCallback(
    (message: WebSocketMessage) => {
      // Handle notify messages with function_call type
      if (message.type === 'notify' && (message as any).content?.type === 'function_call') {
        const data = (message as any).content as FunctionCallNotificationData;

        // Call custom handler if provided
        onFunctionCall?.(data);

        // Show toast notification
        const icon = getItemTypeIcon(data.item_type);
        const actionEmoji = getActionEmoji(data.action);

        if (data.success) {
          toast.success(
            `${icon} ${actionEmoji} ${data.message}`,
            {
              duration: 3000,
              position: 'bottom-right',
              style: {
                borderRadius: '8px',
                background: 'var(--secondary-800, #1f2937)',
                color: '#fff',
                fontSize: '14px',
              },
            }
          );
        } else {
          toast.error(
            `${icon} Failed: ${data.message}`,
            {
              duration: 4000,
              position: 'bottom-right',
            }
          );
        }
      }
    },
    [onFunctionCall]
  );

  const { isConnected } = useWebSocket({
    conversationId,
    projectId,
    autoConnect: enabled,
    onMessage: enabled ? handleMessage : undefined,
  });

  return {
    isConnected,
  };
}

export default useFunctionCallNotifications;
