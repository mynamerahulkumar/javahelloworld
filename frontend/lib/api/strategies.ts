/**
 * Strategy API endpoints
 */
import { createApiRequest, ApiClientConfig } from "./client";
import {
  StartStrategyRequest,
  StartStrategyResponse,
  StopStrategyResponse,
  StrategyListResponse,
  StrategyStatus,
  StrategyLogsResponse,
} from "../types";

export async function startBreakoutStrategy(
  config: StartStrategyRequest["config"],
  apiConfig?: ApiClientConfig
): Promise<StartStrategyResponse> {
  const client = await createApiRequest(apiConfig);
  const request: StartStrategyRequest = {
    strategy_type: "breakout",
    config,
  };
  const response = await client.post<StartStrategyResponse>(
    "/strategies/breakout/start",
    request
  );
  return response.data;
}

export async function stopStrategy(
  strategyId: string,
  apiConfig?: ApiClientConfig
): Promise<StopStrategyResponse> {
  const client = await createApiRequest(apiConfig);
  const response = await client.post<StopStrategyResponse>(
    `/strategies/${strategyId}/stop`,
    {}
  );
  return response.data;
}

export async function getAllStrategies(
  apiConfig?: ApiClientConfig
): Promise<StrategyListResponse> {
  const client = await createApiRequest(apiConfig);
  const response = await client.get<StrategyListResponse>("/strategies");
  return response.data;
}

export async function getStrategyStatus(
  strategyId: string,
  apiConfig?: ApiClientConfig
): Promise<StrategyStatus> {
  const client = await createApiRequest(apiConfig);
  const response = await client.get<StrategyStatus>(
    `/strategies/${strategyId}`
  );
  return response.data;
}

export async function getStrategyLogs(
  strategyId: string,
  limit: number = 100,
  apiConfig?: ApiClientConfig
): Promise<StrategyLogsResponse> {
  const client = await createApiRequest(apiConfig);
  const response = await client.get<StrategyLogsResponse>(
    `/strategies/${strategyId}/logs?limit=${limit}`
  );
  return response.data;
}

