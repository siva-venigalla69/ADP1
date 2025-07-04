import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authApi, User } from '@/services/authApi';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await authApi.getStoredToken();
      console.log('Checking auth status, token found:', !!token);
      
      if (token) {
        const userInfo = await authApi.getStoredUserInfo();
        if (userInfo) {
          console.log('User info found:', userInfo.username);
          setUser(userInfo);
        } else {
          // Decode token if user info not stored
          const decodedUser = authApi.decodeToken(token);
          if (decodedUser) {
            console.log('Decoded user from token:', decodedUser.username);
            setUser(decodedUser);
            await authApi.storeUserInfo(decodedUser);
          }
        }
      } else {
        console.log('No token found, user not authenticated');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      // Clear any invalid tokens
      try {
        await authApi.logout();
      } catch (logoutError) {
        console.error('Logout error:', logoutError);
      }
    } finally {
      setIsLoading(false);
      console.log('Auth check completed');
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const response = await authApi.login({ username, password });
      await authApi.storeToken(response.token);
      
      const userInfo = authApi.decodeToken(response.token);
      if (userInfo) {
        setUser(userInfo);
        await authApi.storeUserInfo(userInfo);
      }
    } catch (error) {
      throw error;
    }
  };

  const register = async (username: string, password: string) => {
    try {
      await authApi.register({ username, password });
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 