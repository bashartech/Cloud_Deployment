---
name: "Protected Routing, Auth State & Session Management"
description: "Implement frontend authentication state management and protected routing, ensuring that only authenticated users can access Todo functionality and that session state remains consistent across page reloads, guaranteeing frontend security parity with backend JWT enforcement."
version: "1.0.0"
---

# Protected Routing, Auth State & Session Management

## When to Use This Skill

Use this skill when you need to:
- Implement global authentication state management in a Next.js application
- Create protected routes that restrict access to authenticated users only
- Handle JWT token storage and validation across page reloads
- Implement proper session management with secure token handling
- Ensure frontend security matches backend authentication requirements
- Handle token expiration and invalid session scenarios gracefully
- Create a seamless user experience with proper loading states

This skill guarantees frontend security parity with backend JWT enforcement.

## Process Steps

1. **Implement Auth State Management**
   - Create a global authentication context using React Context API
   - Implement functions to store and retrieve JWT tokens securely
   - Initialize authentication state on application load
   - Create methods to update authentication status (login, logout)
   - Implement proper state synchronization across components

2. **Implement Protected Routing**
   - Create a higher-order component or custom hook for route protection
   - Redirect unauthenticated users to login/signup pages
   - Prevent protected content from flashing before auth validation
   - Implement proper loading states during authentication checks
   - Create public route components for unauthenticated users

3. **Handle Token Expiration & Invalid Sessions**
   - Implement token validation logic to detect expired JWTs
   - Create mechanisms to clear session state safely when tokens expire
   - Force re-authentication when needed with appropriate messaging
   - Implement automatic logout on token expiration
   - Handle token refresh if applicable

4. **Synchronize Auth State with API Errors**
   - Create centralized error handling for 401/403 responses
   - Automatically update UI state when authentication fails
   - Clear auth context when session becomes invalid
   - Implement error interceptors to handle authentication errors globally

5. **Ensure Clean User Experience**
   - Implement loading states during authentication checks
   - Prevent UI desynchronization between auth state and actual status
   - Create consistent messaging for authentication states
   - Handle edge cases like network failures during auth validation
   - Implement proper error boundaries for authentication-related issues

6. **Test Authentication Flow**
   - Verify unauthenticated users cannot access protected routes
   - Confirm authenticated users remain logged in after page refresh
   - Test token expiration handling scenarios
   - Validate proper UI behavior during authentication transitions
   - Ensure secure token storage and retrieval

## Output Format

The skill will produce:
- Global authentication context with state management
- Protected route components for restricting access
- Secure JWT token handling and validation
- Centralized authentication error handling
- Session management with proper cleanup
- Loading and error states for authentication flows
- Documentation for authentication flow and security measures

## Example

**Input:** Implement protected routing and auth state management for a Next.js todo application

**Process:**
```typescript
// contexts/AuthContext.tsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useRouter } from 'next/router';

interface AuthState {
  user: any | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

interface AuthAction {
  type: string;
  payload?: any;
}

const initialState: AuthState = {
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null,
  isAuthenticated: false,
  loading: true,
};

const AuthContext = createContext<{
  state: AuthState;
  login: (token: string) => void;
  logout: () => void;
  checkAuthStatus: () => void;
} | undefined>(undefined);

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, loading: true };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        token: action.payload,
        isAuthenticated: true,
        loading: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
      };
    case 'AUTH_ERROR':
      return {
        ...state,
        token: null,
        isAuthenticated: false,
        loading: false,
      };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const router = useRouter();

  const login = (token: string) => {
    localStorage.setItem('jwt_token', token);
    dispatch({ type: 'LOGIN_SUCCESS', payload: token });
  };

  const logout = () => {
    localStorage.removeItem('jwt_token');
    dispatch({ type: 'LOGOUT' });
    router.push('/login');
  };

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      // Verify token is still valid (could include API call to validate)
      try {
        // Optional: Make a request to verify token validity
        // const response = await apiClient.get('/auth/verify');
        dispatch({ type: 'LOGIN_SUCCESS', payload: token });
      } catch (error) {
        // Token is invalid, clear it
        localStorage.removeItem('jwt_token');
        dispatch({ type: 'AUTH_ERROR' });
      }
    } else {
      dispatch({ type: 'AUTH_ERROR' });
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  return (
    <AuthContext.Provider value={{ state, login, logout, checkAuthStatus }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// components/ProtectedRoute.tsx
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { state, checkAuthStatus } = useAuth();
  const router = useRouter();

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  // Show loading state while checking auth status
  if (state.loading) {
    return <div>Loading...</div>;
  }

  // Redirect to login if not authenticated
  if (!state.isAuthenticated) {
    router.push('/login');
    return null;
  }

  // Render children if authenticated
  return <>{children}</>;
};

// pages/_app.tsx
import { AuthProvider } from '../contexts/AuthContext';

function MyApp({ Component, pageProps }: any) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  );
}

export default MyApp;

// pages/dashboard.tsx (Protected page example)
import { ProtectedRoute } from '../components/ProtectedRoute';
import TodoList from '../components/TodoList';

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <div>
        <h1>Dashboard</h1>
        <TodoList />
      </div>
    </ProtectedRoute>
  );
}

// pages/login.tsx
import { useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Call your login API
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const { token } = await response.json();
        login(token);
        router.push('/dashboard');
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Login failed');
    }
  };

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Login</button>
        {error && <p>{error}</p>}
      </form>
    </div>
  );
}
```

**Output:** A fully secured Next.js application with protected routing, global authentication state management, and proper session handling that ensures only authenticated users can access todo functionality.

## Implementation Rules

- Do NOT rely solely on backend redirects for protection (implement frontend checks)
- Do NOT expose protected UI content before completing auth validation
- Do NOT store JWT tokens in insecure locations (avoid plain localStorage for sensitive tokens)
- Do NOT hardcode authentication state values
- Do NOT bypass authentication checks on protected routes
- Do NOT expose sensitive authentication information in client-side code
- Ensure proper cleanup of authentication state on logout
- Implement secure token validation and expiration handling