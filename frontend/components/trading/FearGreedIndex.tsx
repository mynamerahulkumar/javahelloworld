"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, AlertCircle, RefreshCw } from "lucide-react";
import { toast } from "sonner";

interface FearGreedData {
  value: number;
  value_classification: string;
  update_time: string;
}

export default function FearGreedIndex() {
  const [data, setData] = useState<FearGreedData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchFearGreedIndex = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch from backend API (which handles CoinMarketCap API call)
      const { getFearGreedIndex } = await import("@/lib/api/trading");
      const result = await getFearGreedIndex();

      if (result.success && result.data && result.data.value !== undefined) {
        setData({
          value: result.data.value,
          value_classification: result.data.value_classification || "Unknown",
          update_time: result.data.update_time || new Date().toISOString(),
        });
      } else {
        throw new Error("Invalid response format");
      }
    } catch (err: any) {
      console.error("Error fetching Fear and Greed Index:", err);
      const errorMessage = err.detail || err.message || "Failed to fetch Fear and Greed Index";
      
      // Check if it's a rate limit error
      const isRateLimit = err.status === 429 || 
                         err.detail?.includes('Rate limit') ||
                         err.detail?.includes('429');
      
      // Check if it's a connection error
      const isConnectionError = err.isConnectionError || 
                                err.message?.includes('timeout') ||
                                err.message?.includes('ERR_CONNECTION') ||
                                err.detail?.includes('Unable to connect');
      
      if (isRateLimit) {
        setError("Rate limit exceeded. Data will refresh automatically in a few minutes.");
        // Don't show toast for rate limits - it's expected behavior
      } else if (isConnectionError) {
        setError("Backend server is not running. Please start the backend server to view Fear & Greed Index.");
      } else {
        setError(errorMessage);
      }
      
      // Don't show toast on initial load or rate limits to avoid noise
      if (data && !isRateLimit) {
        toast.error("Failed to update Fear and Greed Index");
      }
    } finally {
      setIsLoading(false);
    }
  }, [data]);

  useEffect(() => {
    fetchFearGreedIndex();

    // Refresh every 10 minutes (reduced frequency to avoid rate limiting)
    // Backend caches for 5 minutes, so this ensures we get fresh data
    intervalRef.current = setInterval(() => {
      fetchFearGreedIndex();
    }, 10 * 60 * 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchFearGreedIndex]);

  const getClassificationColor = (value: number): string => {
    if (value >= 76) return "text-red-600 bg-red-50 border-red-200";
    if (value >= 51) return "text-orange-600 bg-orange-50 border-orange-200";
    if (value === 50) return "text-yellow-600 bg-yellow-50 border-yellow-200";
    if (value >= 25) return "text-blue-600 bg-blue-50 border-blue-200";
    return "text-purple-600 bg-purple-50 border-purple-200";
  };

  const getGaugeColor = (value: number): string => {
    if (value >= 76) return "bg-red-500";
    if (value >= 51) return "bg-orange-500";
    if (value === 50) return "bg-yellow-500";
    if (value >= 25) return "bg-blue-500";
    return "bg-purple-500";
  };

  const getGaugeGradient = (value: number): string => {
    if (value >= 76) return "from-red-500 to-red-600";
    if (value >= 51) return "from-orange-500 to-orange-600";
    if (value === 50) return "from-yellow-500 to-yellow-600";
    if (value >= 25) return "from-blue-500 to-blue-600";
    return "from-purple-500 to-purple-600";
  };

  if (error && !data) {
    return (
      <Card className="border-2 border-gray-200">
        <CardHeader>
          <CardTitle className="text-lg">Fear & Greed Index</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-sm text-gray-500 py-4">
            <AlertCircle className="w-5 h-5 mx-auto mb-2 text-gray-400" />
            {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-gray-200 bg-gradient-to-br from-white via-blue-50/20 to-white">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-bold">Fear & Greed Index</CardTitle>
          <button
            onClick={fetchFearGreedIndex}
            disabled={isLoading}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 text-gray-500 ${isLoading ? "animate-spin" : ""}`} />
          </button>
        </div>
        <CardDescription className="text-xs">
          Market sentiment indicator (0-100)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading && !data ? (
          <div className="text-center py-4">
            <div className="animate-pulse text-sm text-gray-500">Loading...</div>
          </div>
        ) : data ? (
          <>
            {/* Gauge Meter */}
            <div className="relative">
              <div className="w-full h-6 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full bg-gradient-to-r ${getGaugeGradient(data.value)} transition-all duration-500`}
                  style={{ width: `${data.value}%` }}
                />
              </div>
              <div className="flex justify-between mt-1 text-xs text-gray-500">
                <span>0</span>
                <span className="font-semibold text-gray-700">{data.value}</span>
                <span>100</span>
              </div>
            </div>

            {/* Classification Badge */}
            <div className="flex items-center justify-center">
              <Badge
                variant="outline"
                className={`${getClassificationColor(data.value)} border-2 font-semibold text-sm px-4 py-1.5`}
              >
                {data.value >= 76 ? (
                  <TrendingUp className="w-3 h-3 mr-1" />
                ) : data.value <= 24 ? (
                  <TrendingDown className="w-3 h-3 mr-1" />
                ) : null}
                {data.value_classification}
              </Badge>
            </div>

            {/* Update Time */}
            {data.update_time && (
              <div className="text-xs text-center text-gray-500">
                Updated: {new Date(data.update_time).toLocaleString()}
              </div>
            )}
          </>
        ) : null}
      </CardContent>
    </Card>
  );
}

