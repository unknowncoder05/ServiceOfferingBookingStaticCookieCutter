/**
 * Backend Manager Service
 *
 * Autonomously manages on-demand backend lifecycle:
 * - Starts/wakes backend when needed
 * - Keeps backend alive while app is in use
 * - Handles cold-start detection and retries
 * - Dynamically switches API base URLs
 *
 * This is transparent to the rest of the application.
 */

import env from '../config/environment';

interface TaskInfo {
  status: 'started' | 'extended' | 'alive';
  task_arn?: string;
  public_ip?: string;
  message?: string;
  expires_at?: number;
}

class BackendManager {
  private keepAliveIntervalId: NodeJS.Timeout | null = null;
  private currentBackendUrl: string | null = null;
  private isBackendReady: boolean = false;
  private startupPromise: Promise<void> | null = null;
  private healthCheckAttempted: boolean = false;

  constructor() {
    // Don't auto-start anymore - wait for explicit user action
    // Keep-alive will be initialized after successful start
  }

  /**
   * Get the current API base URL (dynamically updated based on backend state)
   */
  getApiBaseUrl(): string {
    if (!env.backend.useOnDemandBackend) {
      // Local development or static backend
      return env.apiBaseUrl;
    }

    // Use dynamic backend URL if available, otherwise fallback
    return this.currentBackendUrl || env.apiBaseUrl;
  }

  /**
   * Check if backend is healthy (quick check, doesn't start it)
   * Returns true if healthy, false otherwise
   */
  async checkHealth(): Promise<boolean> {
    if (!env.backend.useOnDemandBackend) {
      // Local dev - assume healthy
      return true;
    }

    this.healthCheckAttempted = true;

    try {
      // Try to check health via the dynamic backend URL if we have one
      const baseUrl = this.currentBackendUrl || env.apiBaseUrl;
      const healthUrl = `${baseUrl}/health/`;

      const response = await fetch(healthUrl, {
        method: 'GET',
        signal: AbortSignal.timeout(env.backend.healthCheckTimeout),
      });

      if (response.ok) {
        this.isBackendReady = true;
        this.initializeKeepAlive(); // Start keep-alive if not already running
        return true;
      }
    } catch (error) {
      console.log('Health check failed, backend not running:', error);
    }

    this.isBackendReady = false;
    return false;
  }

  /**
   * Get backend readiness status
   */
  isReady(): boolean {
    return this.isBackendReady;
  }

  /**
   * Check if we've attempted a health check
   */
  hasHealthCheckAttempted(): boolean {
    return this.healthCheckAttempted;
  }

  /**
   * Ensure backend is running before making API calls
   * Returns a promise that resolves when backend is ready
   */
  async ensureBackendReady(): Promise<void> {
    if (!env.backend.useOnDemandBackend) {
      // Not using on-demand backend, skip
      return;
    }

    if (this.isBackendReady) {
      // Backend already running
      return;
    }

    // If startup is already in progress, wait for it
    if (this.startupPromise) {
      return this.startupPromise;
    }

    // Start backend and wait for it to be ready
    this.startupPromise = this.startBackend();

    try {
      await this.startupPromise;
    } finally {
      this.startupPromise = null;
    }
  }

  /**
   * Manually start the backend (called by user action)
   * Returns a promise that resolves when backend is ready
   */
  async manualStart(): Promise<void> {
    if (!env.backend.useOnDemandBackend) {
      return;
    }

    await this.ensureBackendReady();
  }

