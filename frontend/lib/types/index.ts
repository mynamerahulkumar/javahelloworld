/**
 * TypeScript types matching backend models
 */

export interface PlaceLimitOrderWaitRequest {
  symbol?: string;
  product_id?: number;
  product_symbol?: string;
  entry_price: number;
  size: number;
  side: "buy" | "sell";
  stop_loss_price?: number;
  take_profit_price?: number;
  client_order_id?: string;
  wait_time_seconds?: number;
}

export interface OrderResponse {
  success: boolean;
  order_id?: number;
  message: string;
  order_data?: Record<string, any>;
  error?: string | null;
}

export interface ApiError {
  detail: string;
  status?: number;
}

export interface LoginRequest {
  srp_client_id: string;
  srp_client_email: string;
  srp_password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  error?: string | null;
}

export interface TickerResponse {
  success: boolean;
  symbol: string;
  mark_price: number | null;
  spot_price: number | null;
  close: number | null;
  high: number | null;
  low: number | null;
  open: number | null;
  volume: number | null;
  timestamp?: number;
  full_data?: Record<string, any>;
}

export interface PriceFetchIntervalResponse {
  interval_seconds: number;
}

export interface VerifyClientEmailResponse {
  email: string;
  authorized: boolean;
  client_id?: string | null;
  id_matches: boolean;
}

// Strategy types
export interface TradingConfig {
  symbol: string;
  product_id: number;
  order_size: number;
  max_position_size?: number;
  check_existing_orders?: boolean;
}

export interface ScheduleConfig {
  timeframe: "1m" | "3m" | "5m" | "15m" | "30m" | "1h" | "2h" | "4h" | "6h" | "1d" | "1w";
  timezone: string;
  wait_for_next_candle?: boolean;
  startup_delay_minutes?: number;
  reset_interval_minutes?: number;
}

export interface RiskManagementConfig {
  stop_loss_points: number;
  take_profit_points: number;
  breakeven_trigger_points: number;
}

export interface MonitoringConfig {
  order_check_interval?: number;
  position_check_interval?: number;
}

export interface APIConfig {
  base_url?: string;
  api_key?: string;
  api_secret?: string;
}

export interface BreakoutStrategyConfig {
  trading: TradingConfig;
  schedule: ScheduleConfig;
  risk_management: RiskManagementConfig;
  monitoring?: MonitoringConfig;
  api?: APIConfig;
}

export interface StartStrategyRequest {
  strategy_type: "breakout";
  config: BreakoutStrategyConfig;
}

export interface StrategyStatus {
  strategy_id: string;
  status: "stopped" | "running" | "error" | "completed";
  start_time?: number;
  stop_time?: number;
  error_message?: string;
  symbol?: string;
  timeframe?: string;
  prev_period_high?: number;
  prev_period_low?: number;
  active_position?: {
    side?: string;
    entry_price?: number;
    size?: number;
  };
  buy_order_id?: number;
  sell_order_id?: number;
  stop_loss_order_id?: number;
  take_profit_order_id?: number;
  breakeven_applied?: boolean;
}

export interface StrategyInstance extends StrategyStatus {}

export interface StartStrategyResponse {
  success: boolean;
  strategy_id?: string;
  message: string;
  error?: string | null;
}

export interface StopStrategyResponse {
  success: boolean;
  message: string;
  error?: string | null;
}

export interface StrategyListResponse {
  strategies: StrategyStatus[];
  total: number;
}

export interface StrategyLogsResponse {
  strategy_id: string;
  logs: string;
}

// Positions and Orders types
export interface Position {
  user_id: number;
  size: number;
  entry_price: string;
  margin: string;
  liquidation_price?: string | null;
  bankruptcy_price?: string | null;
  adl_level?: number | null;
  product_id: number;
  product_symbol: string;
  commission?: string | null;
  realized_pnl?: string | null;
  realized_funding?: string | null;
}

export interface PositionResponse {
  success: boolean;
  positions: Position[];
}

export interface OrderHistoryItem {
  id: number;
  user_id: number;
  size: number;
  unfilled_size?: number | null;
  side: string;
  order_type: string;
  limit_price?: string | null;
  stop_order_type?: string | null;
  stop_price?: string | null;
  paid_commission?: string | null;
  commission?: string | null;
  reduce_only: boolean;
  client_order_id?: string | null;
  state: string;
  created_at: string;
  product_id: number;
  product_symbol: string;
}

export interface OrderHistoryMeta {
  after?: string | null;
  before?: string | null;
}

export interface OrderHistoryResponse {
  success: boolean;
  result: OrderHistoryItem[];
  meta?: OrderHistoryMeta | null;
}

export interface PnLBySymbol {
  symbol: string;
  realized_pnl: number;
  position_count: number;
}

export interface PnLSummaryResponse {
  success: boolean;
  total_pnl: number;
  total_realized_pnl: number;
  total_unrealized_pnl: number;
  position_count: number;
  pnl_by_symbol: PnLBySymbol[];
}

export interface PollingIntervalResponse {
  interval_seconds: number;
  min_interval: number;
  max_interval: number;
}

export interface DeltaCredentials {
  deltaApiKey: string;
  deltaApiSecret: string;
  deltaBaseUrl?: string;
}

export interface TradeHistoryItem {
  id: number;
  user_id: number;
  order_id: number;
  size: number;
  price: string;
  side: string;
  product_id: number;
  product_symbol: string;
  commission?: string | null;
  realized_funding?: string | null;
  created_at: string;
}

export interface TradeHistoryMeta {
  after?: string | null;
  before?: string | null;
}

export interface TradeHistoryResponse {
  success: boolean;
  result: TradeHistoryItem[];
  meta?: TradeHistoryMeta | null;
}

