import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { clearAuthToken, setAuthToken } from "../api/client";
import { getCurrentUser, login as loginRequest } from "../api/auth";
import type { UserRead } from "../types";

interface AuthContextValue {
  user: UserRead | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserRead | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function bootstrapAuth() {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        clearAuthToken();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    bootstrapAuth();
  }, []);

  async function login(email: string, password: string) {
    const result = await loginRequest(email, password);
    setAuthToken(result.access_token);
    setUser(result.user);
  }

  function logout() {
    clearAuthToken();
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
    }),
    [user, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}