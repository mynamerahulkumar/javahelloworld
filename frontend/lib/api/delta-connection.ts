/**
 * Delta Exchange Connection Test Module
 * Tests connection to Delta Exchange API using client-side credentials
 */

import { getPositionsDirect } from "./delta-direct";

export interface ConnectionTestResult {
  success: boolean;
  connected: boolean;
  error?: string;
  message?: string;
}

/**
 * Test Delta Exchange connection by attempting to fetch positions
 * Uses /v2/positions/margined endpoint to verify credentials
 */
export async function testDeltaConnection(
  apiKey: string,
  apiSecret: string,
  baseUrl: string = 'https://api.india.delta.exchange'
): Promise<ConnectionTestResult> {
  try {
    // Test connection by fetching positions
    // This endpoint requires authentication, so if it succeeds, credentials are valid
    const data = await getPositionsDirect(apiKey, apiSecret, baseUrl);
    
    if (data.success !== false) {
      return {
        success: true,
        connected: true,
        message: "Successfully connected to Delta Exchange",
      };
    } else {
      return {
        success: false,
        connected: false,
        error: data.error || "Connection test failed",
      };
    }
  } catch (error: any) {
    // Handle different types of errors
    let errorMessage = "Connection test failed";
    
    if (error.message) {
      errorMessage = error.message;
    } else if (typeof error === 'string') {
      errorMessage = error;
    }
    
    // Check for common error patterns
    if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
      errorMessage = "Invalid API credentials. Please check your API key and secret.";
    } else if (errorMessage.includes('403') || errorMessage.includes('Forbidden')) {
      errorMessage = "API credentials are not authorized for this operation.";
    } else if (errorMessage.includes('timeout') || errorMessage.includes('network')) {
      errorMessage = "Network error. Please check your internet connection.";
    }
    
    return {
      success: false,
      connected: false,
      error: errorMessage,
    };
  }
}





