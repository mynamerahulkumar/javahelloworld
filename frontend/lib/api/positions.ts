/**
 * Positions API endpoints
 */
import { createApiRequest } from "./client";
import { useCredentialsStore } from "@/store/credentials";
import { useAuthStore } from "@/store/auth";
import {
  PositionResponse,
  PnLSummaryResponse,
  PollingIntervalResponse,
} from "../types";

export async function getPositions(): Promise<PositionResponse> {
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

  const response = await client.get<PositionResponse>("/positions");
  return response.data;
}

export async function getPnLSummary(): Promise<PnLSummaryResponse> {
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

  const response = await client.get<PnLSummaryResponse>("/pnl");
  return response.data;
}

export async function getPollingInterval(): Promise<PollingIntervalResponse> {
  const client = await createApiRequest();
  const response = await client.get<PollingIntervalResponse>("/polling-interval");
  return response.data;
}

