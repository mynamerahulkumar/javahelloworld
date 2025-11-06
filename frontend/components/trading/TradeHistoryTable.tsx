"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TradeHistoryItem, TradeHistoryMeta } from "@/lib/types";
import { TrendingUp, TrendingDown, ChevronLeft, ChevronRight } from "lucide-react";

interface TradeHistoryTableProps {
  trades: TradeHistoryItem[];
  meta?: TradeHistoryMeta | null;
  isLoading?: boolean;
  onPageChange?: (after: string | null, direction: "next" | "prev") => void;
}

export default function TradeHistoryTable({
  trades,
  meta,
  isLoading,
  onPageChange,
}: TradeHistoryTableProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Trade History</CardTitle>
          <CardDescription>Loading trades...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (trades.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Trade History</CardTitle>
          <CardDescription>No trades found</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg font-medium">No trades found</p>
            <p className="text-sm mt-2">Your trade history will appear here</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(parseInt(timestamp) / 1000);
      return date.toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const formatNumber = (value: string | number | null | undefined) => {
    if (value === null || value === undefined) return "N/A";
    const num = typeof value === "string" ? parseFloat(value) : value;
    return isNaN(num) ? "N/A" : num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Trade History (Fills)</CardTitle>
        <CardDescription>
          {trades.length} trade(s) executed
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-3 font-semibold text-sm">Trade ID</th>
                <th className="text-left p-3 font-semibold text-sm">Order ID</th>
                <th className="text-left p-3 font-semibold text-sm">Symbol</th>
                <th className="text-left p-3 font-semibold text-sm">Side</th>
                <th className="text-right p-3 font-semibold text-sm">Price</th>
                <th className="text-right p-3 font-semibold text-sm">Size</th>
                <th className="text-right p-3 font-semibold text-sm">Commission</th>
                <th className="text-left p-3 font-semibold text-sm">Time</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade) => (
                <tr
                  key={trade.id}
                  className="border-b hover:bg-gray-50 transition-colors"
                >
                  <td className="p-3 font-mono text-sm">{trade.id}</td>
                  <td className="p-3 font-mono text-sm text-gray-600">{trade.order_id}</td>
                  <td className="p-3 font-semibold">{trade.product_symbol}</td>
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      {trade.side === "buy" ? (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      <Badge variant={trade.side === "buy" ? "default" : "destructive"}>
                        {trade.side.toUpperCase()}
                      </Badge>
                    </div>
                  </td>
                  <td className="text-right p-3 font-mono font-semibold">
                    {formatNumber(trade.price)}
                  </td>
                  <td className="text-right p-3 font-mono">{trade.size}</td>
                  <td className="text-right p-3 font-mono text-gray-600">
                    {formatNumber(trade.commission)}
                  </td>
                  <td className="p-3 text-sm text-gray-600">{formatDate(trade.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {meta && (meta.after || meta.before) && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange?.(meta.before || null, "prev")}
              disabled={!meta.before}
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange?.(meta.after || null, "next")}
              disabled={!meta.after}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}



