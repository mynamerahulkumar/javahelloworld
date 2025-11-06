/**
 * Custom hook for Delta Exchange connection status management
 */
import { useEffect, useCallback } from "react";
import { useCredentialsStore } from "@/store/credentials";
import { testConnection } from "@/lib/api/delta-direct";

export function useDeltaConnection() {
  const {
    credentials,
    connectionStatus,
    lastConnectionTest,
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
    if (!creds?.deltaApiKey || !creds?.deltaApiSecret) {
      setConnectionStatus("disconnected");
      return;
    }

    setConnectionStatus("testing");
    try {
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

