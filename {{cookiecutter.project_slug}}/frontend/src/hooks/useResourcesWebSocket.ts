import { useEffect, useCallback, useState } from 'react';
import { useWebSocket } from './useWebSocket';
import { ResourceWebSocketEvent, ResourceWebSocketEventType } from '../types/resources';

interface UseResourcesWebSocketOptions {
  projectId: number;
  resourceId?: number;
  onResourceCreated?: (data: ResourceWebSocketEvent['data']) => void;
  onResourceUpdated?: (data: ResourceWebSocketEvent['data']) => void;
  onResourceDeleted?: (data: ResourceWebSocketEvent['data']) => void;
  onResourceLocked?: (data: ResourceWebSocketEvent['data']) => void;
  onResourceUnlocked?: (data: ResourceWebSocketEvent['data']) => void;
  onCommentAdded?: (data: ResourceWebSocketEvent['data']) => void;
  onCollaboratorJoined?: (data: ResourceWebSocketEvent['data']) => void;
  onCollaboratorLeft?: (data: ResourceWebSocketEvent['data']) => void;
}

export const useResourcesWebSocket = ({
  projectId,
  resourceId,
  onResourceCreated,
  onResourceUpdated,
  onResourceDeleted,
  onResourceLocked,
  onResourceUnlocked,
  onCommentAdded,
  onCollaboratorJoined,
  onCollaboratorLeft,
}: UseResourcesWebSocketOptions) => {
  const [activeCollaborators, setActiveCollaborators] = useState<Array<{
    type: 'user' | 'agent';
    id: number;
    name: string;
  }>>([]);

  const { isConnected, subscribe, unsubscribe } = useWebSocket({
    projectId: projectId,
    autoConnect: true,
  });

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((message: any) => {
    const { type, data } = message;

    switch (type as ResourceWebSocketEventType) {
      case 'resource_created':
        onResourceCreated?.(data);
        break;
      case 'resource_updated':
        onResourceUpdated?.(data);
        break;
      case 'resource_deleted':
        onResourceDeleted?.(data);
        break;
      case 'resource_locked':
        onResourceLocked?.(data);
        break;
      case 'resource_unlocked':
        onResourceUnlocked?.(data);
        break;
      case 'resource_comment_added':
        onCommentAdded?.(data);
        break;
      case 'resource_collaborator_joined':
        if (data.collaborator) {
          setActiveCollaborators(prev => {
            const exists = prev.some(c => c.id === data.collaborator.id && c.type === data.collaborator.type);
            if (!exists) {
              return [...prev, data.collaborator];
            }
            return prev;
          });
        }
        onCollaboratorJoined?.(data);
        break;
      case 'resource_collaborator_left':
        if (data.collaborator) {
          setActiveCollaborators(prev =>
            prev.filter(c => !(c.id === data.collaborator.id && c.type === data.collaborator.type))
          );
        }
        onCollaboratorLeft?.(data);
        break;
    }
  }, [
    onResourceCreated,
    onResourceUpdated,
    onResourceDeleted,
    onResourceLocked,
    onResourceUnlocked,
    onCommentAdded,
    onCollaboratorJoined,
    onCollaboratorLeft,
  ]);

  // Subscribe to project and optionally resource-specific channels
  useEffect(() => {
    if (isConnected && projectId) {
      // Subscribe to project-wide resource events
      subscribe({ projectId: projectId });

      // If viewing a specific resource, subscribe to its channel
      if (resourceId) {
        subscribe({ channelId: `resource-${resourceId}` });
      }
    }

    return () => {
      if (resourceId) {
        unsubscribe({ channelId: `resource-${resourceId}` });
      }
    };
  }, [isConnected, projectId, resourceId, subscribe, unsubscribe]);

  return {
    isConnected,
    activeCollaborators,
  };
};

export default useResourcesWebSocket;
