const isDevelopment = __DEV__;

export const config = {
  API_BASE_URL: isDevelopment 
    ? 'http://localhost:8787' // For local development
    : 'https://your-worker-name.your-account.workers.dev', // Production URL
  
  // Security settings
  TOKEN_STORAGE_KEY: 'authToken',
  USER_INFO_STORAGE_KEY: 'userInfo',
  
  // API timeouts
  REQUEST_TIMEOUT: 10000,
  
  // App settings
  APP_NAME: 'Design Gallery',
  APP_VERSION: '1.0.0',
}; 