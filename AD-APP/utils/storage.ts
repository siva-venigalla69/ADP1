import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

interface Storage {
  setItem: (key: string, value: string) => Promise<void>;
  getItem: (key: string) => Promise<string | null>;
  removeItem: (key: string) => Promise<void>;
}

class WebStorage implements Storage {
  async setItem(key: string, value: string): Promise<void> {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(key, value);
    }
  }

  async getItem(key: string): Promise<string | null> {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem(key);
    }
    return null;
  }

  async removeItem(key: string): Promise<void> {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(key);
    }
  }
}

class NativeStorage implements Storage {
  async setItem(key: string, value: string): Promise<void> {
    await SecureStore.setItemAsync(key, value);
  }

  async getItem(key: string): Promise<string | null> {
    return await SecureStore.getItemAsync(key);
  }

  async removeItem(key: string): Promise<void> {
    await SecureStore.deleteItemAsync(key);
  }
}

// Export platform-specific storage
export const platformStorage: Storage = Platform.OS === 'web' 
  ? new WebStorage() 
  : new NativeStorage();

// Helper functions for common storage operations
export const storageUtils = {
  async setAuthToken(token: string): Promise<void> {
    await platformStorage.setItem('authToken', token);
  },

  async getAuthToken(): Promise<string | null> {
    return await platformStorage.getItem('authToken');
  },

  async removeAuthToken(): Promise<void> {
    await platformStorage.removeItem('authToken');
  },

  async setUserInfo(user: any): Promise<void> {
    await platformStorage.setItem('userInfo', JSON.stringify(user));
  },

  async getUserInfo(): Promise<any | null> {
    const userInfo = await platformStorage.getItem('userInfo');
    return userInfo ? JSON.parse(userInfo) : null;
  },

  async removeUserInfo(): Promise<void> {
    await platformStorage.removeItem('userInfo');
  },

  async clearAll(): Promise<void> {
    await this.removeAuthToken();
    await this.removeUserInfo();
  }
}; 