/**
 * Zustand store for authentication state
 * IMPORTANT: No sensitive credentials are stored for privacy reasons
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  isAuthenticated: boolean;
  setAuthenticated: (authenticated: boolean) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      setAuthenticated: (authenticated: boolean) =>
        set({
          isAuthenticated: authenticated,
        }),
      clearAuth: () =>
        set({
          isAuthenticated: false,
        }),
    }),
    {
      name: "auth-storage",
      // Only persist isAuthenticated flag, no sensitive data
    }
  )
);

