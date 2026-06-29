"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";
import { apiClient } from "@/lib/api";

const ACCESS_KEY = "documind_access_token";
const REFRESH_KEY = "documind_refresh_token";

type User = {
  id: string;
  email: string;
  full_name?: string | null;
};

type AuthContextValue = {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  loading: boolean;
  authenticated: boolean;
  login: () => void;
  logout: () => void;
  setAccessToken: (token: string | null) => void;
  setRefreshToken: (token: string | null) => void;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [refreshToken, setRefreshTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const setAccessToken = useCallback((token: string | null) => {
    setAccessTokenState(token);
    if (token) {
      localStorage.setItem(ACCESS_KEY, token);
    } else {
      localStorage.removeItem(ACCESS_KEY);
    }
  }, []);

  const setRefreshToken = useCallback((token: string | null) => {
    setRefreshTokenState(token);
    if (token) {
      localStorage.setItem(REFRESH_KEY, token);
    } else {
      localStorage.removeItem(REFRESH_KEY);
    }
  }, []);

  const login = useCallback(() => {
    window.location.replace("/login");
  }, []);

  const logout = useCallback(() => {
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
    setLoading(false);
    // If you use React Query, you could clear cache here via queryClient.clear()
    window.location.replace("/login");
  }, [setAccessToken, setRefreshToken]);

  const refreshUser = useCallback(async () => {
    if (!accessToken) {
      setUser(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const res = await apiClient.get("/auth/me", {
        headers: { Authorization: "Bearer " + accessToken },
      });
      setUser(res.data);
    } catch {
      setUser(null);
      setAccessToken(null);
    } finally {
      setLoading(false);
    }
  }, [accessToken, setAccessToken]);

  // Hydrate tokens on first render
  useEffect(() => {
    try {
      const storedAccess = typeof window !== "undefined"
        ? localStorage.getItem(ACCESS_KEY)
        : null;
      const storedRefresh = typeof window !== "undefined"
        ? localStorage.getItem(REFRESH_KEY)
        : null;

      if (storedAccess) {
        setAccessTokenState(storedAccess);
      }
      if (storedRefresh) {
        setRefreshTokenState(storedRefresh);
      }

      if (!storedAccess) {
        setLoading(false);
      }
    } catch {
      // localStorage may be unavailable; fail gracefully
      setLoading(false);
    }
  }, []);

  // Fetch current user whenever accessToken changes
  useEffect(() => {
    if (!accessToken) {
      setUser(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    const fetchMe = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get("/auth/me", {
          headers: { Authorization: "Bearer " + accessToken },
        });
        if (!cancelled) setUser(res.data);
      } catch {
        if (!cancelled) {
          setUser(null);
          setAccessToken(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchMe();

    return () => {
      cancelled = true;
    };
  }, [accessToken, setAccessToken]);

  // Attach request interceptor; eject when accessToken changes
  useEffect(() => {
    const requestId = apiClient.interceptors.request.use((config) => {
      if (accessToken) {
        config.headers = config.headers ?? {};
        config.headers["Authorization"] = "Bearer " + accessToken;
      }
      return config;
    });

    return () => {
      apiClient.interceptors.request.eject(requestId);
    };
  }, [accessToken]);

  // Attach response interceptor once; handle 401 globally
  useEffect(() => {
    const responseId = apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error?.response?.status === 401) {
          // Session expired or invalid token
          setAccessToken(null);
          setRefreshToken(null);
          setUser(null);
          window.location.replace("/login");
        }
        return Promise.reject(error);
      }
    );

    return () => {
      apiClient.interceptors.response.eject(responseId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const authenticated = !!user;

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        refreshToken,
        loading,
        authenticated,
        login,
        logout,
        setAccessToken,
        setRefreshToken,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}