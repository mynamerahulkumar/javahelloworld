"use client";

import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown, DollarSign } from "lucide-react";
import { PnLSummaryResponse } from "@/lib/types";

interface PnLDisplayProps {
  pnl: PnLSummaryResponse | null;
  isLoading?: boolean;
}

export default function PnLDisplay({ pnl, isLoading }: PnLDisplayProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-20 bg-gray-200 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!pnl) {
    return null;
  }

  const totalPnL = pnl.total_pnl || 0;
  const realizedPnL = pnl.total_realized_pnl || 0;
  const unrealizedPnL = pnl.total_unrealized_pnl || 0;

  const formatPnL = (value: number) => {
    const formatted = Math.abs(value).toFixed(2);
    return value >= 0 ? `+$${formatted}` : `-$${formatted}`;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <Card className={`border-2 ${totalPnL >= 0 ? 'border-green-500 bg-gradient-to-br from-green-50 to-emerald-50' : 'border-red-500 bg-gradient-to-br from-red-50 to-rose-50'}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Total P&L</p>
              <p className={`text-3xl font-bold ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPnL(totalPnL)}
              </p>
            </div>
            {totalPnL >= 0 ? (
              <TrendingUp className="w-12 h-12 text-green-500" />
            ) : (
              <TrendingDown className="w-12 h-12 text-red-500" />
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="border-2 border-blue-500 bg-gradient-to-br from-blue-50 to-cyan-50">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Realized P&L</p>
              <p className={`text-3xl font-bold ${realizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPnL(realizedPnL)}
              </p>
            </div>
            <DollarSign className="w-12 h-12 text-blue-500" />
          </div>
        </CardContent>
      </Card>

      <Card className="border-2 border-purple-500 bg-gradient-to-br from-purple-50 to-pink-50">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Unrealized P&L</p>
              <p className={`text-3xl font-bold ${unrealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPnL(unrealizedPnL)}
              </p>
              <p className="text-xs text-gray-500 mt-1">{pnl.position_count} position(s)</p>
            </div>
            <TrendingUp className="w-12 h-12 text-purple-500" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}






