import api from './api';
import { storageUtils } from '@/utils/storage';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  token: string;
}

export interface User {
  userId: number;
  username: string;
  isAdmin: boolean;
}

class AuthAPI {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/api/login', credentials);
    return response.data;
  }

  async register(credentials: RegisterCredentials): Promise<{ message: string }> {
    const response = await api.post('/api/register', credentials);
    return response.data;
  }

  async logout(): Promise<void> {
    await storageUtils.clearAll();
  }

  async storeToken(token: string): Promise<void> {
    await storageUtils.setAuthToken(token);
  }

  async getStoredToken(): Promise<string | null> {
    return await storageUtils.getAuthToken();
  }

  async storeUserInfo(user: User): Promise<void> {
    await storageUtils.setUserInfo(user);
  }

  async getStoredUserInfo(): Promise<User | null> {
    return await storageUtils.getUserInfo();
  }

  async isAuthenticated(): Promise<boolean> {
    const token = await this.getStoredToken();
    return !!token;
  }

  // Decode JWT token to get user info (simple version)
  decodeToken(token: string): User | null {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }
}

export const authApi = new AuthAPI(); 