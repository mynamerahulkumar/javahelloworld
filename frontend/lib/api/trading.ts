/**
 * Trading API endpoints
 */
import axios, { AxiosError } from "axios";
import { createApiRequest, ApiClientConfig } from "./client";
import { 
  PlaceLimitOrderWaitRequest, 
  OrderResponse, 
  LoginRequest, 
  LoginResponse,
  TickerResponse,
  PriceFetchIntervalResponse,
  VerifyClientEmailResponse
} from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8501/api/v1";

export async function login(data: LoginRequest): Promise<LoginResponse> {
  // Create a client with shorter timeout for login (should be fast)
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000, // 10 seconds timeout for login
    headers: {
      "Content-Type": "application/json",
    },
  });
  
  // Add error handling for connection issues
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      // Only log connection errors once (not duplicated)
      const isConnectionError = error.code === 'ECONNABORTED' || 
                                error.code === 'ERR_NETWORK' ||
                                error.message?.includes('timeout') || 
                                error.message?.includes('ERR_CONNECTION') ||
                                (!error.response && error.request);
      
      if (isConnectionError) {
        // Log technical details to console for developers (only once)
        console.error("Login connection error:", {
          code: error.code,
          message: error.message,
          url: error.config?.url,
          baseURL: error.config?.baseURL
        });
        console.error("Backend server is not reachable. Please start the backend using: ./start-all.sh or cd backend && ./start.sh");
        
        // User-friendly error message
        return Promise.reject({
          detail: "Unable to connect to the server. Please try again later or contact support if the problem persists.",
          status: 0,
          isConnectionError: true,
        });
      } else if (error.response) {
        // Server responded with error
        const errorMessage = (error.response.data as any)?.detail || (error.response.data as any)?.error || error.message;
        return Promise.reject({
          detail: errorMessage,
          status: error.response.status,
        });
      }
      return Promise.reject({
        detail: error.message || "Login failed",
        status: 0,
      });
    }
  );
  
  const response = await client.post<LoginResponse>("/login", data);
  return response.data;
}

export async function placeLimitOrderWait(
  data: PlaceLimitOrderWaitRequest,
  config?: ApiClientConfig
): Promise<OrderResponse> {
  const client = await createApiRequest(config);
  const response = await client.post<OrderResponse>("/place-limit-order-wait", data);
  return response.data;
}

export async function getTicker(symbol: string, timeout: number = 5000): Promise<TickerResponse> {
  // Create a client with shorter timeout for ticker requests
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  
  let authToken: string | null = null;
  try {
    const { getCurrentSession } = await import("@/lib/auth/supabase/client");
    const session = await getCurrentSession();
    if (session?.access_token) {
      authToken = session.access_token;
    }
  } catch (error) {
    // Session not available, continue without token
  }

  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: timeout, // Short timeout for ticker requests
    headers: {
      "Content-Type": "application/json",
      ...(authToken && { "Authorization": `Bearer ${authToken}` }),
    },
  });

  // Add error handling
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        return Promise.reject({
          detail: "Request timeout",
          status: 0,
          isConnectionError: true,
        });
      } else if (error.response) {
        const errorMessage = (error.response.data as any)?.detail || error.message;
        return Promise.reject({
          detail: errorMessage,
          status: error.response.status,
        });
      } else if (error.request) {
        return Promise.reject({
          detail: "Unable to connect to the server",
          status: 0,
          isConnectionError: true,
        });
      }
      return Promise.reject({
        detail: error.message,
        status: 0,
      });
    }
  );

  const response = await client.get<TickerResponse>(`/ticker/${symbol}`);
  return response.data;
}

export async function getPriceFetchInterval(): Promise<PriceFetchIntervalResponse> {
  const client = await createApiRequest();
  const response = await client.get<PriceFetchIntervalResponse>("/price-fetch-interval");
  return response.data;
}

export async function verifyClientEmail(email: string, clientId?: string): Promise<VerifyClientEmailResponse> {
  const client = await createApiRequest();
  const params: Record<string, string> = { email };
  if (clientId) {
    params.client_id = clientId;
  }
  const response = await client.get<VerifyClientEmailResponse>("/verify-client-email", {
    params,
  });
  return response.data;
}

export interface FearGreedIndexResponse {
  success: boolean;
  data: {
    value: number;
    value_classification: string;
    update_time: string;
  };
}

export async function getFearGreedIndex(): Promise<FearGreedIndexResponse> {
  // createApiRequest already has error handling interceptors
  const client = await createApiRequest();
  const response = await client.get<FearGreedIndexResponse>("/fear-greed-index");
  return response.data;
}

