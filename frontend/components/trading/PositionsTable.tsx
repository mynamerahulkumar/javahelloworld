"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Position } from "@/lib/types";
import { TrendingUp, TrendingDown } from "lucide-react";

interface PositionsTableProps {
  positions: Position[];
  isLoading?: boolean;
}

export default function PositionsTable({ positions, isLoading }: PositionsTableProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Positions</CardTitle>
          <CardDescription>Loading positions...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (positions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Positions</CardTitle>
          <CardDescription>No open positions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg font-medium">No positions found</p>
            <p className="text-sm mt-2">Your open positions will appear here</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const formatNumber = (value: string | number | null | undefined) => {
    if (value === null || value === undefined) return "N/A";
    const num = typeof value === "string" ? parseFloat(value) : value;
    return isNaN(num) ? "N/A" : num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Current Positions</CardTitle>
        <CardDescription>Your margined positions ({positions.length})</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-3 font-semibold text-sm">Symbol</th>
                <th className="text-right p-3 font-semibold text-sm">Size</th>
                <th className="text-right p-3 font-semibold text-sm">Entry Price</th>
                <th className="text-right p-3 font-semibold text-sm">Margin</th>
                <th className="text-right p-3 font-semibold text-sm">Liquidation</th>
                <th className="text-right p-3 font-semibold text-sm">Realized P&L</th>
                <th className="text-right p-3 font-semibold text-sm">Commission</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((position, index) => {
                const size = parseFloat(position.size.toString());
                const realizedPnL = position.realized_pnl ? parseFloat(position.realized_pnl) : 0;
                const isLong = size > 0;

                return (
                  <tr
                    key={`${position.product_id}-${index}`}
                    className={`border-b hover:bg-gray-50 transition-colors ${
                      realizedPnL > 0 ? "bg-green-50/30" : realizedPnL < 0 ? "bg-red-50/30" : ""
                    }`}
                  >
                    <td className="p-3">
                      <div className="flex items-center gap-2">
                        {isLong ? (
                          <TrendingUp className="w-4 h-4 text-green-500" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-red-500" />
                        )}
                        <span className="font-semibold">{position.product_symbol}</span>
                        <Badge variant={isLong ? "default" : "destructive"}>
                          {isLong ? "LONG" : "SHORT"}
                        </Badge>
                      </div>
                    </td>
                    <td className="text-right p-3 font-mono">
                      {formatNumber(Math.abs(size))}
                    </td>
                    <td className="text-right p-3 font-mono">
                      {formatNumber(position.entry_price)}
                    </td>
                    <td className="text-right p-3 font-mono">
                      {formatNumber(position.margin)}
                    </td>
                    <td className="text-right p-3 font-mono text-red-600">
                      {formatNumber(position.liquidation_price)}
                    </td>
                    <td className={`text-right p-3 font-mono font-semibold ${
                      realizedPnL > 0 ? "text-green-600" : realizedPnL < 0 ? "text-red-600" : "text-gray-600"
                    }`}>
                      {formatPnL(realizedPnL)}
                    </td>
                    <td className="text-right p-3 font-mono text-gray-600">
                      {formatNumber(position.commission)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function formatPnL(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}`;
}



