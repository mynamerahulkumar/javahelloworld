/**
 * Orders API endpoints
 */
import { createApiRequest } from "./client";
import { useCredentialsStore } from "@/store/credentials";
import { useAuthStore } from "@/store/auth";
import { OrderHistoryResponse, TradeHistoryResponse } from "../types";

export async function getOrderHistory(
  pageSize: number = 100,
  after?: string
): Promise<OrderHistoryResponse> {
  const credentials = useCredentialsStore.getState().getCredentials();
  const { srpClientId, srpClientEmail } = useAuthStore.getState();

  if (!credentials?.deltaApiKey || !credentials?.deltaApiSecret) {
    throw new Error("Delta API credentials not set. Please configure credentials first.");
  }

  const client = await createApiRequest({
    srpClientId: srpClientId ?? undefined,
    srpClientEmail: srpClientEmail ?? undefined,
    deltaApiKey: credentials.deltaApiKey,
    deltaApiSecret: credentials.deltaApiSecret,
    deltaBaseUrl: credentials.deltaBaseUrl ?? undefined,
  });

  const params = new URLSearchParams();
  params.append("page_size", pageSize.toString());
  if (after) {
    params.append("after", after);
  }

  const response = await client.get<OrderHistoryResponse>(
    `/orders/history?${params.toString()}`
  );
  return response.data;
}

export async function getTradeHistory(
  pageSize: number = 100,
  after?: string
): Promise<TradeHistoryResponse> {
  const credentials = useCredentialsStore.getState().getCredentials();
  const { srpClientId, srpClientEmail } = useAuthStore.getState();

  if (!credentials?.deltaApiKey || !credentials?.deltaApiSecret) {
    throw new Error("Delta API credentials not set. Please configure credentials first.");
  }

  const client = await createApiRequest({
    srpClientId: srpClientId ?? undefined,
    srpClientEmail: srpClientEmail ?? undefined,
    deltaApiKey: credentials.deltaApiKey,
    deltaApiSecret: credentials.deltaApiSecret,
    deltaBaseUrl: credentials.deltaBaseUrl ?? undefined,
  });

  const params = new URLSearchParams();
  params.append("page_size", pageSize.toString());
  if (after) {
    params.append("after", after);
  }

  const response = await client.get<TradeHistoryResponse>(
    `/trades/history?${params.toString()}`
  );
  return response.data;
}

