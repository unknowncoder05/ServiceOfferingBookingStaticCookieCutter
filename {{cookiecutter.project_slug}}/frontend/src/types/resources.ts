export type ResourceWebSocketEventType =
  | 'resource_created'
  | 'resource_updated'
  | 'resource_deleted'
  | 'resource_locked'
  | 'resource_unlocked'
  | 'resource_comment_added'
  | 'resource_collaborator_joined'
  | 'resource_collaborator_left';

export interface ResourceWebSocketEvent {
  type: ResourceWebSocketEventType;
  data: {
    id?: number;
    [key: string]: any;
    collaborator?: {
      type: 'user' | 'agent';
      id: number;
      name: string;
    };
  };
}
