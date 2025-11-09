/**
 * Axios API client with interceptors
 * 
 * Note: Supabase tokens are obtained from the Supabase session and added to Authorization header.
 */
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from "axios";
import { getCurrentSession } from "@/lib/auth/supabase/client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8501/api/v1";

export interface ApiClientConfig {
  srpClientId?: string;
  srpClientEmail?: string;
  deltaApiKey?: string;
  deltaApiSecret?: string;
  deltaBaseUrl?: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor(config?: ApiClientConfig) {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor to add auth headers
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Headers are added via createApiRequest function instead
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          // Server responded with error status
          const errorMessage = (error.response.data as any)?.detail || error.message;
          return Promise.reject({
            detail: errorMessage,
            status: error.response.status,
          });
        } else if (error.request) {
          // Request made but no response received - likely backend is not running
          const isTimeout = error.code === 'ECONNABORTED' || error.message.includes('timeout');
          const isConnectionRefused = error.code === 'ECONNREFUSED' || error.message.includes('ERR_CONNECTION');
          
          // Log technical details to console for developers
          if (isTimeout || isConnectionRefused) {
            console.error("Backend connection error:", {
              code: error.code,
              message: error.message,
              url: error.config?.url,
              baseURL: error.config?.baseURL
            });
            console.error("Backend server is not reachable. Please start the backend using: ./start-all.sh or cd backend && ./start.sh");
          }
          
          // User-friendly error message
          return Promise.reject({
            detail: "Unable to connect to the server. Please try again later or contact support if the problem persists.",
            status: 0,
            isConnectionError: true,
          });
        } else {
          // Something else happened
          return Promise.reject({
            detail: error.message,
            status: 0,
          });
        }
      }
    );
  }

  getClient(): AxiosInstance {
    return this.client;
  }

  // Method to update headers dynamically
  updateConfig(config: ApiClientConfig) {
    this.client.defaults.headers = this.client.defaults.headers || {};
    if (config.srpClientId) {
      (this.client.defaults.headers as any)["X-SRP-Client-ID"] = config.srpClientId;
    }
    if (config.srpClientEmail) {
      (this.client.defaults.headers as any)["X-SRP-Client-Email"] = config.srpClientEmail;
    }
    if (config.deltaApiKey) {
      (this.client.defaults.headers as any)["X-Delta-API-Key"] = config.deltaApiKey;
    }
    if (config.deltaApiSecret) {
      (this.client.defaults.headers as any)["X-Delta-API-Secret"] = config.deltaApiSecret;
    }
    if (config.deltaBaseUrl) {
      (this.client.defaults.headers as any)["X-Delta-Base-URL"] = config.deltaBaseUrl;
    }
  }
}

// Create singleton instance
export const apiClient = new ApiClient();

// Export function to create requests with config
export async function createApiRequest(config?: ApiClientConfig): Promise<AxiosInstance> {
  // Get Supabase session token
  let authToken: string | null = null;
  try {
    const session = await getCurrentSession();
    if (session?.access_token) {
      authToken = session.access_token;
    }
  } catch (error) {
    // Session not available, continue without token
    console.warn("Could not get Supabase session for API request:", error);
  }

  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000, // 5 minutes timeout for order placement (includes wait time)
    headers: {
      "Content-Type": "application/json",
      ...(authToken && { "Authorization": `Bearer ${authToken}` }),
      ...(config?.srpClientId && { "X-SRP-Client-ID": config.srpClientId }),
      ...(config?.srpClientEmail && { "X-SRP-Client-Email": config.srpClientEmail }),
      ...(config?.deltaApiKey && { "X-Delta-API-Key": config.deltaApiKey }),
      ...(config?.deltaApiSecret && { "X-Delta-API-Secret": config.deltaApiSecret }),
      ...(config?.deltaBaseUrl && { "X-Delta-Base-URL": config.deltaBaseUrl }),
    },
    withCredentials: true, // Include cookies for session management
  });

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        return Promise.reject({
          detail: "Request timeout: The request is taking longer than expected. Please check backend logs.",
          status: 0,
          isConnectionError: true,
        });
      } else if (error.response) {
        const errorMessage = (error.response.data as any)?.detail || (error.response.data as any)?.error || error.message;
        return Promise.reject({
          detail: errorMessage,
          status: error.response.status,
        });
      } else if (error.request) {
        const isTimeout = error.code === 'ECONNABORTED' || error.message.includes('timeout');
        const isConnectionRefused = error.code === 'ECONNREFUSED' || error.message.includes('ERR_CONNECTION');
        
        // Log technical details to console for developers
        if (isTimeout || isConnectionRefused) {
          console.error("Backend connection error:", {
            code: error.code,
            message: error.message,
            url: error.config?.url,
            baseURL: error.config?.baseURL
          });
          console.error("Backend server is not reachable. Please start the backend using: ./start-all.sh or cd backend && ./start.sh");
        }
        
        // User-friendly error message
        return Promise.reject({
          detail: "Unable to connect to the server. Please try again later or contact support if the problem persists.",
          status: 0,
          isConnectionError: true,
        });
      } else {
        return Promise.reject({
          detail: error.message,
          status: 0,
        });
      }
    }
  );

  return client;
}

