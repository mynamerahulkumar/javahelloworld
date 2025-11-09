/**
 * Direct Delta Exchange API client (client-side only)
 * 
 * This module provides functions to call Delta Exchange API directly from the browser.
 * All credentials are stored client-side only and never sent to our server.
 */

/**
 * Get UTC timestamp in seconds as string
 */
function getTimestamp(): string {
  return Math.floor(Date.now() / 1000).toString();
}

/**
 * Build query string from params
 */
function buildQueryString(params: Record<string, string | number> | null): string {
  if (!params) return '';
  const queryParts = Object.entries(params)
    .map(([key, value]) => `${key}=${encodeURIComponent(String(value))}`);
  return queryParts.length > 0 ? '?' + queryParts.join('&') : '';
}

/**
 * Generate signature for Delta Exchange API request
 * Uses Web Crypto API for HMAC-SHA256
 */
async function generateHMACSignature(secret: string, message: string): Promise<string> {
  const encoder = new TextEncoder();
  const keyData = encoder.encode(secret);
  const messageData = encoder.encode(message);
  
  // Import key for HMAC
  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    keyData,
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  
  // Sign the message
  const signature = await crypto.subtle.sign('HMAC', cryptoKey, messageData);
  
  // Convert to hex string
  const hashArray = Array.from(new Uint8Array(signature));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Fetch positions directly from Delta Exchange API
 * Uses /v2/positions/margined endpoint to get all margined positions
 */
export async function getPositionsDirect(
  apiKey: string,
  apiSecret: string,
  baseUrl: string = 'https://api.india.delta.exchange'
): Promise<any> {
  const method = 'GET';
  const path = '/v2/positions/margined';
  const query = null; // No query params to get all positions
  const queryStr = buildQueryString(query);
  const timestamp = getTimestamp();
  
  // Build signature data: method + timestamp + path + query_string + body_string
  const signatureData = method + timestamp + path + queryStr + '';
  const signature = await generateHMACSignature(apiSecret, signatureData);
  
  // Build URL
  const url = `${baseUrl}${path}${queryStr}`;
  
  // Make request
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'api-key': apiKey,
      'timestamp': timestamp,
      'signature': signature,
    },
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch positions');
  }
  
  return data;
}

/**
 * Fetch ticker data for a symbol (no authentication required)
 */
export async function getTickerDirect(
  symbol: string,
  baseUrl: string = 'https://api.india.delta.exchange'
): Promise<any> {
  const url = `${baseUrl}/v2/tickers/${symbol}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  
  if (!data.success || !data.result) {
    throw new Error(data.error || 'Failed to fetch ticker');
  }
  
  return {
    success: true,
    symbol: data.result.symbol,
    mark_price: parseFloat(data.result.mark_price) || 0,
    close: parseFloat(data.result.close) || 0,
    spot_price: parseFloat(data.result.spot_price) || 0,
  };
}

/**
 * Close all positions using Delta Exchange API
 * Uses /v2/positions/close_all endpoint
 */
export async function closeAllPositions(
  apiKey: string,
  apiSecret: string,
  baseUrl: string = 'https://api.india.delta.exchange',
  userId: number = 0
): Promise<any> {
  const method = 'POST';
  const path = '/v2/positions/close_all';
  const query = null;
  const queryStr = buildQueryString(query);
  const timestamp = getTimestamp();
  
  // Request body
  const body = JSON.stringify({
    close_all_portfolio: true,
    close_all_isolated: true,
    user_id: userId,
  });
  
  // Build signature data: method + timestamp + path + query_string + body_string
  const signatureData = method + timestamp + path + queryStr + body;
  const signature = await generateHMACSignature(apiSecret, signatureData);
  
  // Build URL
  const url = `${baseUrl}${path}${queryStr}`;
  
  // Make request
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'api-key': apiKey,
      'timestamp': timestamp,
      'signature': signature,
    },
    body: body,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Failed to close all positions');
  }
  
  return data;
}

/**
 * Get order history from Delta Exchange API
 * Uses /v2/orders/history endpoint with pagination support
 */
export async function getOrderHistory(
  apiKey: string,
  apiSecret: string,
  baseUrl: string = 'https://api.india.delta.exchange',
  after?: string,
  before?: string
): Promise<any> {
  const method = 'GET';
  const path = '/v2/orders/history';
  const query: Record<string, string> = {};
  if (after) query.after = after;
  if (before) query.before = before;
  const queryStr = buildQueryString(query);
  const timestamp = getTimestamp();
  
  // Build signature data: method + timestamp + path + query_string + body_string
  const signatureData = method + timestamp + path + queryStr + '';
  const signature = await generateHMACSignature(apiSecret, signatureData);
  
  // Build URL
  const url = `${baseUrl}${path}${queryStr}`;
  
  // Make request
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'api-key': apiKey,
      'timestamp': timestamp,
      'signature': signature,
    },
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch order history');
  }
  
  return data;
}

/**
 * Test connection to Delta Exchange API
 * Uses /v2/positions/margined endpoint to verify credentials
 */
export async function testConnection(
  apiKey: string,
  apiSecret: string,
  baseUrl: string = 'https://api.india.delta.exchange'
): Promise<{ success: boolean; connected: boolean; error?: string }> {
  try {
    await getPositionsDirect(apiKey, apiSecret, baseUrl);
    return {
      success: true,
      connected: true,
    };
  } catch (error: any) {
    return {
      success: false,
      connected: false,
      error: error.message || 'Connection test failed',
    };
  }
}

