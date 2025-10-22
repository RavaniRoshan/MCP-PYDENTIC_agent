// src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';

/**
 * @interface User
 * @description Represents a user.
 * @property {string} id - The unique identifier for the user.
 * @property {string} name - The name of the user.
 * @property {string} email - The email of the user.
 */
interface User {
  id: string;
  name: string;
  email: string;
}

/**
 * @interface AuthContextType
 * @description The context for authentication.
 * @property {User | null} user - The current user.
 * @property {(email: string, password: string) => Promise<boolean>} login - A function to log in a user.
 * @property {() => void} logout - A function to log out a user.
 * @property {(name: string, email: string, password: string) => Promise<boolean>} register - A function to register a new user.
 * @property {boolean} isAuthenticated - A flag indicating whether the user is authenticated.
 */
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * @provider AuthProvider
 * @description A provider for the authentication context.
 * @param {{ children: ReactNode }} props - The props for the component.
 * @returns {React.FC} The authentication provider.
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check for existing session on component mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        localStorage.removeItem('user');
      }
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    // In a real app, this would make an API call to your backend
    // For now, we'll simulate a successful login
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Mock user data - in a real app this would come from your API
      const mockUser: User = {
        id: 'user_123',
        name: 'John Doe',
        email: email
      };
      
      setUser(mockUser);
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify(mockUser));
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const register = async (name: string, email: string, password: string): Promise<boolean> => {
    // In a real app, this would make an API call to your backend
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Mock user data - in a real app this would come from your API
      const mockUser: User = {
        id: 'user_123',
        name: name,
        email: email
      };
      
      setUser(mockUser);
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify(mockUser));
      return true;
    } catch (error) {
      console.error('Registration failed:', error);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('user');
    // In a real app, you might also call an API to invalidate the session
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, register, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * @hook useAuth
 * @description A hook to use the authentication context.
 * @returns {AuthContextType} The authentication context.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};