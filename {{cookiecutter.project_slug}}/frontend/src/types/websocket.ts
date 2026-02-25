export interface WebSocketMessage {
  type: string;
  error?: string;
  user_id?: number;
  [key: string]: any;
}
