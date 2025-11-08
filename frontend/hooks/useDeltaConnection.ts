/**
 * Custom hook for Delta Exchange connection status management
 */
import { useEffect, useCallback } from "react";
import { useCredentialsStore } from "@/store/credentials";
import { testConnection } from "@/lib/api/delta-direct";
import { verifyClientEmail } from "@/lib/api/trading";

export function useDeltaConnection() {
  const {
    credentials,
    connectionStatus,
    setConnectionStatus,
    setLastConnectionTest,
    getLastConnectionTestDate,
    hasCredentials,
  } = useCredentialsStore();

  /**
   * Test connection to Delta Exchange
   */
  const testConnectionStatus = useCallback(async () => {
    if (!hasCredentials()) {
      setConnectionStatus("disconnected");
      return;
    }

    const creds = credentials;
    if (
      !creds?.deltaApiKey ||
      !creds?.deltaApiSecret ||
      !creds?.srpClientEmail ||
      !creds?.srpClientId
    ) {
      setConnectionStatus("disconnected");
      return;
    }

    setConnectionStatus("testing");
    try {
      const verification = await verifyClientEmail(
        creds.srpClientEmail,
        creds.srpClientId
      );

      if (!verification.authorized || !verification.id_matches) {
        setConnectionStatus("disconnected");
        setLastConnectionTest(new Date());
        return;
      }

      const result = await testConnection(
        creds.deltaApiKey,
        creds.deltaApiSecret,
        creds.deltaBaseUrl || 'https://api.india.delta.exchange'
      );

      if (result.connected) {
        setConnectionStatus("connected");
        setLastConnectionTest(new Date());
      } else {
        setConnectionStatus("disconnected");
        setLastConnectionTest(new Date());
      }
    } catch (error) {
      console.warn("Delta connection test failed", error);
      setConnectionStatus("disconnected");
      setLastConnectionTest(new Date());
    }
  }, [credentials, hasCredentials, setConnectionStatus, setLastConnectionTest]);

  /**
   * Auto-test connection on mount and when credentials change
   */
  useEffect(() => {
    if (hasCredentials()) {
      testConnectionStatus();
    } else {
      setConnectionStatus("disconnected");
    }
  }, [hasCredentials, testConnectionStatus, setConnectionStatus]);

  /**
   * Periodic connection status refresh (every 30 seconds)
   */
  useEffect(() => {
    if (!hasCredentials()) {
      return;
    }

    const interval = setInterval(() => {
      testConnectionStatus();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [hasCredentials, testConnectionStatus]);

  return {
    connectionStatus,
    lastConnectionTest: getLastConnectionTestDate(),
    isConnected: connectionStatus === "connected",
    isTesting: connectionStatus === "testing",
    testConnection: testConnectionStatus,
  };
}

