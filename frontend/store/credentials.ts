/**
 * Zustand store for Delta API credentials
 * CRITICAL: Credentials are stored client-side only (localStorage), never sent to server for storage
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface DeltaCredentials {
  deltaApiKey: string;
  deltaApiSecret: string;
  deltaBaseUrl?: string;
  srpClientEmail?: string;
  srpClientId?: string;
}

export type ConnectionStatus = "connected" | "disconnected" | "testing" | "unknown";

interface CredentialsState {
  credentials: DeltaCredentials | null;
  connectionStatus: ConnectionStatus;
  lastConnectionTest: string | null; // ISO string for serialization
  setCredentials: (credentials: DeltaCredentials) => void;
  getCredentials: () => DeltaCredentials | null;
  clearCredentials: () => void;
  hasCredentials: () => boolean;
  setConnectionStatus: (status: ConnectionStatus) => void;
  setLastConnectionTest: (date: Date | null) => void;
  getLastConnectionTestDate: () => Date | null;
}

export const useCredentialsStore = create<CredentialsState>()(
  persist(
    (set, get) => ({
      credentials: null,
      connectionStatus: "unknown" as ConnectionStatus,
      lastConnectionTest: null,
      setCredentials: (credentials: DeltaCredentials) =>
        set({ credentials }),
      getCredentials: () => get().credentials,
      clearCredentials: () => set({ 
        credentials: null,
        connectionStatus: "unknown",
        lastConnectionTest: null,
      }),
      hasCredentials: () => {
        const creds = get().credentials;
        if (!creds) {
          return false;
        }
        return !!(
          creds.deltaApiKey &&
          creds.deltaApiSecret &&
          creds.srpClientEmail &&
          creds.srpClientId
        );
      },
      setConnectionStatus: (status: ConnectionStatus) =>
        set({ connectionStatus: status }),
      setLastConnectionTest: (date: Date | null) =>
        set({ lastConnectionTest: date ? date.toISOString() : null }),
      getLastConnectionTestDate: () => {
        const test = get().lastConnectionTest;
        return test ? new Date(test) : null;
      },
    }),
    {
      name: "delta-credentials-storage",
      // Only persist credentials client-side in localStorage
      // NEVER send to server for storage
      partialize: (state) => ({
        credentials: state.credentials,
        // Don't persist connection status and lastConnectionTest
        // They should be reset on page load
      }),
    }
  )
);


