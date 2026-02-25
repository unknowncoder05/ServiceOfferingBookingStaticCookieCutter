/**
 * WebSocket Service
 *
 * Manages WebSocket connections for real-time communication with the backend.
 * Supports automatic reconnection, message queuing, and subscription management.
 */

import { WebSocketMessage } from '../types/websocket';
import backendManager from './BackendManager';

export type WebSocketCallback = (message: WebSocketMessage) => void;
export type ConnectionStatusCallback = (connected: boolean) => void;

interface SubscriptionRequest {
  action: 'subscribe' | 'unsubscribe';
  project_id?: number;
  channel_id?: string;
  agent_id?: string;
  conversation_id?: number;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private messageCallbacks: Set<WebSocketCallback> = new Set();
  private statusCallbacks: Set<ConnectionStatusCallback> = new Set();
  private messageQueue: any[] = [];
  private isConnecting = false;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingInterval: NodeJS.Timeout | null = null;
  private currentSubscriptions: SubscriptionRequest[] = [];
  private authToken: string | null = null;
  private userId: number | null = null;

  /**
   * Get WebSocket URL from API base URL
   */
  private getWebSocketUrl(): string {
    const apiUrl = backendManager.getApiBaseUrl();
    const wsProtocol = apiUrl.startsWith('https://') ? 'wss://' : 'ws://';

    let baseUrl = apiUrl.replace(/^https?:/, '');
    console.log(`${wsProtocol}${baseUrl}/ws/`)

    // No token in URL - authentication happens via message after connection
    return `${wsProtocol}${baseUrl}/ws/`;
  }

  /**
   * Set authentication token for WebSocket connection
   */
  setAuthToken(token: string | null): void {
    this.authToken = token;

    // If token changed and we're connected, reconnect with new token
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('Auth token changed, reconnecting...');
      this.disconnect();
      if (token) {
        this.connect();
      }
    }
  }

  /**
   * Connect to WebSocket server
   * Requires auth token to be set first via setAuthToken()
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      console.log('WebSocket already connected or connecting');
      return;
    }

    this.isConnecting = true;
    const wsUrl = this.getWebSocketUrl();
    console.log('Connecting to WebSocket:', wsUrl);

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected, sending authentication...');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;

        // Send authentication message with token
        if (this.authToken && this.ws) {
          this.ws.send(JSON.stringify({
            action: 'authenticate',
            token: this.authToken,
          }));
        } else {
          console.warn('No auth token available for WebSocket authentication');
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          console.log('WebSocket message received:', message);

          // Handle connection_accepted (before authentication)
          if (message.type === 'connection_accepted') {
            console.log('WebSocket connection accepted, awaiting authentication...');
            return;
          }

          // Handle authentication failure
          if (message.type === 'authentication_failed') {
            console.error('WebSocket authentication failed:', message.error);
            this.notifyStatusCallbacks(false);
            return;
          }

          // Handle successful authentication
          if (message.type === 'connection_established' && message.user_id) {
            this.userId = message.user_id;
            console.log('WebSocket authenticated for user:', this.userId);

            // Now that we're authenticated, notify callbacks and setup
            this.notifyStatusCallbacks(true);
            this.startPingInterval();

            // Resubscribe to previous subscriptions
            this.resubscribe();

            // Send queued messages
            this.flushMessageQueue();
          }

          this.notifyMessageCallbacks(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnecting = false;
        this.notifyStatusCallbacks(false);
        this.stopPingInterval();
        this.scheduleReconnect();
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.stopPingInterval();

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.currentSubscriptions = [];
    this.reconnectAttempts = 0;
    this.userId = null;
  }

  /**
   * Get authenticated user ID
   */
  getUserId(): number | null {
    return this.userId;
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    );

    console.log(`Scheduling reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  /**
   * Start ping interval to keep connection alive
   */
  private startPingInterval(): void {
    this.stopPingInterval();
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', data: {} });
      }
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Stop ping interval
   */
  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Send message through WebSocket
   * Messages are queued until WebSocket is connected AND authenticated
   */
  send(message: any): void {
    // Only send if connected AND authenticated (userId is set after successful auth)
    if (this.ws?.readyState === WebSocket.OPEN && this.userId !== null) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.log('WebSocket not ready or not authenticated, queuing message');
      this.messageQueue.push(message);
    }
  }

  /**
   * Flush queued messages
   */
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift();
      this.ws.send(JSON.stringify(message));
    }
  }

  /**
   * Subscribe to project updates
   */
  subscribe(request: SubscriptionRequest): void {
    // Store subscription for resubscription on reconnect
    this.currentSubscriptions.push(request);
    this.send(request);
  }

  /**
   * Unsubscribe from updates
   */
  unsubscribe(request: Omit<SubscriptionRequest, 'action'>): void {
    const unsubRequest = { ...request, action: 'unsubscribe' as const };
    this.send(unsubRequest);

    // Remove from current subscriptions
    this.currentSubscriptions = this.currentSubscriptions.filter(
      sub => !this.subscriptionsMatch(sub, unsubRequest)
    );
  }

  /**
   * Check if two subscriptions match
   */
  private subscriptionsMatch(sub1: SubscriptionRequest, sub2: SubscriptionRequest): boolean {
    return (
      sub1.project_id === sub2.project_id &&
      sub1.channel_id === sub2.channel_id &&
      sub1.agent_id === sub2.agent_id
    );
  }

  /**
   * Resubscribe to all current subscriptions
   */
  private resubscribe(): void {
    for (const subscription of this.currentSubscriptions) {
      this.send(subscription);
    }
  }

  /**
   * Add message callback
   */
  onMessage(callback: WebSocketCallback): () => void {
    this.messageCallbacks.add(callback);
    return () => this.messageCallbacks.delete(callback);
  }

  /**
   * Add connection status callback
   */
  onConnectionStatus(callback: ConnectionStatusCallback): () => void {
    this.statusCallbacks.add(callback);
    // Immediately notify of current status
    callback(this.ws?.readyState === WebSocket.OPEN);
    return () => this.statusCallbacks.delete(callback);
  }

  /**
   * Notify all message callbacks
   */
  private notifyMessageCallbacks(message: WebSocketMessage): void {
    this.messageCallbacks.forEach(callback => {
      try {
        callback(message);
      } catch (error) {
        console.error('Error in message callback:', error);
      }
    });
  }

  /**
   * Notify all status callbacks
   */
  private notifyStatusCallbacks(connected: boolean): void {
    this.statusCallbacks.forEach(callback => {
      try {
        callback(connected);
      } catch (error) {
        console.error('Error in status callback:', error);
      }
    });
  }

  /**
   * Check if WebSocket is connected and authenticated
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN && this.userId !== null;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();
export default websocketService;
