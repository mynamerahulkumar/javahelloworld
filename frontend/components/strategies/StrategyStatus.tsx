"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { StrategyStatus as StrategyStatusType } from "@/lib/types";
import { stopStrategy } from "@/lib/api/strategies";
import { toast } from "sonner";
import { useAuthStore } from "@/store/auth";
import {
  Play,
  Square,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Shield,
} from "lucide-react";
import { useState } from "react";

interface StrategyStatusProps {
  strategy: StrategyStatusType;
  onStop?: () => void;
}

export function StrategyStatus({ strategy, onStop }: StrategyStatusProps) {
  const { srpClientId, srpClientEmail } = useAuthStore();
  const [isStopping, setIsStopping] = useState(false);

  const getStatusBadge = () => {
    switch (strategy.status) {
      case "running":
        return (
          <Badge className="bg-green-500/10 text-green-700 border-green-500/20">
            <CheckCircle className="w-3 h-3 mr-1" />
            Running
          </Badge>
        );
      case "stopped":
        return (
          <Badge className="bg-gray-500/10 text-gray-700 border-gray-500/20">
            <Square className="w-3 h-3 mr-1" />
            Stopped
          </Badge>
        );
      case "error":
        return (
          <Badge className="bg-red-500/10 text-red-700 border-red-500/20">
            <AlertCircle className="w-3 h-3 mr-1" />
            Error
          </Badge>
        );
      default:
        return (
          <Badge className="bg-blue-500/10 text-blue-700 border-blue-500/20">
            <Clock className="w-3 h-3 mr-1" />
            {strategy.status}
          </Badge>
        );
    }
  };

  const handleStop = async () => {
    if (!srpClientId || !srpClientEmail) {
      toast.error("Please login first");
      return;
    }

    setIsStopping(true);
    try {
      const response = await stopStrategy(strategy.strategy_id, {
        srpClientId,
        srpClientEmail,
      });

      if (response.success) {
        toast.success(response.message);
        onStop?.();
      } else {
        toast.error(response.error || "Failed to stop strategy");
      }
    } catch (error: any) {
      toast.error(error.detail || "Failed to stop strategy");
    } finally {
      setIsStopping(false);
    }
  };

  const formatTime = (timestamp?: number) => {
    if (!timestamp) return "N/A";
    return new Date(timestamp * 1000).toLocaleString();
  };

  return (
    <Card className="hover:shadow-xl transition-all duration-300 border-2 hover:border-blue-300 bg-white">
      <CardHeader className="bg-gradient-to-r from-gray-50 to-blue-50/30 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm">
                {strategy.symbol?.substring(0, 2) || "N/A"}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-gray-900">
                    {strategy.symbol || "N/A"}
                  </span>
                  <span className="text-sm text-gray-500">•</span>
                  <span className="text-sm font-semibold text-gray-700">
                    {strategy.timeframe || "N/A"}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5 font-mono">
                  ID: {strategy.strategy_id.substring(0, 8)}...
                </p>
              </div>
              {getStatusBadge()}
            </CardTitle>
          </div>
          {strategy.status === "running" && (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleStop}
              disabled={isStopping}
              className="shadow-md hover:shadow-lg transition-all duration-200"
            >
              <Square className="w-4 h-4 mr-2" />
              {isStopping ? "Stopping..." : "Stop"}
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-5 pt-6">
        {/* Status Info */}
        <div className="grid grid-cols-2 gap-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div>
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Started</span>
            <p className="font-semibold text-gray-900 mt-1">{formatTime(strategy.start_time)}</p>
          </div>
          {strategy.stop_time && (
            <div>
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Stopped</span>
              <p className="font-semibold text-gray-900 mt-1">{formatTime(strategy.stop_time)}</p>
            </div>
          )}
        </div>

        {/* Breakout Levels */}
        {(strategy.prev_period_high || strategy.prev_period_low) && (
          <div className="space-y-3 p-4 bg-gradient-to-br from-blue-50/50 to-indigo-50/50 rounded-lg border border-blue-200">
            <h4 className="text-sm font-bold text-gray-800 flex items-center gap-2 uppercase tracking-wide">
              <Target className="w-4 h-4 text-blue-600" />
              Breakout Levels
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-white rounded-lg border border-green-200 shadow-sm">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-1">Previous High</span>
                <p className="font-bold text-lg text-green-600">
                  {strategy.prev_period_high?.toLocaleString() || "N/A"}
                </p>
              </div>
              <div className="p-3 bg-white rounded-lg border border-red-200 shadow-sm">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-1">Previous Low</span>
                <p className="font-bold text-lg text-red-600">
                  {strategy.prev_period_low?.toLocaleString() || "N/A"}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Active Position */}
        {strategy.active_position && (
          <div className="space-y-3 p-4 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-lg border-2 border-emerald-300 shadow-md">
            <h4 className="text-sm font-bold text-gray-800 flex items-center gap-2 uppercase tracking-wide">
              <DollarSign className="w-4 h-4 text-emerald-600" />
              Active Position
            </h4>
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 bg-white rounded-lg border border-gray-200 shadow-sm">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-1">Side</span>
                <p
                  className={`font-bold text-lg ${
                    strategy.active_position.side === "long"
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  {strategy.active_position.side?.toUpperCase() || "N/A"}
                </p>
              </div>
              <div className="p-3 bg-white rounded-lg border border-gray-200 shadow-sm">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-1">Size</span>
                <p className="font-bold text-lg text-gray-900">
                  {strategy.active_position.size || "N/A"}
                </p>
              </div>
              <div className="p-3 bg-white rounded-lg border border-gray-200 shadow-sm">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-1">Entry Price</span>
                <p className="font-bold text-lg text-gray-900">
                  {strategy.active_position.entry_price?.toLocaleString() ||
                    "N/A"}
                </p>
              </div>
            </div>
            {strategy.breakeven_applied && (
              <Badge className="mt-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white border-0 shadow-md">
                <Shield className="w-3 h-3 mr-1" />
                Breakeven Applied
              </Badge>
            )}
          </div>
        )}

        {/* Orders */}
        {(strategy.buy_order_id ||
          strategy.sell_order_id ||
          strategy.stop_loss_order_id ||
          strategy.take_profit_order_id) && (
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-gray-800 uppercase tracking-wide">Active Orders</h4>
            <div className="grid grid-cols-2 gap-3">
              {strategy.buy_order_id && (
                <div className="p-3 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border-2 border-green-300 shadow-sm">
                  <span className="text-xs font-medium text-gray-600 uppercase tracking-wide block mb-1">Buy Order</span>
                  <p className="font-bold text-sm text-green-700 font-mono">#{strategy.buy_order_id}</p>
                </div>
              )}
              {strategy.sell_order_id && (
                <div className="p-3 bg-gradient-to-br from-red-50 to-rose-50 rounded-lg border-2 border-red-300 shadow-sm">
                  <span className="text-xs font-medium text-gray-600 uppercase tracking-wide block mb-1">Sell Order</span>
                  <p className="font-bold text-sm text-red-700 font-mono">#{strategy.sell_order_id}</p>
                </div>
              )}
              {strategy.stop_loss_order_id && (
                <div className="p-3 bg-gradient-to-br from-orange-50 to-amber-50 rounded-lg border-2 border-orange-300 shadow-sm">
                  <span className="text-xs font-medium text-gray-600 uppercase tracking-wide block mb-1">Stop Loss</span>
                  <p className="font-bold text-sm text-orange-700 font-mono">#{strategy.stop_loss_order_id}</p>
                </div>
              )}
              {strategy.take_profit_order_id && (
                <div className="p-3 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-300 shadow-sm">
                  <span className="text-xs font-medium text-gray-600 uppercase tracking-wide block mb-1">Take Profit</span>
                  <p className="font-bold text-sm text-blue-700 font-mono">#{strategy.take_profit_order_id}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Error Message */}
        {strategy.error_message && (
          <div className="p-4 bg-gradient-to-br from-red-50 to-rose-50 rounded-lg border-2 border-red-300 shadow-md">
            <p className="text-sm font-medium text-red-800 flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <span>{strategy.error_message}</span>
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

