export const environment = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  apiBaseUrl: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  apiGatewayStartEndpoint: process.env.REACT_APP_API_GATEWAY_START_ENDPOINT || '',
  keepAliveInterval: parseInt(process.env.REACT_APP_KEEP_ALIVE_INTERVAL || '300000', 10),
  startupTimeout: parseInt(process.env.REACT_APP_STARTUP_TIMEOUT || '90000', 10),
  healthCheckTimeout: parseInt(process.env.REACT_APP_HEALTH_CHECK_TIMEOUT || '5000', 10),
  pollingInterval: parseInt(process.env.REACT_APP_POLLING_INTERVAL || '2000', 10),
  navigationDelay: parseInt(process.env.REACT_APP_NAVIGATION_DELAY || '1000', 10),
  backend: {
    useOnDemandBackend: !!process.env.REACT_APP_API_GATEWAY_START_ENDPOINT,
    port: parseInt(process.env.REACT_APP_BACKEND_PORT || '5000', 10),
    apiBasePath: process.env.REACT_APP_API_BASE_PATH || '/api',
    healthCheckTimeout: parseInt(process.env.REACT_APP_HEALTH_CHECK_TIMEOUT || '5000', 10),
    startupTimeout: parseInt(process.env.REACT_APP_STARTUP_TIMEOUT || '90000', 10),
    pollingInterval: parseInt(process.env.REACT_APP_POLLING_INTERVAL || '2000', 10),
    keepAliveInterval: parseInt(process.env.REACT_APP_KEEP_ALIVE_INTERVAL || '300000', 10),
  },
};

export default environment;