  /**
   * Start or wake the backend
   */
  private async startBackend(): Promise<void> {
    if (!env.apiGatewayStartEndpoint) {
      console.warn('API Gateway start endpoint not configured');
      this.isBackendReady = true; // Assume ready to avoid blocking
      return;
    }

    try {
      console.log('Starting backend...');

      const response = await fetch(env.apiGatewayStartEndpoint, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to start backend: ${response.status}`);
      }

      const data: TaskInfo = await response.json();
      console.log('Backend response:', data);

      if (data.status === 'started') {
        // Backend is starting up, wait for it
        console.log('Backend starting, waiting for it to be ready...');
        await this.waitForBackendReady(data.public_ip);
      } else if (data.status === 'extended' || data.status === 'alive' || data.status === 'ready') {
        // Backend already running
        console.log('Backend already running');
        if (data.public_ip) {
          this.updateBackendUrl(data.public_ip);
        }
        this.isBackendReady = true;
        this.initializeKeepAlive(); // Start keep-alive
      }
    } catch (error) {
      console.error('Error starting backend:', error);
      // Mark as ready anyway to avoid infinite blocking
      // API calls will fail naturally if backend is truly down
      this.isBackendReady = true;
      throw error;
    }
  }

  /**
   * Wait for backend to be ready by polling health endpoint
   */
  private async waitForBackendReady(publicIp?: string): Promise<void> {
    if (!publicIp) {
      console.warn('No public IP provided, assuming backend ready');
      this.isBackendReady = true;
      return;
    }

    const backendUrl = `http://${publicIp}:${env.backend.port}`;
    const healthCheckUrl = `${backendUrl}${env.backend.apiBasePath}/health/`;
    const startTime = Date.now();

    while (Date.now() - startTime < env.backend.startupTimeout) {
      try {
        const response = await fetch(healthCheckUrl, {
          method: 'GET',
          signal: AbortSignal.timeout(env.backend.healthCheckTimeout),
        });

        if (response.ok) {
          console.log('Backend is ready!');
          this.updateBackendUrl(publicIp);
          this.isBackendReady = true;
          this.initializeKeepAlive(); // Start keep-alive
          return;
        }
      } catch (error) {
        // Backend not ready yet, continue polling
      }

      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, env.backend.pollingInterval));
    }

    // Timeout reached
    console.warn('Backend startup timeout, proceeding anyway');
    this.updateBackendUrl(publicIp);
    this.isBackendReady = true;
  }

  /**
   * Update the backend URL to point to the ECS task
   */
  private updateBackendUrl(publicIp: string): void {
    this.currentBackendUrl = `http://${publicIp}:${env.backend.port}${env.backend.apiBasePath}`;
    console.log(`Backend URL updated to: ${this.currentBackendUrl}`);
  }

  /**
   * Initialize keep-alive mechanism
   */
  private initializeKeepAlive(): void {
    // Clear any existing interval
    if (this.keepAliveIntervalId) {
      clearInterval(this.keepAliveIntervalId);
    }

    // Don't start keep-alive if not configured
    if (!env.apiGatewayStartEndpoint) {
      return;
    }

    // Ping backend periodically to keep it alive
    this.keepAliveIntervalId = setInterval(() => {
      this.pingBackend();
    }, env.backend.keepAliveInterval);

    console.log(`Keep-alive initialized (interval: ${env.backend.keepAliveInterval}ms)`);
  }

  /**
   * Ping backend to extend its lifetime
   * Now calls Django's keep-alive endpoint which pushes CloudWatch metrics
   */
  private async pingBackend(): Promise<void> {
    if (!this.isBackendReady) {
      // Don't ping if backend isn't ready
      return;
    }

    try {
      const keepAliveUrl = `${this.getApiBaseUrl()}/keep-alive/`;
      const response = await fetch(keepAliveUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Backend keep-alive ping successful:', data.status);

        // Update ping frequency if provided by backend
        if (data.ping_frequency_ms && data.ping_frequency_ms !== env.backend.keepAliveInterval) {
          console.log(`Updating ping frequency to ${data.ping_frequency_ms}ms`);
          env.backend.keepAliveInterval = data.ping_frequency_ms;
          // Restart keep-alive with new interval
          this.initializeKeepAlive();
        }
      } else if (response.status === 404 || response.status >= 500) {
        // Backend stopped or having issues, mark as not ready
        console.log('Backend not responding, will restart on next API call');
        this.isBackendReady = false;
        this.currentBackendUrl = null;
      }
    } catch (error) {
      console.error('Keep-alive ping failed:', error);
      // Don't mark as not ready on network errors - might be temporary
    }
  }

  /**
   * Stop keep-alive mechanism (e.g., when user logs out)
   */
  stopKeepAlive(): void {
    if (this.keepAliveIntervalId) {
      clearInterval(this.keepAliveIntervalId);
      this.keepAliveIntervalId = null;
      console.log('Keep-alive stopped');
    }
  }

  /**
   * Reset backend state (useful after authentication changes)
   */
  reset(): void {
    this.isBackendReady = false;
    this.currentBackendUrl = null;
    this.startupPromise = null;
  }

  /**
   * Manually trigger backend start (useful for testing or initial load)
   */
  async warmUp(): Promise<void> {
    if (env.backend.useOnDemandBackend) {
      await this.ensureBackendReady();
    }
  }
}

// Singleton instance
const backendManager = new BackendManager();

export default backendManager;
