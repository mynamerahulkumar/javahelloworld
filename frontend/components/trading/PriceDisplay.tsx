"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown } from "lucide-react";

interface PriceDisplayProps {
  symbol: string;
  price: number;
  change24h?: number;
  changePercent24h?: number;
}

export function PriceDisplay({ symbol, price, change24h, changePercent24h }: PriceDisplayProps) {
  const isPositive = (changePercent24h || 0) >= 0;
  const changeColor = isPositive ? "text-green-500" : "text-red-500";
  const changeBgColor = isPositive ? "bg-green-500/10" : "bg-red-500/10";

  return (
    <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-gray-600">
          {symbol} Price
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-end justify-between">
          <div>
            <div className="text-4xl font-bold text-gray-900 mb-2">
              ${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            {change24h !== undefined && (
              <div className="flex items-center gap-2">
                {isPositive ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-sm font-semibold ${changeColor}`}>
                  {change24h >= 0 ? "+" : ""}${change24h.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                {changePercent24h !== undefined && (
                  <Badge className={`${changeBgColor} ${changeColor} border-0`}>
                    {changePercent24h >= 0 ? "+" : ""}{changePercent24h.toFixed(2)}%
                  </Badge>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

