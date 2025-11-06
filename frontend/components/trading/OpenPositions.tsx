"use client";

import { useState, useEffect, useCallback, useRef, memo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, RefreshCw, DollarSign, AlertCircle } from "lucide-react";
import { useCredentialsStore } from "@/store/credentials";
import { getPositionsDirect, getTickerDirect } from "@/lib/api/delta-direct";
import { Position } from "@/lib/types";
import { toast } from "sonner";
import CredentialsSetup from "./CredentialsSetup";

export const OpenPositions = memo(function OpenPositions() {
  // Use selector to only subscribe to credentials changes
  const credentials = useCredentialsStore((state) => state.credentials);
  const [positions, setPositions] = useState<Position[]>([]);
  const [totalUnrealizedPnL, setTotalUnrealizedPnL] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const credentialsRef = useRef(credentials);
  const priceCacheRef = useRef<Record<string, number>>({});

  // Handle client-side mounting to prevent hydration errors
  useEffect(() => {
    setMounted(true);
  }, []);

  // Keep ref in sync with credentials
  useEffect(() => {
    credentialsRef.current = credentials;
  }, [credentials]);

  const fetchPositions = useCallback(async () => {
    // Check credentials from ref to avoid re-renders
    const creds = credentialsRef.current;
    if (!creds?.deltaApiKey || !creds?.deltaApiSecret) {
      setError(null);
      setPositions([]);
      setTotalUnrealizedPnL(0);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const baseUrl = creds.deltaBaseUrl || 'https://api.india.delta.exchange';
      const data = await getPositionsDirect(
        creds.deltaApiKey,
        creds.deltaApiSecret,
        baseUrl
      );

      let positionsList: Position[] = [];
      let totalUnrealized = 0;

      if (data.result && Array.isArray(data.result)) {
        // Filter to show only open positions (size !== 0)
        const openPositions = data.result.filter((pos: any) => {
          const size = parseFloat(pos.size?.toString() || '0');
          return size !== 0;
        });

        // Clear price cache and fetch fresh prices for all open positions in parallel
        priceCacheRef.current = {};
        const pricePromises = openPositions.map(async (pos: any) => {
          const symbol = pos.product_symbol;
          try {
            const ticker = await getTickerDirect(symbol, baseUrl);
            const currentPrice = ticker.mark_price || ticker.close || 0;
            priceCacheRef.current[symbol] = currentPrice;
            return { symbol, price: currentPrice };
          } catch (error) {
            console.error(`Error fetching price for ${symbol}:`, error);
            return { symbol, price: 0 };
          }
        });

        const prices = await Promise.all(pricePromises);
        const priceMap = new Map(prices.map(p => [p.symbol, p.price]));

        // Map positions with calculated unrealized PnL
        positionsList = openPositions.map((pos: any) => {
          const size = parseFloat(pos.size?.toString() || '0');
          const entryPrice = parseFloat(pos.entry_price?.toString() || '0');
          const currentPrice = priceMap.get(pos.product_symbol) || 0;
          const isLong = size > 0;
          const absSize = Math.abs(size);

          // Try to get unrealized_pnl from API first (if available)
          let unrealizedPnL = 0;
          const apiUnrealizedPnL = pos.unrealized_pnl;
          
          if (apiUnrealizedPnL !== null && apiUnrealizedPnL !== undefined && apiUnrealizedPnL !== '') {
            // Use API provided unrealized PnL (already in USD)
            unrealizedPnL = parseFloat(apiUnrealizedPnL?.toString() || '0') || 0;
          } else if (entryPrice > 0 && absSize > 0 && currentPrice > 0) {
            // Calculate unrealized PnL manually
            // In Delta Exchange, the calculation depends on contract type
            // For linear contracts: PnL = (price_diff) * size
            // However, size might be in a smaller unit (e.g., 0.001 = 1 contract)
            // or there might be a contract multiplier
            
            const priceDiff = isLong ? (currentPrice - entryPrice) : (entryPrice - currentPrice);
            let calculatedPnL = priceDiff * absSize;
            
            // Check if the calculated value seems too large compared to realized PnL
            // This helps detect unit conversion issues
            const realizedPnLStr = pos.realized_pnl?.toString() || '0';
            const realizedPnL = parseFloat(realizedPnLStr) || 0;
            
            // If calculated is way larger (1000x+) than realized, likely a unit issue
            // Try dividing by common multipliers (100, 1000) to see if it matches better
            if (Math.abs(calculatedPnL) > 10 && Math.abs(realizedPnL) > 0) {
              const ratio = Math.abs(calculatedPnL) / Math.abs(realizedPnL);
              
              // If ratio is around 1000, divide by 1000
              if (ratio > 500 && ratio < 2000) {
                calculatedPnL = calculatedPnL / 1000;
                console.log(`Adjusted unrealized PnL for ${pos.product_symbol}: ${calculatedPnL.toFixed(2)} USD (was ${(priceDiff * absSize).toFixed(2)}, ratio was ${ratio.toFixed(2)})`);
              }
              // If ratio is around 100, divide by 100
              else if (ratio > 50 && ratio < 200) {
                calculatedPnL = calculatedPnL / 100;
                console.log(`Adjusted unrealized PnL for ${pos.product_symbol}: ${calculatedPnL.toFixed(2)} USD (was ${(priceDiff * absSize).toFixed(2)}, ratio was ${ratio.toFixed(2)})`);
              }
            }
            // Fallback: If calculated value is very large (> 100) and no realized PnL to compare,
            // it's likely a unit issue - divide by 1000 as a common multiplier
            else if (Math.abs(calculatedPnL) > 100 && Math.abs(realizedPnL) === 0) {
              calculatedPnL = calculatedPnL / 1000;
              console.log(`Adjusted unrealized PnL for ${pos.product_symbol} (fallback): ${calculatedPnL.toFixed(2)} USD (was ${(priceDiff * absSize).toFixed(2)})`);
            }
            
            unrealizedPnL = calculatedPnL;
          }

          totalUnrealized += unrealizedPnL;

          return {
            user_id: pos.user_id || 0,
            product_id: pos.product_id || 0,
            product_symbol: pos.product_symbol || '',
            size: size,
            entry_price: pos.entry_price?.toString() || '0',
            margin: pos.margin?.toString() || '0',
            liquidation_price: pos.liquidation_price?.toString() || null,
            bankruptcy_price: pos.bankruptcy_price?.toString() || null,
            adl_level: pos.adl_level || null,
            commission: pos.commission?.toString() || null,
            realized_funding: pos.realized_funding?.toString() || null,
            unrealized_pnl: unrealizedPnL,
            current_price: currentPrice,
          };
        });
      }

      setPositions(positionsList);
      setTotalUnrealizedPnL(totalUnrealized);
    } catch (error: any) {
      console.error("Error fetching positions:", error);
      setError(error.message || "Failed to fetch positions");
      setPositions([]);
      setTotalUnrealizedPnL(0);
      // Don't show toast for missing credentials (user hasn't set them up yet)
      if (error.message && !error.message.includes("credentials")) {
        toast.error(error.message || "Failed to fetch positions");
      }
    } finally {
      setIsLoading(false);
    }
  }, []); // No dependencies - uses ref for credentials

  // Auto-refresh every 10 seconds
  useEffect(() => {
    if (!credentials?.deltaApiKey || !credentials?.deltaApiSecret) {
      return;
    }

    fetchPositions();

    intervalRef.current = setInterval(() => {
      fetchPositions();
    }, 10000); // 10 seconds

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchPositions, credentials?.deltaApiKey, credentials?.deltaApiSecret]); // Only depend on credential values

  // Prevent hydration mismatch by not rendering credentials-dependent content until mounted
  if (!mounted) {
    return (
      <Card className="h-full flex flex-col shadow-xl border-2 border-gray-200/60 bg-gradient-to-br from-white via-blue-50/20 to-white backdrop-blur-sm">
        <CardHeader className="pb-4 border-b-2 border-gray-200/60 bg-gradient-to-r from-blue-50/80 via-indigo-50/50 to-transparent">
          <CardTitle className="flex items-center gap-2 text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            <div className="p-1.5 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 shadow-md">
              <TrendingUp className="w-4 h-4 text-white" />
            </div>
            Open Positions
          </CardTitle>
          <CardDescription className="mt-1.5 text-sm font-medium text-gray-600">
            Loading...
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto pt-4">
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 mb-4">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
            <p className="text-sm font-medium text-gray-600">Loading positions...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show credentials setup if no credentials (only after mount to prevent hydration error)
  if (!credentials?.deltaApiKey || !credentials?.deltaApiSecret) {
    return (
      <Card className="border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-900">
            <AlertCircle className="w-5 h-5" />
            Open Positions
          </CardTitle>
          <CardDescription className="text-amber-700">
            Configure API credentials to view your positions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CredentialsSetup />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col shadow-xl border-2 border-gray-200/60 bg-gradient-to-br from-white via-blue-50/20 to-white backdrop-blur-sm">
      <CardHeader className="pb-4 border-b-2 border-gray-200/60 bg-gradient-to-r from-blue-50/80 via-indigo-50/50 to-transparent">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              <div className="p-1.5 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 shadow-md">
                <TrendingUp className="w-4 h-4 text-white" />
              </div>
              Open Positions
            </CardTitle>
            <CardDescription className="mt-1.5 text-sm font-medium text-gray-600">
              {positions.length} active position{positions.length !== 1 ? 's' : ''}
            </CardDescription>
          </div>
          <button
            onClick={fetchPositions}
            disabled={isLoading}
            className="p-2.5 rounded-xl hover:bg-blue-100/80 transition-all duration-200 disabled:opacity-50 hover:scale-105 active:scale-95 shadow-sm hover:shadow-md"
            title="Refresh positions"
          >
            <RefreshCw className={`w-4 h-4 text-blue-600 ${isLoading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto pt-4">
        {/* Unrealized PnL Summary */}
        <div className="mb-5">
          <div className="p-5 rounded-2xl bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 border-2 border-blue-200/60 shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-xl ${totalUnrealizedPnL >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
                  <DollarSign className={`w-5 h-5 ${totalUnrealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}`} />
                </div>
                <div>
                  <span className="text-sm font-semibold text-gray-700 block">Total Unrealized P&L</span>
                  <span className="text-xs text-gray-500">Open positions only</span>
                </div>
              </div>
              <div className={`text-2xl font-extrabold ${totalUnrealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'} drop-shadow-sm`}>
                {totalUnrealizedPnL >= 0 ? '+' : ''}
                {totalUnrealizedPnL.toFixed(2)}
              </div>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Loading State */}
        {isLoading && positions.length === 0 && (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 mb-4">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
            <p className="text-sm font-medium text-gray-600">Loading positions...</p>
            <p className="text-xs text-gray-400 mt-1">Fetching from Delta Exchange</p>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && positions.length === 0 && (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 mb-5">
              <TrendingUp className="w-10 h-10 text-gray-400" />
            </div>
            <p className="text-lg font-bold text-gray-600 mb-1">No open positions</p>
            <p className="text-sm text-gray-400">Your open positions will appear here</p>
          </div>
        )}

        {/* Positions List */}
        {!isLoading && positions.length > 0 && (
          <div className="space-y-3">
            {positions.map((position, index) => {
              const size = typeof position.size === 'string' ? parseFloat(position.size) : position.size;
              const entryPrice = parseFloat(position.entry_price || '0');
              const unrealizedPnL = (position as any).unrealized_pnl || 0;
              const currentPrice = (position as any).current_price || 0;
              const isLong = size > 0;
              const margin = parseFloat(position.margin || '0');

              return (
                <div
                  key={`${position.product_id}-${index}`}
                  className="p-5 rounded-2xl border-2 bg-gradient-to-br from-white to-gray-50/50 hover:shadow-xl transition-all duration-300 border-gray-200/60 hover:border-blue-400/60 hover:scale-[1.02] active:scale-[0.98]"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-xl ${isLong ? 'bg-green-100' : 'bg-red-100'}`}>
                        {isLong ? (
                          <TrendingUp className="w-5 h-5 text-green-600" />
                        ) : (
                          <TrendingDown className="w-5 h-5 text-red-600" />
                        )}
                      </div>
                      <div>
                        <div className="font-extrabold text-gray-900 text-lg mb-1.5">{position.product_symbol}</div>
                        <Badge
                          variant={isLong ? "default" : "destructive"}
                          className="text-xs font-bold px-2.5 py-0.5 shadow-sm"
                        >
                          {isLong ? "LONG" : "SHORT"}
                        </Badge>
                      </div>
                    </div>
                    <div className={`text-right font-extrabold text-xl ${unrealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'} drop-shadow-sm`}>
                      {unrealizedPnL >= 0 ? '+' : ''}
                      {unrealizedPnL.toFixed(2)}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-2.5 rounded-lg bg-gray-50/80 border border-gray-200/50">
                      <div className="text-gray-500 text-xs mb-1.5 font-medium">Size</div>
                      <div className="font-bold text-gray-900 text-base">{Math.abs(size).toFixed(4)}</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-gray-50/80 border border-gray-200/50">
                      <div className="text-gray-500 text-xs mb-1.5 font-medium">Entry Price</div>
                      <div className="font-bold text-gray-900 text-base">{entryPrice.toFixed(2)}</div>
                    </div>
                    {currentPrice > 0 && (
                      <div className="p-2.5 rounded-lg bg-blue-50/80 border border-blue-200/50">
                        <div className="text-blue-600 text-xs mb-1.5 font-medium">Current Price</div>
                        <div className="font-bold text-blue-700 text-base">{currentPrice.toFixed(2)}</div>
                      </div>
                    )}
                    <div className="p-2.5 rounded-lg bg-gray-50/80 border border-gray-200/50">
                      <div className="text-gray-500 text-xs mb-1.5 font-medium">Margin</div>
                      <div className="font-bold text-gray-900 text-base">{margin.toFixed(2)}</div>
                    </div>
                    {position.liquidation_price && (
                      <div className="p-2.5 rounded-lg bg-red-50/80 border border-red-200/50">
                        <div className="text-red-600 text-xs mb-1.5 font-medium">Liquidation</div>
                        <div className="font-bold text-red-700 text-base">{parseFloat(position.liquidation_price).toFixed(2)}</div>
                      </div>
                    )}
                  </div>

                  {position.commission && parseFloat(position.commission) > 0 && (
                    <div className="mt-4 pt-4 border-t-2 border-gray-200/60">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-gray-500 font-medium">Commission</span>
                        <span className="font-bold text-gray-700 bg-gray-100 px-2 py-1 rounded-md">{parseFloat(position.commission).toFixed(4)}</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
});

