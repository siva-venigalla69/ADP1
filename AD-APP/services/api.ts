import axios from 'axios';
import { storageUtils } from '@/utils/storage';

// Update this URL to your deployed Cloudflare Worker URL
const API_BASE_URL = 'http://localhost:8787'; // For local development
// const API_BASE_URL = 'https://your-actual-worker-url'; // Replace with URL from dashboard

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await storageUtils.getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear it
      await storageUtils.removeAuthToken();
      // Optionally redirect to login
    }
    return Promise.reject(error);
  }
);

export default api; 