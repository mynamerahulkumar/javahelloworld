/**
 * Zustand store for authentication state
 * 
 * This store is used to cache SRP client ID and email from Supabase user metadata.
 * These values are used for order placement validation (CSV whitelist check).
 * 
 * IMPORTANT: No sensitive credentials are stored for privacy reasons.
 * Client ID and email come from Supabase user metadata (set during user migration).
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  srpClientId: string | null;
  srpClientEmail: string | null;
  setClientInfo: (clientId: string | null, clientEmail: string | null) => void;
  clearClientInfo: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      srpClientId: null,
      srpClientEmail: null,
      setClientInfo: (clientId: string | null, clientEmail: string | null) =>
        set({
          srpClientId: clientId || null,
          srpClientEmail: clientEmail || null,
        }),
      clearClientInfo: () =>
        set({
          srpClientId: null,
          srpClientEmail: null,
        }),
    }),
    {
      name: "auth-storage",
      // Only persist SRP client identifiers for order validation
    }
  )
);

